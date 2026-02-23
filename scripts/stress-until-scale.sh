#!/bin/bash
# Generate sustained load to trigger HPA scaling

echo "Stress Test - Trigger Auto-scaling"
echo "==================================="
echo ""

echo "Estado inicial:"
kubectl get pods -n claudescale -l app=demo-app
kubectl get hpa -n claudescale demo-app-hpa
echo ""

echo "Generando carga en TODOS los pods..."
echo "  (Esto tomará ~2-3 minutos para que HPA reaccione)"
echo ""

PODS=$(kubectl get pods -n claudescale -l app=demo-app -o jsonpath='{.items[*].metadata.name}')

for POD in $PODS; do
    echo "Starting stress on $POD..."
    kubectl exec -n claudescale $POD -c nginx -- sh -c "
        apk add --no-cache stress-ng > /dev/null 2>&1
        nohup stress-ng --cpu 2 --timeout 180s > /dev/null 2>&1 &
    " &
done

echo ""
echo "Monitoreando HPA (presiona Ctrl+C para detener)..."
echo ""

watch -n 5 "kubectl get hpa -n claudescale demo-app-hpa && echo '' && kubectl get pods -n claudescale -l app=demo-app"
