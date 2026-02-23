# ClaudeScale — Session Context

## Project
AI-powered Kubernetes autoscaler using Claude via MCP protocol.
Repo: https://github.com/kratosvil/ClaudeScale
Directory: /home/kratosvil/Desarrollo/ClaudeScale

## Working rules
- Respond in technical English (B1-B2 level)
- Explain each step before executing (what, why, how)
- On failure: explain root cause + repair options
- No commits unless user explicitly says so
- No push unless user explicitly says so

---

## Current Progress

### Phase 1 — Project Setup ✅ COMPLETE
- [x] Git init + GitHub repo created (public)
- [x] .gitignore
- [x] README.md
- [x] Directory structure (mcp-server/, k8s-manifests/, monitoring/, scripts/, docs/, assets/)
- [x] Python __init__.py files
- [x] requirements.txt
- [x] .env.example
- [x] LICENSE (MIT)

### Phase 2 — Kubernetes Infrastructure ✅ COMPLETE
- [x] kubectl installed (v1.35.1)
- [x] minikube installed (v1.38.1)
- [x] Cluster started: `minikube start --driver=docker --memory=4096 --cpus=2`
- [x] Namespace `claudescale` created and set as default context
- [x] k8s-manifests/namespace.yaml
- [x] k8s-manifests/rbac.yaml (NOT applied yet — Phase 13)
- [x] docs/SETUP.md
- [x] docs/SECURITY.md

### Phase 3 — Prometheus Deployment ✅ COMPLETE
- [x] Decision: Manual manifests (not Helm)
- [x] monitoring/prometheus-config.yaml
- [x] k8s-manifests/prometheus-configmap.yaml (simplificado con cAdvisor)
- [x] k8s-manifests/prometheus-deployment.yaml (Deployment + Service + ServiceAccount + RBAC)
- [x] scripts/verify-prometheus.sh
- [x] docs/PROMETHEUS_DECISION.md
- [x] docs/PROMETHEUS_QUERIES.md
- [x] Prometheus running: pod/prometheus-c47f87c47-4bbfj 1/1

### Phase 4 — Grafana Deployment ✅ COMPLETE
- [x] monitoring/grafana-datasource.yaml
- [x] monitoring/grafana-dashboards-config.yaml
- [x] k8s-manifests/grafana-configmap.yaml
- [x] k8s-manifests/grafana-deployment.yaml
- [x] monitoring/grafana-k8s-dashboard.json
- [x] monitoring/claudescale-final-working.json (dashboard funcional — en .gitignore)
- [x] docs/GRAFANA_SETUP.md
- [x] Grafana running: pod/grafana-776d6fcfc4-mj7sz 1/1
- [x] Datasource Prometheus conectado y verificado

### Phase 5 — Demo Application ✅ COMPLETE
- [x] k8s-manifests/demo-app.yaml (nginx:alpine + nginx-exporter sidecar)
- [x] k8s-manifests/demo-app-custom-html.yaml (HTML personalizado con hostname)
- [x] k8s-manifests/demo-app-service.yaml (NodePort, sessionAffinity: None)
- [x] k8s-manifests/demo-app-hpa.yaml (HPA: min=2, max=5, CPU target=50%)
- [x] k8s-manifests/nginx-config (ConfigMap — stub_status habilitado)
- [x] scripts/generate-load.sh
- [x] scripts/generate-load-simple.sh
- [x] scripts/stress-until-scale.sh
- [x] scripts/watch-autoscaling.sh
- [x] docs/DEMO_APP.md
- [x] docs/LOAD_TESTING.md
- [x] docs/HPA_VS_CLAUDESCALE.md
- [x] Demo app running: 2 pods (2/2 cada uno — nginx + nginx-exporter)
- [x] HPA activo: cpu 1%/50%, replicas=2, min=2, max=5
- [x] metrics-server habilitado en minikube

### Phase 6 — MCP Server Development ⏳ NEXT
- [ ] Pendiente — continuar aquí mañana

---

## Cluster State (al finalizar sesión)

```
PODS en namespace claudescale:
  demo-app-67b764fdf5-2hdtb   2/2 Running
  demo-app-67b764fdf5-xz24k   2/2 Running
  grafana-776d6fcfc4-mj7sz    1/1 Running
  prometheus-c47f87c47-4bbfj  1/1 Running

SERVICES:
  demo-app    NodePort   10.96.126.136   80:31696/TCP, 9113:30279/TCP
  grafana     ClusterIP  10.109.209.250  3000/TCP
  prometheus  ClusterIP  10.102.76.159   9090/TCP

HPA:
  demo-app-hpa  cpu: 1%/50%  min=2  max=5  replicas=2

Minikube IP: 192.168.49.2
Demo app URL (NodePort): http://192.168.49.2:31696
```

## Environment State
- Python: 3.10.12 (system) — 3.11 pendiente de instalar con sudo
- venv: NOT created yet (pendiente de sudo para python3.11)
- Docker: v29.2.1 ✅
- kubectl: v1.35.1 ✅
- minikube: v1.38.1 ✅
- Cluster: running (driver=docker, memory=4096, cpus=2)
- Default namespace: claudescale
- metrics-server: enabled ✅

## Arranque de sesión (ejecutar al inicio)
```bash
cd /home/kratosvil/Desarrollo/ClaudeScale
minikube start --driver=docker --memory=4096 --cpus=2   # si está parado
kubectl config set-context --current --namespace=claudescale
kubectl get pods -n claudescale   # verificar estado
```

## Git State
- Branch: main
- Last commit: 7382dd4 — feat: Add HPA and comparison with ClaudeScale
- Commits NO pusheados a origin (verificar con `git status`)

## Notas técnicas importantes
- nginx-config ConfigMap DEBE estar montado en demo-app para que stub_status funcione
- El balanceo de carga real se ve via NodePort (192.168.49.2:31696), NO via port-forward
- Dashboard Grafana funcional: monitoring/claudescale-final-working.json (importar manualmente)
- Prometheus scraping: cAdvisor (metricas CPU/mem) + service-endpoints (nginx-exporter)
