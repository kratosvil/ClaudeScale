# Grafana Setup and Usage

## First Time Access

1. **Start port-forward:**
```bash
kubectl port-forward -n claudescale svc/grafana 3000:3000
```

2. **Open browser:**
```
http://localhost:3000
```

3. **Login:**
   - Username: `admin`
   - Password: `admin`
   - You'll be prompted to change password (can skip)

## Verify Prometheus Connection

1. Go to **Configuration** (gear icon) → **Data Sources**
2. You should see **Prometheus** listed
3. Click on it
4. Scroll down and click **Save & Test**
5. Should see green message: "Data source is working"

## Import ClaudeScale Dashboard

### Method 1: Manual Import
1. Click **+** (plus icon) → **Import**
2. Click **Upload JSON file**
3. Select: `monitoring/grafana-k8s-dashboard.json`
4. Click **Load**
5. Select **Prometheus** as data source
6. Click **Import**

### Method 2: Copy-Paste
1. Click **+** → **Import**
2. Open `monitoring/grafana-k8s-dashboard.json`
3. Copy all content
4. Paste in Grafana import box
5. Click **Load**

## Import Community Dashboards

Grafana has thousands of pre-made dashboards. Here are good ones for Kubernetes:

### Kubernetes Cluster Monitoring (ID: 315)
1. Click **+** → **Import**
2. Enter ID: `315`
3. Click **Load**
4. Select Prometheus datasource
5. Click **Import**

### Kubernetes Pods (ID: 6417)
1. Click **+** → **Import**
2. Enter ID: `6417`
3. Click **Load**
4. Select Prometheus datasource
5. Click **Import**

### Node Exporter (ID: 1860)
1. Click **+** → **Import**
2. Enter ID: `1860`
3. Click **Load**
4. Select Prometheus datasource
5. Click **Import**

## Useful Queries for ClaudeScale

### CPU Usage of demo-app
```promql
rate(container_cpu_usage_seconds_total{pod=~"demo-app-.*"}[5m])
```

### Memory Usage of demo-app
```promql
container_memory_usage_bytes{pod=~"demo-app-.*"} / 1024 / 1024
```

### Number of Replicas
```promql
count(container_cpu_usage_seconds_total{pod=~"demo-app-.*"})
```

### All Pods in claudescale namespace
```promql
count by (pod) (container_cpu_usage_seconds_total{namespace="claudescale"})
```

## Tips

- **Auto-refresh:** Set to 10s or 30s for live monitoring
- **Time range:** Use "Last 5 minutes" for recent data
- **Variables:** Create dashboard variables for dynamic deployment names
- **Alerts:** Set up alerts for high CPU/memory (Phase 11)
- **Annotations:** Add annotations for scaling events (Phase 11)

## Troubleshooting

### "No data" in graphs
- Check Prometheus is running: `kubectl get pods -n claudescale`
- Verify datasource connection in Grafana
- Check if metrics exist in Prometheus: http://localhost:9090

### Can't connect to Grafana
- Verify port-forward is running
- Check pod status: `kubectl get pods -n claudescale -l app=grafana`
- Check logs: `kubectl logs -n claudescale -l app=grafana`

### Forgot password
```bash
# Delete Grafana pod (it will recreate with default password)
kubectl delete pod -n claudescale -l app=grafana
```
