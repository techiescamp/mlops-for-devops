## Commands to deploy helm chart

### Deploy vector store

helm install vector-store vector-store -n rag-storage --create-namespace

### Deploy sync-backend

helm install sync-backend sync-backend -n rag-backend --create-namespace

### Manually trigger sync backend cronjob

kubectl create job --from=cronjob/rag-sync-backend -n rag-backend sync-backend

### Deploy main backend

helm install main-backend main-backend -n rag-backend

### Deploy frontend

helm install frontend frontend -n rag-frontend --create-namespace

## Commands to delete helm chart

### Delete frontend

helm delete frontend -n rag-frontend

### Delete main backend

helm delete main-backend -n rag-backend

### Delete sync backend

helm delete sync-backend -n rag-backend

### Delete vector store

helm delete vector-store -n rag-storage

### Delete PVC attached to vector store
kubectl delete pvc <pvc-name> -n rag-storage
