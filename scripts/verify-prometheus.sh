#!/bin/bash
# Verification script for Prometheus

echo "Verifying Prometheus installation..."
echo ""

echo "1. Pod status:"
kubectl get pods -n claudescale -l app=prometheus
echo ""

echo "2. Service:"
kubectl get svc -n claudescale prometheus
echo ""

echo "3. Testing Prometheus API (requires port-forward in another terminal)..."
echo "   Run this in another terminal first:"
echo "   kubectl port-forward -n claudescale svc/prometheus 9090:9090"
echo ""

read -p "Press Enter when port-forward is running..."

if curl -s http://localhost:9090/api/v1/query?query=up > /dev/null 2>&1; then
    echo "Prometheus API is responding!"
    TARGETS=$(curl -s http://localhost:9090/api/v1/targets | grep -o '"health":"up"' | wc -l)
    echo "Found $TARGETS healthy targets"
else
    echo "Prometheus API not reachable. Is port-forward running?"
fi

echo ""
echo "Quick test queries:"
echo ""
echo "Query: up"
curl -s "http://localhost:9090/api/v1/query?query=up" | python3 -m json.tool 2>/dev/null | head -20

echo ""
echo "Verification complete!"
echo "   Open http://localhost:9090 in your browser to explore"
