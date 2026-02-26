# Claude Desktop Usage Guide

How to use ClaudeScale from Claude Desktop via MCP protocol.

## Prerequisites

Before opening Claude Desktop:

1. Minikube running: `minikube status`
2. Port-forward Prometheus active: `kubectl port-forward -n claudescale svc/prometheus 9090:9090`
3. MCP server configured in `~/.config/Claude/claude_desktop_config.json`

---

## Starting Up

```bash
# 1. Start cluster (if stopped)
minikube start --driver=docker --memory=4096 --cpus=2
kubectl config set-context --current --namespace=claudescale

# 2. Start port-forwards
kubectl port-forward -n claudescale svc/prometheus 9090:9090 &
kubectl port-forward -n claudescale svc/grafana 3000:3000 &
kubectl port-forward -n claudescale svc/demo-app 8080:80 &

# 3. Open Claude Desktop
```

---

## Available Tools

Claude has access to 4 tools via MCP:

| Tool | What it does |
|------|-------------|
| `claudescale_get_current_state` | Lists deployments, replicas, pod status |
| `claudescale_get_metrics` | Queries Prometheus for CPU, memory, network |
| `claudescale_scale_deployment` | Scales a deployment (min 2, max 5 replicas) |
| `claudescale_generate_report` | Generates a full markdown audit report |

---

## Example Conversations

### Health Check
```
You: Check the status of my Kubernetes cluster

Claude: [calls claudescale_get_current_state]
Your cluster is healthy:
- demo-app: 2/2 replicas ready
- prometheus: 1/1 replica ready
- grafana: 1/1 replica ready
Total: 4/4 pods running
```

### Check Metrics
```
You: What's the current CPU usage on demo-app?

Claude: [calls claudescale_get_metrics]
demo-app CPU usage: 12% (0.024 cores average)
Memory: 18MB / 256MB limit
Status: Healthy — no scaling needed
```

### Manual Scale Up
```
You: Scale demo-app to 4 replicas, we have a traffic spike coming

Claude: [calls claudescale_scale_deployment]
Scaled demo-app from 2 → 4 replicas.
Reason: Proactive scaling for anticipated traffic spike.
New pods will be ready in ~30 seconds.
```

### Reactive Scaling (after load test)
```
You: Check the metrics and decide if we need to scale

Claude: [calls claudescale_get_metrics]
CPU usage is at 87% (0.174 cores). This is above the 80%
threshold I recommend for scaling.

[calls claudescale_scale_deployment]
Scaled demo-app from 2 → 3 replicas.
Reason: CPU at 87% — adding capacity to maintain performance.
```

### Generate Audit Report
```
You: Generate a scaling report for the last 10 minutes

Claude: [calls claudescale_get_current_state + claudescale_get_metrics]

# ClaudeScale Scaling Report
**Time:** 2026-02-26 11:30 UTC
**Namespace:** claudescale

## Cluster State
- demo-app: 3/3 replicas (scaled up from 2)
...
```

### Scale Down
```
You: Traffic has dropped, optimize the cluster

Claude: [calls claudescale_get_metrics]
CPU is at 8%, memory at 15%. Over-provisioned.

[calls claudescale_scale_deployment]
Scaled demo-app from 3 → 2 replicas (minimum).
Reason: Low utilization — optimizing resource cost.
```

---

## Tips

- Always have Prometheus port-forward running before asking for metrics
- Claude will explain every scaling decision
- Scaling is limited to 2-5 replicas (hardcoded safety limits)
- Ask Claude to "generate a report" to get a full audit trail
- You can ask in natural language: "Is the cluster healthy?", "Do we need more pods?"
