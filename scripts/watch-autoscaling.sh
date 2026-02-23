#!/bin/bash
# Watch auto-scaling in real-time

echo "Watching Auto-scaling Events"
echo "============================="
echo ""

while true; do
    clear
    date
    echo ""
    echo "=== HPA Status ==="
    kubectl get hpa -n claudescale demo-app-hpa
    echo ""
    echo "=== Pods ==="
    kubectl get pods -n claudescale -l app=demo-app
    echo ""
    echo "=== CPU Usage ==="
    kubectl top pods -n claudescale -l app=demo-app 2>/dev/null || echo "Metrics not available yet"
    echo ""
    echo "=== Recent Events ==="
    kubectl get events -n claudescale --sort-by='.lastTimestamp' | grep -E "demo-app|Scaled" | tail -5
    echo ""
    echo "Press Ctrl+C to stop monitoring"
    sleep 5
done
