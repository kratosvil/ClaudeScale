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

### Phase 3 — Prometheus Deployment ⏳ NEXT
- [ ] Pending — user will paste Phase 3 instructions

---

## Pending Manual Steps (require sudo in terminal)
- [ ] Install Python 3.11:
  ```bash
  sudo apt install -y software-properties-common
  sudo add-apt-repository ppa:deadsnakes/ppa -y
  sudo apt update
  sudo apt install -y python3.11 python3.11-venv
  ```
- [ ] Create virtual environment:
  ```bash
  cd /home/kratosvil/Desarrollo/ClaudeScale
  python3.11 -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt
  ```

---

## Environment State
- Python: 3.10.12 (system) — 3.11 NOT YET installed
- Docker: v29.2.1 ✅
- kubectl: v1.35.1 ✅
- minikube: v1.38.1 ✅
- Cluster: running (minikube, driver=docker)
- Default namespace: claudescale
- venv: NOT created yet

## Git State
- Branch: main
- All commits pushed to origin/main
- Last commit: 7a674a2 — docs: Add security documentation and RBAC explanation
