#!/bin/bash
# Test MCP Server functionality

echo "Testing ClaudeScale MCP Server"
echo "=================================="
echo ""

# Check if running in project directory
if [ ! -f "mcp-server/server.py" ]; then
    echo "Error: Must run from project root directory"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate 2>/dev/null || {
    echo "Warning: Could not activate venv, continuing anyway..."
}

# Check Python dependencies
echo "Checking dependencies..."
python3 -c "import fastmcp, kubernetes, prometheus_api_client" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Missing dependencies. Installing..."
    pip install -r requirements-mcp.txt
fi
echo "Dependencies OK"
echo ""

# Check Kubernetes connection
echo "Testing Kubernetes connection..."
kubectl get nodes > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Cannot connect to Kubernetes cluster"
    echo "Make sure Minikube is running: minikube start"
    exit 1
fi
echo "Kubernetes connection OK"
echo ""

# Check namespace
echo "Checking claudescale namespace..."
kubectl get namespace claudescale > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Namespace 'claudescale' not found"
    exit 1
fi
echo "Namespace OK"
echo ""

# Check demo-app deployment
echo "Checking demo-app deployment..."
kubectl get deployment demo-app -n claudescale > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Deployment 'demo-app' not found"
    exit 1
fi
echo "Deployment OK"
echo ""

# Show current state
echo "Current State:"
kubectl get pods -n claudescale -l app=demo-app
echo ""
kubectl get hpa -n claudescale demo-app-hpa 2>/dev/null
echo ""

# Test Python imports
echo "Testing Python imports..."
python3 << PYEOF
import sys
sys.path.insert(0, 'mcp-server')

try:
    from config import settings
    from utils.kubernetes_client import KubernetesClient
    from utils.prometheus_client import PrometheusClient
    from tools.scaling_tools import get_current_state, get_metrics, scale_deployment
    print("All imports successful")
except Exception as e:
    print(f"Import error: {e}")
    sys.exit(1)
PYEOF

if [ $? -ne 0 ]; then
    exit 1
fi
echo ""

# Test Kubernetes client
echo "Testing Kubernetes client..."
python3 << PYEOF
import sys
sys.path.insert(0, 'mcp-server')

from utils.kubernetes_client import KubernetesClient

try:
    k8s = KubernetesClient(namespace="claudescale", in_cluster=False)
    deployments = k8s.list_deployments()
    print(f"Found {len(deployments)} deployment(s)")
    for dep in deployments:
        print(f"  - {dep['name']}: {dep['ready_replicas']}/{dep['replicas']} ready")
except Exception as e:
    print(f"Kubernetes client error: {e}")
    sys.exit(1)
PYEOF

if [ $? -ne 0 ]; then
    exit 1
fi
echo ""

# Test Prometheus if port-forward is up
echo "Testing Prometheus connection..."
curl -s http://localhost:9090/api/v1/query?query=up > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "Prometheus connection OK"
else
    echo "Prometheus not reachable — start port-forward if needed:"
    echo "  kubectl port-forward -n claudescale svc/prometheus 9090:9090"
fi
echo ""

echo "=========================================="
echo "ALL TESTS PASSED"
echo "=========================================="
echo ""
echo "MCP Server is ready to run."
echo ""
echo "To start the server:"
echo "  cd mcp-server && python3 server.py"
echo ""
