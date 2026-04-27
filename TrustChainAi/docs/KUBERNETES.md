# Local Kubernetes Deployment Guide

This guide explains how to set up and run TrustChainAi on a local Kubernetes cluster using `kind` (Kubernetes in Docker) or `minikube`.

## Prerequisites

```bash
# Install Docker
https://docs.docker.com/get-docker/

# Install kind (recommended for simplicity)
https://kind.sigs.k8s.io/docs/user/quick-start/

# OR install minikube
https://minikube.sigs.k8s.io/docs/start/

# Install kubectl
https://kubernetes.io/docs/tasks/tools/

# Verify installation
kind version
kubectl version --client
```

## Quick Start with Kind

### 1. Create a Local Cluster

```bash
# Create cluster with image pre-loading support
kind create cluster --name trustchainai --config - <<EOF
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
  extraPortMappings:
  - containerPort: 8501  # Streamlit dashboard
    hostPort: 8501
    protocol: TCP
EOF

# Verify cluster
kubectl cluster-info
kubectl get nodes
```

### 2. Build & Load Docker Image

```bash
# Build image
docker build -t trustchainai:latest .

# Load into kind cluster
kind load docker-image trustchainai:latest --name trustchainai

# Verify image is available
kubectl images
```

### 3. Create Namespace & Deploy

```bash
# Create namespace
kubectl create namespace trustchainai

# Deploy manifests
kubectl apply -f kubernetes/ -n trustchainai

# Check rollout status
kubectl rollout status deployment/trustchainai-dashboard -n trustchainai

# View pods
kubectl get pods -n trustchainai
```

### 4. Access Dashboard

```bash
# Port-forward to local machine
kubectl port-forward -n trustchainai svc/trustchainai-dashboard 8501:80

# Open browser
open http://localhost:8501
```

## Troubleshooting

### Image not found
```bash
# Re-load image into cluster
kind load docker-image trustchainai:latest --name trustchainai

# Verify
kubectl describe pod <pod-name> -n trustchainai
```

### Pod stuck in CrashLoopBackOff
```bash
# Check logs
kubectl logs <pod-name> -n trustchainai

# Inspect pod for errors
kubectl describe pod <pod-name> -n trustchainai
```

### RPC connectivity issues
```bash
# Verify ConfigMap has correct endpoint
kubectl get configmap trustchainai-config -n trustchainai -o yaml

# Update if needed
kubectl set env deployment/trustchainai-dashboard \
  WEB3_RPC_ENDPOINT="https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY" \
  -n trustchainai
```

## Cleanup

```bash
# Delete deployment
kubectl delete namespace trustchainai

# Delete cluster
kind delete cluster --name trustchainai
```

## Portfolio Notes

This local K8s setup demonstrates:
- ✅ **Containerization**: Docker multi-stage builds
- ✅ **Orchestration**: Kubernetes deployment, services, ConfigMaps
- ✅ **Scaling Ready**: Manifests can easily scale to AWS/GCP
- ✅ **Production Patterns**: StatefulSets, CronJobs, PersistentVolumes

**Mention in interviews:** *"Deployed TrustChainAi on local Kubernetes (kind) to simulate production environment, including configuration management with ConfigMaps and persistent storage via PersistentVolumes. Architecture is cloud-provider agnostic and easily scales to AWS/GCP."*

## Cloud Deployment (Future)

The current manifests use `gcePersistentDisk` as placeholder. For cloud deployment:

### AWS EKS
```bash
# Use EBS for PersistentVolume
# Update volumes in kubernetes/deployment.yaml:
# - storageClassName: gp2
```

### Google Cloud GKE
```bash
# Use Google Persistent Disks (already configured)
gcloud container clusters create trustchainai \
  --zone us-central1-a --num-nodes 2
kubectl apply -f kubernetes/
```

---

**Next:** See [../docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md) for deployment architecture overview.
