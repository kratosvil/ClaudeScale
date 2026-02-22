# ClaudeScale Setup Guide

## Prerequisites Installed ✅

- Minikube (Kubernetes local cluster)
- kubectl (Kubernetes CLI)
- Python 3.11+
- Docker

## Kubernetes Cluster

### Starting the Cluster
```bash
minikube start --driver=docker --memory=4096 --cpus=2
```

**Why these settings?**
- `--driver=docker`: Uses Docker as the container runtime
- `--memory=4096`: Allocates 4GB RAM (enough for our stack)
- `--cpus=2`: Uses 2 CPU cores

### Verify Cluster
```bash
# Check node status
kubectl get nodes

# Check current context
kubectl config current-context
# Should show: minikube

# Check cluster info
kubectl cluster-info
```

### Stopping the Cluster
```bash
# When you're done for the day
minikube stop

# To completely delete the cluster (if needed)
minikube delete
```

## Next Steps

Continue with namespace creation (Task 7).
