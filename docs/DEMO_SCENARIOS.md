# Demo Scenarios

Seven scenarios to showcase ClaudeScale capabilities.

---

## Quick Demo Flow (10 minutes)

1. Health Check (1 min)
2. Metrics Check (1 min)
3. Generate Load (2 min)
4. Reactive Scaling (2 min)
5. Audit Report (1 min)
6. Scale Down (1 min)
7. Summary (2 min)

---

## Scenario 1 — Health Check

**Goal:** Show Claude reading cluster state via MCP.

**Setup:** Cluster running, no load.

**Prompt:**
```
Check the status of my Kubernetes cluster
```

**Expected:**
- Claude calls `claudescale_get_current_state`
- Lists 3 deployments, 4 pods, all healthy
- No scaling action needed

---

## Scenario 2 — Metrics Baseline

**Goal:** Show Prometheus integration.

**Setup:** Prometheus port-forward active on localhost:9090.

**Prompt:**
```
What are the current CPU and memory metrics for demo-app?
```

**Expected:**
- Claude calls `claudescale_get_metrics`
- Reports low CPU (~1-5%), low memory
- Confirms no scaling needed

---

## Scenario 3 — Reactive Scaling

**Goal:** Show AI-driven reactive scaling under real load.

**Setup:** Run stress test in a separate terminal:
```bash
bash scripts/stress-until-scale.sh
```

**Prompt (after ~60s of load):**
```
Check the metrics and decide if we need to scale demo-app
```

**Expected:**
- Claude detects high CPU (>70%)
- Calls `claudescale_scale_deployment`
- Scales 2 → 3 replicas with explanation

---

## Scenario 4 — Proactive Scaling

**Goal:** Show intelligence beyond threshold rules.

**Setup:** No load running.

**Prompt:**
```
We're doing a product launch in 10 minutes and expect 5x traffic. Prepare the cluster.
```

**Expected:**
- Claude doesn't wait for high CPU
- Scales proactively to 4-5 replicas
- Explains reasoning: "Scaling ahead of anticipated spike"

---

## Scenario 5 — Cost Optimization

**Goal:** Show intelligent scale-down.

**Setup:** Cluster at 4-5 replicas after previous scenarios.

**Prompt:**
```
Traffic has dropped back to normal. Optimize the cluster for cost.
```

**Expected:**
- Claude checks current metrics (low CPU/memory)
- Scales down to 2 replicas (minimum)
- Explains: "Low utilization — reducing to minimum for cost efficiency"

---

## Scenario 6 — Audit Report

**Goal:** Show explainability and audit trail.

**Prompt:**
```
Generate a full scaling report for the last session
```

**Expected:**
- Claude calls `claudescale_get_current_state` + `claudescale_get_metrics`
- Generates markdown report with:
  - Cluster state snapshot
  - Current metrics
  - Scaling actions taken
  - Recommendations

---

## Scenario 7 — Multi-factor Decision

**Goal:** Show context-aware reasoning vs simple HPA.

**Prompt:**
```
CPU is at 45% and memory at 60%. Should we scale?
```

**Expected:**
- Claude analyzes both metrics together
- Considers that CPU is below 50% threshold but memory trend is worth watching
- Recommends monitoring vs immediate scaling
- Explains reasoning — this is what differentiates ClaudeScale from HPA

---

## Portfolio Talking Points

When presenting ClaudeScale:

> "Standard Kubernetes HPA scales when CPU crosses 50%. ClaudeScale uses Claude AI to consider multiple signals simultaneously — CPU, memory, network trends, and context — and explains every decision in plain language. This is how a human SRE would reason about capacity planning."

Key differentiators to highlight:
- **Explainability** — Claude says WHY it scaled, not just that it did
- **Proactive** — scales before thresholds are hit
- **Conversational** — natural language control of infrastructure
- **Multi-metric** — considers CPU + memory + network together
