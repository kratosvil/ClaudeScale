#!/bin/bash
# Load Generation Script for demo-app
# This simulates high CPU usage to trigger scaling

echo "ClaudeScale Load Generator"
echo "=========================="
echo ""

# Configuration
NAMESPACE="claudescale"
DEPLOYMENT="demo-app"
DURATION=${1:-60}
INTENSITY=${2:-high}

echo "Configuration:"
echo "  Namespace: $NAMESPACE"
echo "  Deployment: $DEPLOYMENT"
echo "  Duration: ${DURATION}s"
echo "  Intensity: $INTENSITY"
echo ""

# Get first pod
POD=$(kubectl get pods -n $NAMESPACE -l app=$DEPLOYMENT -o jsonpath='{.items[0].metadata.name}')

if [ -z "$POD" ]; then
    echo "No pods found for deployment $DEPLOYMENT"
    exit 1
fi

echo "Target pod: $POD"
echo ""

# Generate load based on intensity
case $INTENSITY in
    low)
        WORKERS=1
        ;;
    medium)
        WORKERS=2
        ;;
    high)
        WORKERS=4
        ;;
    *)
        echo "Invalid intensity. Use: low, medium, high"
        exit 1
        ;;
esac

echo "Starting load generation..."
echo "  Workers: $WORKERS"
echo "  Duration: ${DURATION}s"
echo ""
echo "Press Ctrl+C to stop early"
echo ""

kubectl exec -n $NAMESPACE $POD -- sh -c "
    apk add --no-cache stress-ng 2>/dev/null || true
    echo 'Generating CPU load...'
    timeout ${DURATION}s stress-ng --cpu $WORKERS --timeout ${DURATION}s --metrics-brief
"

echo ""
echo "Load generation complete!"
echo ""
echo "Check metrics:"
echo "  Prometheus: http://localhost:9090"
echo "  Query: rate(container_cpu_usage_seconds_total{pod=~\"demo-app-.*\"}[1m])"
echo ""
echo "  Grafana: http://localhost:3000"
echo "  Dashboard: ClaudeScale - Kubernetes Overview"
echo ""
