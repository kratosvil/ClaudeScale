#!/bin/bash
# Stop all ClaudeScale port-forwards

echo "ClaudeScale — Stopping port-forwards"
echo "======================================"

pkill -f "kubectl port-forward" 2>/dev/null && echo "Port-forwards stopped." || echo "No port-forwards running."

echo ""
echo "Cluster is still running. To stop minikube:"
echo "  minikube stop"
