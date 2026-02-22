# 🏗️ KUBERNETES ARCHITECTURE BREAKDOWN
## Complete Infrastructure Layout for K8s Intelligent Scaler

---

## 🎯 SIMPLE ANSWER: What's Running?

**1 Cluster** (your local Minikube/Docker Desktop)
  ↓
**1 Namespace** ("intelligent-scaler" - like a folder)
  ↓
**4 Deployments** (4 different applications running)
  ↓
**~6 Pods total** (containers actually running)

---

## 📊 DETAILED ARCHITECTURE

```
YOUR LAPTOP
├── Minikube / Docker Desktop
│   └── Kubernetes Cluster (1)
│       └── Namespace: intelligent-scaler (1)
│           │
│           ├── Deployment: demo-app
│           │   ├── Pod: demo-app-abc123 (nginx)
│           │   ├── Pod: demo-app-def456 (nginx)
│           │   └── Pod: demo-app-ghi789 (nginx)
│           │   └── Service: demo-app (ClusterIP:80)
│           │
│           ├── Deployment: prometheus
│           │   └── Pod: prometheus-xyz789 (prometheus)
│           │   └── Service: prometheus (ClusterIP:9090)
│           │
│           ├── Deployment: grafana
│           │   └── Pod: grafana-mno456 (grafana)
│           │   └── Service: grafana (ClusterIP:3000)
│           │
│           └── Deployment: mcp-server (Phase 13)
│               └── Pod: mcp-server-pqr123 (python)
│
└── Outside Cluster (your terminal/browser)
    ├── kubectl (controls cluster)
    ├── Browser (accesses via port-forward)
    └── Claude Desktop (connects to MCP server)
```

---

## 🔢 COMPONENT COUNT

| Component | Count | Purpose |
|-----------|-------|---------|
| **Clusters** | 1 | Your local K8s environment |
| **Namespaces** | 1 | "intelligent-scaler" - keeps everything organized |
| **Deployments** | 4 | demo-app, prometheus, grafana, mcp-server |
| **Pods** | ~6 | Actual running containers (number varies) |
| **Services** | 4 | Internal networking (ClusterIP) |
| **ConfigMaps** | 3-4 | Configuration files |
| **Secrets** | 1-2 | Passwords, tokens |
| **ServiceAccounts** | 1 | For RBAC security |
| **Roles/RoleBindings** | 1 each | Security permissions |

---

## 🌐 NETWORKING - NO LOAD BALANCER

### **Why No LoadBalancer?**

❌ **NOT Using LoadBalancer because:**
- We're running **locally** (not in cloud)
- LoadBalancers are for production (AWS, GCP, Azure)
- LoadBalancers cost money in cloud
- Not needed for development/testing

✅ **Instead, we use:**
- **ClusterIP Services** (internal only, inside cluster)
- **Port-forwarding** (to access from laptop)

### **How Services Work**

```
Inside Cluster (invisible to you):
┌────────────────────────────────────┐
│ Service: demo-app                  │
│ Type: ClusterIP                    │
│ IP: 10.96.45.123 (internal only)  │
│ Port: 80                           │
└────────────┬───────────────────────┘
             │ Routes traffic to
             ▼
   ┌─────────────────────────┐
   │ Pod 1    Pod 2    Pod 3 │
   │ nginx    nginx    nginx │
   └─────────────────────────┘

Access from Laptop:
┌────────────────────────────────────┐
│ kubectl port-forward               │
│ svc/demo-app 8080:80              │
└────────────┬───────────────────────┘
             │ Creates tunnel
             ▼
   http://localhost:8080 → demo-app
```

### **Port-Forward Commands You'll Use**

```bash
# Access Prometheus
kubectl port-forward -n intelligent-scaler svc/prometheus 9090:9090
# Opens: http://localhost:9090

# Access Grafana
kubectl port-forward -n intelligent-scaler svc/grafana 3000:3000
# Opens: http://localhost:3000

# Access demo-app (if needed)
kubectl port-forward -n intelligent-scaler svc/demo-app 8080:80
# Opens: http://localhost:8080
```

---

## 📝 ALL YAML FILES (Infrastructure as Code)

### **1. Namespace** (`k8s-manifests/namespace.yaml`)
```yaml
# Creates the "folder" where everything lives
apiVersion: v1
kind: Namespace
metadata:
  name: intelligent-scaler
```
**What it does:** Organizes resources, provides isolation

---

### **2. RBAC Security** (`k8s-manifests/rbac.yaml`)
```yaml
# WHO: ServiceAccount (identity for MCP server)
# CAN DO WHAT: Read deployments, scale deployments
# WHERE: In intelligent-scaler namespace only

# ServiceAccount = identity
apiVersion: v1
kind: ServiceAccount
metadata:
  name: mcp-scaler
  namespace: intelligent-scaler
---
# Role = list of permissions
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: deployment-scaler
  namespace: intelligent-scaler
rules:
- apiGroups: ["apps"]
  resources: ["deployments", "deployments/scale"]
  verbs: ["get", "list", "patch", "update"]
---
# RoleBinding = connects identity to permissions
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: mcp-scaler-binding
  namespace: intelligent-scaler
subjects:
- kind: ServiceAccount
  name: mcp-scaler
roleRef:
  kind: Role
  name: deployment-scaler
  apiGroup: rbac.authorization.k8s.io
```
**What it does:** Security - limits what MCP server can do

---

### **3. Demo App** (`k8s-manifests/demo-app.yaml`)
```yaml
# The application we'll scale
apiVersion: apps/v1
kind: Deployment
metadata:
  name: demo-app
  namespace: intelligent-scaler
spec:
  replicas: 2  # Start with 2 pods
  selector:
    matchLabels:
      app: demo-app
  template:
    metadata:
      labels:
        app: demo-app
    spec:
      containers:
      - name: nginx
        image: nginx:alpine
        ports:
        - containerPort: 80
        resources:
          requests:
            cpu: 100m      # Minimum CPU needed
            memory: 128Mi  # Minimum memory needed
          limits:
            cpu: 200m      # Maximum CPU allowed
            memory: 256Mi  # Maximum memory allowed
---
# Service to access the pods
apiVersion: v1
kind: Service
metadata:
  name: demo-app
  namespace: intelligent-scaler
spec:
  type: ClusterIP  # Internal only
  selector:
    app: demo-app
  ports:
  - port: 80
    targetPort: 80
```
**What it does:** Runs 2 nginx pods that Claude will scale

---

### **4. Prometheus** (`k8s-manifests/prometheus-deployment.yaml`)
```yaml
# Monitoring system - collects metrics
apiVersion: apps/v1
kind: Deployment
metadata:
  name: prometheus
  namespace: intelligent-scaler
spec:
  replicas: 1  # Only need 1 Prometheus
  selector:
    matchLabels:
      app: prometheus
  template:
    metadata:
      labels:
        app: prometheus
    spec:
      containers:
      - name: prometheus
        image: prom/prometheus:latest
        ports:
        - containerPort: 9090
        volumeMounts:
        - name: config
          mountPath: /etc/prometheus
      volumes:
      - name: config
        configMap:
          name: prometheus-config
---
apiVersion: v1
kind: Service
metadata:
  name: prometheus
  namespace: intelligent-scaler
spec:
  type: ClusterIP
  selector:
    app: prometheus
  ports:
  - port: 9090
    targetPort: 9090
```
**What it does:** Collects CPU, memory metrics every 15 seconds

---

### **5. Grafana** (`k8s-manifests/grafana-deployment.yaml`)
```yaml
# Visualization - creates beautiful graphs
apiVersion: apps/v1
kind: Deployment
metadata:
  name: grafana
  namespace: intelligent-scaler
spec:
  replicas: 1
  selector:
    matchLabels:
      app: grafana
  template:
    metadata:
      labels:
        app: grafana
    spec:
      containers:
      - name: grafana
        image: grafana/grafana:latest
        ports:
        - containerPort: 3000
        env:
        - name: GF_SECURITY_ADMIN_PASSWORD
          value: "admin"  # Change in production!
---
apiVersion: v1
kind: Service
metadata:
  name: grafana
  namespace: intelligent-scaler
spec:
  type: ClusterIP
  selector:
    app: grafana
  ports:
  - port: 3000
    targetPort: 3000
```
**What it does:** Shows graphs of metrics from Prometheus

---

### **6. MCP Server** (`k8s-manifests/mcp-server-deployment.yaml`)
```yaml
# Your Python server (deployed later in Phase 13)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mcp-server
  namespace: intelligent-scaler
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mcp-server
  template:
    metadata:
      labels:
        app: mcp-server
    spec:
      serviceAccountName: mcp-scaler  # Use RBAC identity
      containers:
      - name: mcp-server
        image: k8s-scaler-mcp:latest
        env:
        - name: PROMETHEUS_URL
          value: "http://prometheus:9090"
        - name: K8S_NAMESPACE
          value: "intelligent-scaler"
        - name: K8S_IN_CLUSTER
          value: "true"
```
**What it does:** Runs your Python MCP server inside cluster

---

## 🔄 DATA FLOW - How Everything Talks

### **Normal Operation:**
```
1. Demo App runs → Exposes metrics at /metrics endpoint
                    ↓
2. Prometheus scrapes → Every 15 seconds, collects metrics
                    ↓
3. Stores in database → Time-series data (CPU, memory over time)
                    ↓
4. Grafana queries → Reads from Prometheus, shows graphs
```

### **Scaling Operation (when Claude is involved):**
```
1. You ask Claude → "Scale demo-app to 4 replicas"
        ↓
2. Claude calls MCP server → Uses get_metrics tool
        ↓
3. MCP queries Prometheus → Gets current CPU/memory
        ↓
4. Claude decides → "CPU is high, scaling is good"
        ↓
5. Claude calls MCP server → Uses scale_deployment tool
        ↓
6. MCP calls K8s API → Changes replica count
        ↓
7. Kubernetes reacts → Creates new pods
        ↓
8. Prometheus detects → Sees new pods, starts scraping
        ↓
9. Grafana shows change → You see the scaling in graphs
        ↓
10. MCP generates report → Creates markdown file with details
```

---

## 🔐 SECURITY LAYERS

### **Layer 1: Namespace Isolation**
- Everything in "intelligent-scaler" namespace
- Can't affect other namespaces

### **Layer 2: RBAC (Role-Based Access Control)**
- ServiceAccount: `mcp-scaler` (identity)
- Role: `deployment-scaler` (permissions)
- RoleBinding: connects them
- **Result:** MCP server can ONLY:
  - Read deployments
  - Scale deployments
  - Nothing else!

### **Layer 3: Network Policies** (optional, Phase 10)
- Restricts which pods can talk to which
- Example: Only MCP server can talk to K8s API

### **Layer 4: Resource Limits**
- Each pod has CPU/memory limits
- Prevents one pod from consuming all resources

---

## 📦 RESOURCE REQUESTS vs LIMITS

Every pod defines:

**Requests** = Minimum resources needed
- "I need at least 100m CPU to run"
- Kubernetes won't schedule me unless node has this

**Limits** = Maximum resources allowed
- "I can use up to 200m CPU, no more"
- If I try to use more, Kubernetes throttles me

**Example:**
```yaml
resources:
  requests:
    cpu: 100m       # 100 millicores = 0.1 CPU
    memory: 128Mi   # 128 Mebibytes
  limits:
    cpu: 200m       # 200 millicores = 0.2 CPU
    memory: 256Mi   # 256 Mebibytes
```

**Units:**
- `m` = millicores (1000m = 1 full CPU core)
- `Mi` = Mebibytes (1024 Mi = 1 GiB)
- `Gi` = Gibibytes

---

## 🎓 LEARNING POINTS

### **Kubernetes Hierarchy:**
```
Cluster
  └── Namespace
      └── Deployment
          └── ReplicaSet (managed automatically)
              └── Pod(s)
                  └── Container(s)
```

### **Services:**
- **ClusterIP**: Internal only (what we use)
- **NodePort**: Exposes on each node's IP
- **LoadBalancer**: External load balancer (cloud only)

### **ConfigMaps vs Secrets:**
- **ConfigMap**: Non-sensitive config (Prometheus config, etc.)
- **Secret**: Sensitive data (passwords, tokens) - base64 encoded

---

## 💡 COMMON QUESTIONS

**Q: Do I need 1 cluster per project?**
A: No! You can have many namespaces in 1 cluster. We use namespaces to separate projects.

**Q: Why ClusterIP instead of LoadBalancer?**
A: LoadBalancer costs money in cloud and isn't needed locally. ClusterIP + port-forward works perfectly for development.

**Q: How many replicas should I use?**
A: Start with 2 for demo-app. That's enough to see scaling work. In production, you'd use more based on traffic.

**Q: Can pods talk to each other?**
A: Yes! Within the same namespace, pods can reach each other by service name (e.g., `http://prometheus:9090`).

**Q: What happens if a pod crashes?**
A: Kubernetes automatically restarts it. That's the "self-healing" feature!

---

## 🚀 NEXT STEPS

When you're ready to build:
1. Start with namespace (Task 7)
2. Add demo-app (Task 18)
3. Add Prometheus (Task 11-12)
4. Add Grafana (Task 15-16)
5. Finally add MCP server (Task 44)

Each builds on the previous! 🎯
