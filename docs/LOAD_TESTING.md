# Load Testing Demo App

## Scripts Available

### 1. generate-load.sh (Advanced)
Uses `stress-ng` to generate CPU load inside the pod.

**Usage:**
```bash
./scripts/generate-load.sh [duration] [intensity]

# Examples:
./scripts/generate-load.sh 60 high      # 60 seconds, high CPU
./scripts/generate-load.sh 120 medium   # 2 minutes, medium CPU
./scripts/generate-load.sh 30 low       # 30 seconds, low CPU
```

**Intensity levels:**
- `low`: 1 CPU worker
- `medium`: 2 CPU workers
- `high`: 4 CPU workers

### 2. generate-load-simple.sh (Simple)
Generates HTTP requests (less CPU intensive but easier).

**Usage:**
```bash
./scripts/generate-load-simple.sh [duration] [requests_per_sec]

# Examples:
./scripts/generate-load-simple.sh 60 10   # 60s at 10 req/s
./scripts/generate-load-simple.sh 120 50  # 2min at 50 req/s
```

## Manual Load Testing

### Using Apache Bench (ab)
```bash
# Install (if not present)
sudo apt install apache2-utils

# Port forward demo-app
kubectl port-forward -n claudescale svc/demo-app 8080:80

# Generate load
ab -n 10000 -c 100 http://localhost:8080/
# -n: total requests
# -c: concurrent requests
```

### Using hey
```bash
# Install
go install github.com/rakyll/hey@latest

# Generate load
hey -n 10000 -c 100 http://localhost:8080/
```

## Monitoring During Load Test

### Prometheus Queries
```promql
# CPU usage
rate(container_cpu_usage_seconds_total{pod=~"demo-app-.*"}[1m])

# Memory usage
container_memory_usage_bytes{pod=~"demo-app-.*"} / 1024 / 1024

# Network traffic
rate(container_network_receive_bytes_total{pod=~"demo-app-.*"}[1m])
```

### kubectl Commands
```bash
# Watch pod metrics
kubectl top pods -n claudescale -l app=demo-app

# Watch in real-time
watch -n 1 kubectl top pods -n claudescale -l app=demo-app
```

### Grafana
Open dashboard and watch graphs update in real-time during load test.

## Expected Behavior

With 2 pods and CPU limit of 200m each:

1. **No load:** CPU ~5-10m per pod
2. **Low load:** CPU ~50-80m per pod
3. **Medium load:** CPU ~100-150m per pod
4. **High load:** CPU approaching 200m (limit)

When CPU consistently exceeds ~150m (75%), it's a good time to scale up!
