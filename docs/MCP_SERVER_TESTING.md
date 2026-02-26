# MCP Server Testing Guide

## Prerequisites

Before testing the MCP server, ensure:

1. Minikube is running: `minikube status`
2. Namespace exists: `kubectl get ns claudescale`
3. demo-app is deployed: `kubectl get deployment demo-app -n claudescale`
4. Prometheus port-forward running (for metrics tests)

## Quick Test

Run the automated test script from the project root:
```bash
./scripts/test-mcp-server.sh
```

This verifies:
- Python dependencies
- Kubernetes connection
- Namespace and deployment
- Python imports
- Kubernetes client

## Manual Testing

### Setup

Start Prometheus port-forward in a separate terminal:
```bash
kubectl port-forward -n claudescale svc/prometheus 9090:9090
```

Run all tool tests:
```bash
python3 scripts/manual-test-tools.py
```

Skip scaling test (read-only):
```bash
python3 scripts/manual-test-tools.py --no-scale
```

### Individual Tool Testing

#### Tool 1: get_current_state
```python
import sys, asyncio
sys.path.insert(0, 'mcp-server')
from utils.kubernetes_client import KubernetesClient
from tools.scaling_tools import get_current_state

k8s = KubernetesClient(namespace="claudescale", in_cluster=False)
result = asyncio.run(get_current_state(k8s))
print(result)
```

Expected output:
```json
{
  "namespace": "claudescale",
  "total_deployments": 3,
  "total_pods": 4,
  "total_ready_pods": 4,
  "deployments": [
    {"name": "demo-app", "replicas": 2, "ready_replicas": 2},
    {"name": "prometheus", "replicas": 1, "ready_replicas": 1},
    {"name": "grafana", "replicas": 1, "ready_replicas": 1}
  ]
}
```

#### Tool 2: get_metrics
```python
import sys, asyncio
sys.path.insert(0, 'mcp-server')
from utils.prometheus_client import PrometheusClient
from tools.scaling_tools import get_metrics

prom = PrometheusClient(url="http://localhost:9090")
result = asyncio.run(get_metrics(prom, namespace="claudescale", deployment="demo-app"))
print(result)
```

#### Tool 3: scale_deployment
```python
import sys, asyncio
sys.path.insert(0, 'mcp-server')
from utils.kubernetes_client import KubernetesClient
from tools.scaling_tools import scale_deployment

k8s = KubernetesClient(namespace="claudescale", in_cluster=False)
result = asyncio.run(scale_deployment(k8s, deployment="demo-app", replicas=3, reason="test"))
print(result)
```

Expected output:
```json
{
  "success": true,
  "action": "scaled_up",
  "previous_replicas": 2,
  "new_replicas": 3,
  "reason": "test"
}
```

## Running the Full MCP Server

```bash
cd /home/kratosvil/Desarrollo/ClaudeScale
source venv/bin/activate
cd mcp-server && python3 server.py
```

Expected output:
```
Starting claudescale-mcp v1.0.0
Namespace: claudescale
Prometheus: http://localhost:9090

Tools:
  1. claudescale_get_current_state
  2. claudescale_get_metrics
  3. claudescale_scale_deployment
  4. claudescale_generate_report
```

## Troubleshooting

**Cannot connect to Kubernetes:**
```bash
minikube status
minikube start --driver=docker --memory=4096 --cpus=2
```

**Connection refused to Prometheus:**
```bash
kubectl port-forward -n claudescale svc/prometheus 9090:9090
```

**Module not found:**
```bash
source venv/bin/activate
pip install -r requirements-mcp.txt
```

**Deployment not found:**
```bash
kubectl apply -f k8s-manifests/demo-app.yaml
```

## Next Steps

After successful testing:
- Phase 6 complete
- Continue to Phase 7: Claude Desktop Integration
- Configure claude_desktop_config.json
- Test with real Claude AI
