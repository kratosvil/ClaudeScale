# ClaudeScale — Installation Guide

Step-by-step installation from scratch.

## System Requirements

### Minimum
- **OS:** Ubuntu 22.04 LTS or similar Linux
- **RAM:** 8GB (16GB recommended)
- **CPU:** 2 cores (4 recommended)
- **Disk:** 20GB free space
- **Software:** Docker 20.10+, Python 3.10+, kubectl 1.28+, Claude Desktop

### Verified
- Ubuntu 22.04 LTS
- Docker 29.x
- Python 3.10.12
- kubectl v1.35.1
- minikube v1.38.1

---

## Step 1 — Install Prerequisites

### Docker
```bash
sudo apt update
sudo apt install -y docker.io
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker $USER
newgrp docker
docker --version
```

### Minikube
```bash
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
minikube version
```

### kubectl
```bash
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install kubectl /usr/local/bin/
kubectl version --client
```

### Claude Desktop
Download from: https://claude.ai/download

---

## Step 2 — Clone Repository

```bash
cd ~/Desarrollo
git clone https://github.com/kratosvil/ClaudeScale.git
cd ClaudeScale
```

---

## Step 3 — Setup Python Environment

```bash
cd ~/Desarrollo/ClaudeScale

# Crear venv
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements-mcp.txt

# Verificar imports
python3 -c "import fastmcp, kubernetes, prometheus_api_client; print('OK - All imports successful')"
```

---

## Step 4 — Start Minikube Cluster

```bash
minikube start --driver=docker --memory=4096 --cpus=2
minikube addons enable metrics-server

# Verificar
kubectl get nodes
minikube status
```

---

## Step 5 — Deploy Kubernetes Resources

```bash
# Namespace
kubectl apply -f k8s-manifests/namespace.yaml
kubectl config set-context --current --namespace=claudescale

# Prometheus
kubectl apply -f k8s-manifests/prometheus-configmap.yaml
kubectl apply -f k8s-manifests/prometheus-deployment.yaml

# Grafana
kubectl apply -f k8s-manifests/grafana-configmap.yaml
kubectl apply -f k8s-manifests/grafana-deployment.yaml

# Demo app
kubectl apply -f k8s-manifests/demo-app.yaml
kubectl apply -f k8s-manifests/demo-app-hpa.yaml

# Esperar a que estén ready
kubectl wait --for=condition=ready pod --all -n claudescale --timeout=300s

# Verificar
kubectl get all -n claudescale
```

---

## Step 6 — Configure Claude Desktop

El archivo de configuración está en:
```
~/.config/Claude/claude_desktop_config.json
```

Añadir la entrada `claudescale` al objeto `mcpServers` (sin sobreescribir entradas existentes):

```json
{
  "mcpServers": {
    "claudescale": {
      "command": "/home/kratosvil/Desarrollo/ClaudeScale/venv/bin/python",
      "args": [
        "/home/kratosvil/Desarrollo/ClaudeScale/mcp-server/server.py"
      ],
      "env": {
        "PYTHONPATH": "/home/kratosvil/Desarrollo/ClaudeScale/mcp-server",
        "KUBERNETES_NAMESPACE": "claudescale",
        "PROMETHEUS_LOCAL_URL": "http://localhost:9090",
        "KUBERNETES_IN_CLUSTER": "false"
      }
    }
  }
}
```

---

## Step 7 — Start Port-Forwards

Cada uno en su propia terminal:

```bash
# Terminal 1 — Prometheus (requerido por MCP server)
kubectl port-forward -n claudescale svc/prometheus 9090:9090

# Terminal 2 — Grafana (UI opcional)
kubectl port-forward -n claudescale svc/grafana 3000:3000

# Terminal 3 — Demo App
kubectl port-forward -n claudescale svc/demo-app 8080:80
```

---

## Step 8 — Test MCP Server

```bash
cd ~/Desarrollo/ClaudeScale
source venv/bin/activate
./scripts/test-mcp-server.sh
```

Salida esperada:
```
✅ Kubernetes connection OK
✅ Namespace OK
✅ Deployment OK
✅ All imports successful
✅ ALL TESTS PASSED!
```

---

## Step 9 — Verify Claude Desktop Integration

1. Abrir Claude Desktop
2. Reiniciar si ya estaba abierto
3. Escribir: `Check my Kubernetes cluster status`

Respuesta esperada:
```
Your cluster is healthy with:
- demo-app: 2/2 replicas ready
- prometheus: 1/1 replica ready
- grafana: 1/1 replica ready
```

---

## Troubleshooting

### Minikube no arranca
```bash
sudo systemctl status docker
minikube delete
minikube start --driver=docker --memory=4096 --cpus=2
```

### Pods en Pending
```bash
kubectl get events -n claudescale --sort-by='.lastTimestamp'
kubectl describe pod <pod-name> -n claudescale
```

### MCP Server no conecta en Claude Desktop
```bash
# Verificar sintaxis del config
python3 -m json.tool ~/.config/Claude/claude_desktop_config.json

# Test manual del server
cd ~/Desarrollo/ClaudeScale
source venv/bin/activate
cd mcp-server && python3 server.py
```

### Prometheus no accesible
```bash
kubectl get pods -n claudescale -l app=prometheus
curl http://localhost:9090/api/v1/query?query=up

# Reiniciar port-forward
pkill -f "port-forward.*prometheus"
kubectl port-forward -n claudescale svc/prometheus 9090:9090
```

### Claude Desktop no ve los tools
- Reiniciar Claude Desktop completamente
- Verificar que el port-forward de Prometheus está activo
- Revisar que el venv tiene las dependencias: `pip list | grep fastmcp`

---

## Uninstall

```bash
# Borrar recursos Kubernetes
kubectl delete namespace claudescale

# Parar Minikube
minikube stop
minikube delete

# Eliminar proyecto (opcional)
rm -rf ~/Desarrollo/ClaudeScale
```

---

**Tiempo estimado de instalación: ~20-30 minutos**
