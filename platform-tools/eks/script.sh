#!/bin/bash

set -e

ACTION=$1  # create | delete

# -------- Config --------
CLUSTER_NAME="mlops-spot-cluster"
AWS_REGION="us-west-2"
NAMESPACE="airflow"
SERVICE_ACCOUNT="airflow-dvc-sa"
ROLE_NAME="Airflow-DVC-S3-Role"
POLICY_NAME="Airflow-DVC-S3-Policy"
DVC_BUCKET="dcube-attrition-data"

export AWS_PAGER=""

AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
POLICY_ARN="arn:aws:iam::${AWS_ACCOUNT_ID}:policy/${POLICY_NAME}"
ROLE_ARN="arn:aws:iam::${AWS_ACCOUNT_ID}:role/${ROLE_NAME}"

# -------- CREATE --------
create_resources() {
  echo "Creating IAM Policy..."

  aws iam create-policy \
    --policy-name "$POLICY_NAME" \
    --policy-document "{
      \"Version\": \"2012-10-17\",
      \"Statement\": [
        {
          \"Effect\": \"Allow\",
          \"Action\": [
            \"s3:GetObject\",
            \"s3:PutObject\",
            \"s3:DeleteObject\",
            \"s3:ListBucket\"
          ],
          \"Resource\": [
            \"arn:aws:s3:::${DVC_BUCKET}\",
            \"arn:aws:s3:::${DVC_BUCKET}/*\"
          ]
        }
      ]
    }" || echo "Policy already exists"

  echo "Creating IAM Role..."

  aws iam create-role \
    --role-name "$ROLE_NAME" \
    --assume-role-policy-document '{
      "Version": "2012-10-17",
      "Statement": [
        {
          "Effect": "Allow",
          "Principal": {
            "Service": "pods.eks.amazonaws.com"
          },
          "Action": [
            "sts:AssumeRole",
            "sts:TagSession"
          ]
        }
      ]
    }' || echo "Role already exists"

  echo "Attaching policy..."
  aws iam attach-role-policy \
    --role-name "$ROLE_NAME" \
    --policy-arn "$POLICY_ARN"

  echo "Creating namespace + service account..."
  kubectl create namespace "$NAMESPACE" || true
  kubectl create serviceaccount "$SERVICE_ACCOUNT" -n "$NAMESPACE" || true

  echo "Creating Pod Identity Association..."
  aws eks create-pod-identity-association \
    --cluster-name "$CLUSTER_NAME" \
    --namespace "$NAMESPACE" \
    --service-account "$SERVICE_ACCOUNT" \
    --role-arn "$ROLE_ARN" \
    --region "$AWS_REGION" || echo "Association already exists"

  echo "Create completed."
}

# -------- DELETE --------
delete_resources() {
  echo "Deleting Pod Identity Association..."

  ASSOCIATION_ID=$(aws eks list-pod-identity-associations \
    --cluster-name "$CLUSTER_NAME" \
    --region "$AWS_REGION" \
    --query "associations[?namespace=='$NAMESPACE' && serviceAccount=='$SERVICE_ACCOUNT'].associationId" \
    --output text 2>/dev/null || true)

  if [[ -n "$ASSOCIATION_ID" ]]; then
    aws eks delete-pod-identity-association \
      --cluster-name "$CLUSTER_NAME" \
      --association-id "$ASSOCIATION_ID" \
      --region "$AWS_REGION"
  else
    echo "No association found"
  fi

  echo "Detaching IAM policy..."
  aws iam detach-role-policy \
    --role-name "$ROLE_NAME" \
    --policy-arn "$POLICY_ARN" || true

  echo "Deleting IAM role..."
  aws iam delete-role \
    --role-name "$ROLE_NAME" || true

  echo "Deleting non-default policy versions..."
  VERSION_IDS=$(aws iam list-policy-versions \
    --policy-arn "$POLICY_ARN" \
    --query 'Versions[?IsDefaultVersion==`false`].VersionId' \
    --output text 2>/dev/null || true)

  for v in $VERSION_IDS; do
    aws iam delete-policy-version \
      --policy-arn "$POLICY_ARN" \
      --version-id "$v"
  done

  echo "Deleting IAM policy..."
  aws iam delete-policy \
    --policy-arn "$POLICY_ARN" || true

  echo "Deleting Kubernetes resources..."
  kubectl delete serviceaccount "$SERVICE_ACCOUNT" -n "$NAMESPACE" || true
  kubectl delete namespace "$NAMESPACE" || true

  echo "Delete completed."
}

# -------- MAIN --------
if [[ "$ACTION" == "create" ]]; then
  create_resources
elif [[ "$ACTION" == "delete" ]]; then
  delete_resources
else
  echo "Usage: $0 {create|delete}"
  exit 1
fi