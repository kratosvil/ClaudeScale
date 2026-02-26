#!/bin/bash
# Start all ClaudeScale services and port-forwards

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
NAMESPACE="claudescale"

echo "ClaudeScale — Starting services"
echo "================================"
echo ""

# 1. Verify minikube
echo "Checking minikube..."
if ! minikube status | grep -q "Running"; then
    echo "Minikube not running. Starting..."
    minikube start --driver=docker --memory=4096 --cpus=2
fi
echo "  Minikube: OK"

# 2. Set namespace
kubectl config set-context --current --namespace="$NAMESPACE" > /dev/null
echo "  Namespace: $NAMESPACE"

# 3. Verify pods
READY=$(kubectl get pods -n "$NAMESPACE" --no-headers 2>/dev/null | grep -c "Running" || true)
echo "  Pods running: $READY"
echo ""

# 4. Kill existing port-forwards
pkill -f "kubectl port-forward" 2>/dev/null || true
sleep 1

# 5. Start port-forwards in background
echo "Starting port-forwards..."

kubectl port-forward -n "$NAMESPACE" svc/prometheus 9090:9090 \
    > /tmp/pf-prometheus.log 2>&1 &
echo "  Prometheus → http://localhost:9090 (PID $!)"

kubectl port-forward -n "$NAMESPACE" svc/grafana 3000:3000 \
    > /tmp/pf-grafana.log 2>&1 &
echo "  Grafana    → http://localhost:3000 (PID $!)"

kubectl port-forward -n "$NAMESPACE" svc/demo-app 8080:80 \
    > /tmp/pf-demo-app.log 2>&1 &
echo "  Demo App   → http://localhost:8080 (PID $!)"

sleep 2

# 6. Verify port-forwards
echo ""
echo "Verifying connections..."
curl -s http://localhost:9090/-/healthy > /dev/null && echo "  Prometheus: OK" || echo "  Prometheus: FAILED (check /tmp/pf-prometheus.log)"
curl -s http://localhost:3000/api/health > /dev/null && echo "  Grafana:    OK" || echo "  Grafana:    FAILED (check /tmp/pf-grafana.log)"
curl -s http://localhost:8080 > /dev/null && echo "  Demo App:   OK" || echo "  Demo App:   FAILED (check /tmp/pf-demo-app.log)"

echo ""
echo "Done. Open Claude Desktop and start chatting."
echo ""
echo "To stop: bash scripts/stop-claudescale.sh"
