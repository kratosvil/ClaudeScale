#!/bin/bash
# ClaudeScale — Cluster status overview

NS="claudescale"

echo "=========================================="
echo "  ClaudeScale — Cluster Status"
echo "=========================================="
echo ""

echo "--- Minikube ---"
minikube status
echo ""

echo "--- Pods [$NS] ---"
kubectl get pods -n $NS -o wide
echo ""

echo "--- Services [$NS] ---"
kubectl get svc -n $NS
echo ""

echo "--- HPA [$NS] ---"
kubectl get hpa -n $NS
echo ""

echo "--- Minikube IP ---"
echo "  $(minikube ip)"
echo ""
