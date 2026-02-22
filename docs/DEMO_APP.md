# Demo Application

## What is it?

A simple nginx web server running in Kubernetes.

## Why nginx?

- Lightweight: Uses minimal resources (perfect for local testing)
- Fast to start: Pods ready in seconds
- Stable: Rarely crashes or has bugs
- Well-known: Everyone understands what nginx does
- Easy to generate load: Just send HTTP requests

## Configuration

- **Image:** `nginx:alpine` (smallest nginx variant ~5MB)
- **Initial replicas:** 2
- **CPU request:** 100m (0.1 cores)
- **CPU limit:** 200m (0.2 cores)
- **Memory request:** 128Mi
- **Memory limit:** 256Mi

## Why these resource limits?

Small limits make it easier to trigger scaling:
- Lower limits = CPU/Memory fills up faster
- Faster fill-up = Claude will see high usage sooner
- Easier to demo scaling without heavy load generation

In production, you'd set limits based on actual app needs.

## What metrics will we monitor?

1. **CPU usage:** `container_cpu_usage_seconds_total`
2. **Memory usage:** `container_memory_usage_bytes`
3. **Network traffic:** `container_network_*_bytes_total`
4. **Pod count:** Count of running pods
5. **Pod restarts:** Times pod has crashed

## Service

- **Type:** ClusterIP (internal only)
- **Port:** 80
- **Accessible at:** `http://demo-app:80` (inside cluster)

## How to access from outside cluster
```bash
kubectl port-forward -n claudescale svc/demo-app 8080:80
# Then: http://localhost:8080
```
