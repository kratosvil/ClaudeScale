#!/bin/bash
# Simple load generator using HTTP requests
# No installation needed in pods

echo "Simple HTTP Load Generator"
echo "=========================="
echo ""

NAMESPACE="claudescale"
SERVICE="demo-app"
DURATION=${1:-60}
REQUESTS_PER_SEC=${2:-10}

echo "Configuration:"
echo "  Target: $SERVICE.$NAMESPACE"
echo "  Duration: ${DURATION}s"
echo "  Rate: ${REQUESTS_PER_SEC} req/s"
echo ""

TOTAL=$((DURATION * REQUESTS_PER_SEC))
DELAY=$(echo "scale=3; 1/$REQUESTS_PER_SEC" | bc)

echo "Starting HTTP flood..."
echo "  Total requests: $TOTAL"
echo ""

# Port forward in background
kubectl port-forward -n $NAMESPACE svc/$SERVICE 8888:80 > /dev/null 2>&1 &
PF_PID=$!
sleep 2

# Generate requests
for i in $(seq 1 $TOTAL); do
    curl -s http://localhost:8888/ > /dev/null &
    sleep $DELAY

    if [ $((i % 50)) -eq 0 ]; then
        echo "  Sent $i/$TOTAL requests..."
    fi
done

echo ""
echo "Load generation complete!"

# Cleanup
kill $PF_PID 2>/dev/null
