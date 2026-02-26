# Changelog

All notable changes to ClaudeScale are documented here.

---

## [1.0.0] - 2026-02-26

### Initial Release

First stable release of ClaudeScale — AI-powered Kubernetes autoscaler using Claude via MCP protocol.

### Features

- **MCP Server** (FastMCP) with 4 tools exposed to Claude AI:
  - `claudescale_get_current_state` — cluster state and pod readiness
  - `claudescale_get_metrics` — CPU, memory, network from Prometheus
  - `claudescale_scale_deployment` — intelligent scaling with guardrails
  - `claudescale_generate_report` — markdown audit report with history

- **Kubernetes infrastructure** (minikube / local cluster):
  - Dedicated namespace `claudescale`
  - Demo application (nginx + nginx-exporter sidecar)
  - Prometheus (metrics collection via cAdvisor + service endpoints)
  - Grafana (dashboards for real-time visualization)
  - HPA as safety fallback (min=2, max=5, CPU target=50%)

- **Security hardening**:
  - RBAC with minimum permissions (ServiceAccount `claudescale-sa`)
  - LLM guardrails: cooldown 90s/180s, scale-down guard, snapshot pre-action
  - Persistent audit log per action
  - Grafana credentials via K8s Secret (not plain text)
  - Automated security audit: `scripts/security-check.sh` (21/21 checks)

- **Claude Desktop integration**:
  - MCP server configured in `~/.config/Claude/claude_desktop_config.json`
  - Validated: reactive scaling and proactive scaling scenarios tested

### Documentation

- `README.md` — architecture, quickstart, examples
- `docs/INSTALLATION.md` — step-by-step install guide
- `docs/SECURITY.md` — threat model, guardrails, recovery procedures
- `docs/CLAUDE_DESKTOP_USAGE.md` — conversation examples
- `docs/DEMO_SCENARIOS.md` — 7 demo scenarios for portfolio
- `docs/HPA_VS_CLAUDESCALE.md` — comparison with native Kubernetes HPA
- `SECURITY_POLICY.md` — vulnerability disclosure policy
- `CHANGELOG.md` — this file

### Scripts

- `scripts/start-claudescale.sh` — start all port-forwards with health check
- `scripts/stop-claudescale.sh` — stop port-forwards
- `scripts/stress-until-scale.sh` — CPU stress test to trigger scaling
- `scripts/watch-autoscaling.sh` — real-time HPA monitor
- `scripts/security-check.sh` — automated security audit
- `scripts/test-mcp-server.sh` — MCP server automated tests

### Architecture

```
Claude Desktop → MCP Server (Python/FastMCP) → Kubernetes API
                                             → Prometheus API
```

### Known Limitations

- MCP Server runs outside cluster in development (uses admin kubeconfig)
- Audit log stored in `/tmp` (not persistent across reboots)
- Single cluster support (multi-cluster planned)
- Network Policies not implemented (future hardening)
