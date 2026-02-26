# ClaudeScale — Session Context

## Project
AI-powered Kubernetes autoscaler using Claude via MCP protocol.
Repo: https://github.com/kratosvil/ClaudeScale
Directory: /home/kratosvil/Desarrollo/ClaudeScale

## Working rules
- Responder en español, estilo técnico directo
- Explicar cada paso antes de ejecutar (qué, por qué, cómo)
- En fallo: explicar causa raíz + opciones de reparación
- No hacer commits salvo que el usuario lo pida explícitamente
- No hacer push salvo que el usuario lo pida explícitamente
- ANTES DE MODIFICAR claude_desktop_config.json: leer el archivo y verificar mcpServers existentes. Siempre AGREGAR, nunca sobreescribir.

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
- [x] k8s-manifests/demo-app-service.yaml (ClusterIP — acceso via port-forward)
- [x] k8s-manifests/demo-app-hpa.yaml (HPA: min=2, max=5, CPU target=50%)
- [x] k8s-manifests/nginx-config (ConfigMap — stub_status habilitado)
- [x] scripts/generate-load.sh
- [x] scripts/generate-load-simple.sh
- [x] scripts/stress-until-scale.sh
- [x] scripts/watch-autoscaling.sh
- [x] scripts/status.sh (resumen rápido de pods/services/HPA)
- [x] docs/DEMO_APP.md
- [x] docs/LOAD_TESTING.md
- [x] docs/HPA_VS_CLAUDESCALE.md
- [x] Demo app running: 2 pods (2/2 cada uno — nginx + nginx-exporter)
- [x] HPA activo: cpu 1%/50%, replicas=2, min=2, max=5
- [x] metrics-server habilitado en minikube

### Phase 6 — MCP Server Development ✅ COMPLETE
- [x] venv creado: /home/kratosvil/Desarrollo/ClaudeScale/venv (Python 3.10.12)
- [x] requirements-mcp.txt (fastmcp 3.0.2, kubernetes 35.0.0, prometheus-api-client 0.7.0)
- [x] mcp-server/config.py (pydantic-settings)
- [x] mcp-server/utils/kubernetes_client.py (wrapper kubectl Python SDK)
- [x] mcp-server/utils/prometheus_client.py (wrapper Prometheus API)
- [x] mcp-server/tools/scaling_tools.py (4 tools: get_state, get_metrics, scale, report)
- [x] mcp-server/server.py (FastMCP server — 4 tools registrados)
- [x] .env (configuración local — en .gitignore)
- [x] scripts/test-mcp-server.sh (test automatizado — ALL TESTS PASSED)
- [x] scripts/manual-test-tools.py (test manual por tool — flag --no-scale)
- [x] docs/MCP_SERVER_TESTING.md
- [x] Diagnóstico local ejecutado y verificado: 3 deployments, 4/4 pods ready

### Phase 7 — Claude Desktop Integration ✅ COMPLETE
- [x] ~/.config/Claude/claude_desktop_config.json actualizado (claudescale agregado sin pisar mcp-cicd-agent ni mcp-web-deployer)
- [x] _meta warning en config para recordar no sobreescribir servidores existentes
- [x] docs/CLAUDE_DESKTOP_USAGE.md (guía de uso con ejemplos de conversación)
- [x] docs/DEMO_SCENARIOS.md (7 escenarios demo + flujo de 10 minutos)
- [x] scripts/start-claudescale.sh (levanta minikube + port-forwards)
- [x] scripts/stop-claudescale.sh (detiene port-forwards)

### Phase 8 — PRÓXIMA SESIÓN ⏳
- [ ] Probar MCP server conectado a Claude Desktop (reiniciar Claude Desktop primero)
- [ ] Verificar que los 4 tools aparecen disponibles en Claude Desktop
- [ ] Ejecutar demo Scenario 1: Health Check
- [ ] Ejecutar demo Scenario 2: Reactive Scaling bajo carga
- [ ] Ajustes si hay errores de conexión

### Pendientes / Ideas futuras
- [ ] **MCP Tool: `cluster_status`** — Exponer scripts/status.sh como tool MCP de solo lectura para diagnóstico rápido desde lenguaje natural. Candidato a Phase 8 o 9.
- [ ] Phase 9: Kubernetes Architecture Detailed (ver KUBERNETES_ARCHITECTURE_DETAILED.md)

---

## Cluster State (sesión 2026-02-26)

```
PODS en namespace claudescale:
  demo-app-769855c867-cn955   2/2 Running
  demo-app-769855c867-nnx4w   2/2 Running
  grafana-776d6fcfc4-mj7sz    1/1 Running
  prometheus-c47f87c47-4bbfj  1/1 Running

SERVICES (todos ClusterIP — acceso via port-forward):
  demo-app    ClusterIP  10.96.126.136   80/TCP, 9113/TCP
  grafana     ClusterIP  10.109.209.250  3000/TCP
  prometheus  ClusterIP  10.102.76.159   9090/TCP

HPA:
  demo-app-hpa  cpu: 1%/50%  min=2  max=5  replicas=2

Minikube IP: 192.168.49.2
```

## Environment State
- Python: 3.10.12 (sistema)
- venv: /home/kratosvil/Desarrollo/ClaudeScale/venv ✅ (Python 3.10.12)
- Docker: v29.2.1 ✅
- kubectl: v1.35.1 ✅
- minikube: v1.38.1 ✅
- Cluster: running (driver=docker, memory=4096, cpus=2)
- Default namespace: claudescale
- metrics-server: enabled ✅
- fastmcp: 3.0.2 ✅
- kubernetes SDK: 35.0.0 ✅

## Arranque de sesión (ejecutar al inicio)
```bash
cd /home/kratosvil/Desarrollo/ClaudeScale
minikube start --driver=docker --memory=4096 --cpus=2   # si está parado
kubectl config set-context --current --namespace=claudescale
kubectl get pods -n claudescale                         # verificar estado
source venv/bin/activate                                # activar venv
```

## Port-forwards necesarios (para métricas y UI)
```bash
kubectl port-forward -n claudescale svc/prometheus 9090:9090 &
kubectl port-forward -n claudescale svc/grafana 3000:3000 &
kubectl port-forward -n claudescale svc/demo-app 8080:80 &
# O usar: ./scripts/start-claudescale.sh
```

## Git State
- Branch: main
- Commits locales pendientes de push (verificar con `git log origin/main..HEAD`)

## MCP Server — Archivos clave
```
mcp-server/server.py                   ← entry point FastMCP
mcp-server/config.py                   ← settings (.env)
mcp-server/tools/scaling_tools.py      ← 4 tools MCP
mcp-server/utils/kubernetes_client.py  ← kubectl wrapper
mcp-server/utils/prometheus_client.py  ← prometheus wrapper
```

## Claude Desktop MCP Config
- Archivo: ~/.config/Claude/claude_desktop_config.json
- Servers activos: claudescale, mcp-cicd-agent, mcp-web-deployer
- IMPORTANTE: Siempre leer el archivo antes de modificar. Agregar, no sobreescribir.

## Notas técnicas importantes
- nginx-config ConfigMap DEBE estar montado en demo-app para que stub_status funcione
- demo-app service es ClusterIP (no NodePort) — acceso SOLO via port-forward en localhost:8080
- Dashboard Grafana funcional: monitoring/claudescale-final-working.json (importar manualmente — en .gitignore)
- Prometheus scraping: cAdvisor (métricas CPU/mem) + service-endpoints (nginx-exporter)
- MCP server usa venv python, NO python3 del sistema
