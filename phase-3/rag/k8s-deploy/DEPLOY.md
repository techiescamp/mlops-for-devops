# RAG on EKS — Full Deployment Guide

## Architecture

```
User
 │
 ▼
rag-ui (NodePort :30500)          [rag-frontend namespace]
 │
 ▼
rag-backend-service (:8000)       [rag-backend namespace]
 │
 ▼
vector-store-service (:8001)      [rag-vector-store namespace]
 │
 ▼
AWS S3 Vectors ◄──► AWS Bedrock
```

## Services

| Service | Namespace | Port | Kind |
|---|---|---|---|
| Frontend (React + Express) | rag-frontend | 3000 | NodePort 30500 |
| Main Backend (FastAPI) | rag-backend | 8000 | ClusterIP |
| Vector Store (FastAPI) | rag-vector-store | 8001 | ClusterIP |
| Sync Backend | rag-backend | — | CronJob (daily 00:00 IST) |

## Docker Images

| Service | Image |
|---|---|
| Frontend | catninjauser/ragfrontend:1.0.1 |
| Main Backend | catninjauser/ragmain:1.0.0 |
| Vector Store | catninjauser/regpvector:1.0.1 |
| Sync Backend | catninjauser/ragsync:1.0.0 |

---

## Step 1 — Build & Push Docker Images

```bash
cd phase-3/RAG/k8s-deploy

docker buildx build --platform linux/amd64,linux/arm64 \
  -t catninjauser/ragfrontend:1.0.1 --push frontend/

docker buildx build --platform linux/amd64,linux/arm64 \
  -t catninjauser/ragmain:1.0.0 --push backend/main-backend/

docker buildx build --platform linux/amd64,linux/arm64 \
  -t catninjauser/regpvector:1.0.1 --push backend/vector-store/

docker buildx build --platform linux/amd64,linux/arm64 \
  -t catninjauser/ragsync:1.0.0 --push backend/sync-backend/
```

---

## Step 2 — AWS S3 Vectors Setup

```bash
# Create vector bucket
aws s3vectors create-vector-bucket \
  --vector-bucket-name vector-bucket-demo \
  --region us-west-2

# Create index (1536 dims, Titan Embed v2, cosine distance)
aws s3vectors create-index \
  --vector-bucket-name vector-bucket-demo \
  --index-name vector-bucket-index \
  --data-type float32 \
  --dimension 1536 \
  --distance-metric cosine \
  --region us-west-2
```

---

## Step 3 — IAM Role for Pod Identity

```bash
# Trust policy
cat > trust-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": { "Service": "pods.eks.amazonaws.com" },
    "Action": ["sts:AssumeRole", "sts:TagSession"]
  }]
}
EOF

# Create role
aws iam create-role \
  --role-name rag-eks-pod-role \
  --assume-role-policy-document file://trust-policy.json

# Bedrock access
aws iam attach-role-policy \
  --role-name rag-eks-pod-role \
  --policy-arn arn:aws:iam::aws:policy/AmazonBedrockFullAccess

# S3 Vectors access
cat > s3vectors-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "s3vectors:PutVectors",
      "s3vectors:QueryVectors",
      "s3vectors:GetVectors",
      "s3vectors:DeleteVectors"
    ],
    "Resource": "*"
  }]
}
EOF

aws iam put-role-policy \
  --role-name rag-eks-pod-role \
  --policy-name s3vectors-access \
  --policy-document file://s3vectors-policy.json
```

---

## Step 4 — EKS Pod Identity Associations

```bash
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/rag-eks-pod-role"

# rag-backend namespace (main-backend + sync-backend)
aws eks create-pod-identity-association \
  --cluster-name eks-spot-cluster \
  --namespace rag-backend \
  --service-account rag-service-account \
  --role-arn $ROLE_ARN \
  --region us-west-2

# rag-vector-store namespace
aws eks create-pod-identity-association \
  --cluster-name eks-spot-cluster \
  --namespace rag-vector-store \
  --service-account rag-service-account \
  --role-arn $ROLE_ARN \
  --region us-west-2

# verify
aws eks list-pod-identity-associations \
  --cluster-name eks-spot-cluster \
  --region us-west-2
```

---

## Step 5 — Configure Manifests

Fill real values in these files before applying:

**manifest/vector-store/configmap.yaml**
```yaml
AWS_REGION: "us-west-2"
AWS_ACCOUNT_ID: "<your-account-id>"
S3_VECTOR_BUCKET_NAME: "vector-bucket-demo"
S3_VECTOR_INDEX_NAME: "vector-bucket-index"
BEDROCK_EMBEDDING_MODEL_ID: "amazon.titan-embed-text-v2:0"
```

**manifest/main-backend/configmap.yaml**
```yaml
AWS_REGION: "us-west-2"
BEDROCK_LLM_MODEL: "us.amazon.nova-micro-v1:0"
```

---

## Step 6 — Deploy to EKS

```bash
cd manifest/

kubectl apply -f namespace.yaml       # create namespaces first
kubectl apply -f serviceaccount.yaml  # service accounts
kubectl apply -f vector-store/        # vector-store (others depend on it)
kubectl apply -f main-backend/        # main backend
kubectl apply -f sync-backend/        # sync cronjob
kubectl apply -f frontend/            # frontend last
```

---

## Step 7 — Verify

```bash
kubectl get pods -n rag-frontend
kubectl get pods -n rag-backend
kubectl get pods -n rag-vector-store
```

All pods must show `1/1 Running`.

---

## Step 8 — Access the App

```bash
# get node external IPs
kubectl get nodes -o wide
```

Open in browser:
```
http://<any-node-external-ip>:30500
```

---

## Manifest Structure

```
manifest/
├── namespace.yaml              # rag-frontend, rag-backend, rag-vector-store
├── serviceaccount.yaml         # rag-service-account (rag-backend + rag-vector-store)
├── frontend/
│   ├── deploy.yaml
│   └── service.yaml            # NodePort 30500
├── main-backend/
│   ├── configmap.yaml
│   ├── deploy.yaml
│   └── service.yaml            # ClusterIP 8000
├── vector-store/
│   ├── configmap.yaml
│   ├── deploy.yaml
│   └── service.yaml            # ClusterIP 8001
└── sync-backend/
    ├── configmap.yaml
    └── deploy.yaml             # CronJob daily 00:00 IST
```

---

## Cross-Namespace DNS

| From | To | URL |
|---|---|---|
| frontend | main-backend | `http://rag-backend-service.rag-backend.svc.cluster.local:8000` |
| main-backend | vector-store | `http://vector-store-service.rag-vector-store.svc.cluster.local:8001` |
| sync-backend | vector-store | `http://vector-store-service.rag-vector-store.svc.cluster.local:8001` |

---

## Step 9 — Initial Data Sync

CronJob runs daily at 00:00 IST automatically. For first-time setup, trigger manually:

```bash
kubectl create job sync-now \
  --from=cronjob/sync-backend \
  -n rag-backend
```

Watch progress:
```bash
kubectl logs -l job-name=sync-now -n rag-backend -f
```

Wait for `Completed`:
```bash
kubectl get pods -n rag-backend
```

Expected output when done:
```
✅ Successfully stored batch 36
✅ Completed processing with 36 successful batches
✅ Total documents processed: 1766
✅ Successfully stored embeddings...
```

After sync completes, S3 Vectors contains 1766 Kubernetes docs chunks. All queries now use real RAG context.

---

## Rebuild & Redeploy

```bash
# rebuild image
docker buildx build --platform linux/amd64,linux/arm64 \
  -t catninjauser/<image>:<new-tag> --push <service-dir>/

# update deployment
kubectl set image deployment/<name> \
  <container>=catninjauser/<image>:<new-tag> -n <namespace>

# watch rollout
kubectl rollout status deployment/<name> -n <namespace>
```
