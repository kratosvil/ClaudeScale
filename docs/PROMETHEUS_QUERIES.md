# Useful Prometheus Queries for ClaudeScale

## Basic Health Checks

### Check all targets are up
```promql
up
```
Returns 1 if target is reachable, 0 if down.

### Count running pods
```promql
count(up{job="kubernetes-pods"})
```

## Container Metrics

### CPU Usage (percentage)
```promql
# Average CPU usage across all containers in a deployment
avg(rate(container_cpu_usage_seconds_total{pod=~"demo-app-.*"}[5m])) * 100
```

### Memory Usage (MB)
```promql
# Average memory usage
avg(container_memory_usage_bytes{pod=~"demo-app-.*"}) / 1024 / 1024
```

### Network Traffic (bytes/sec)
```promql
# Receive rate
rate(container_network_receive_bytes_total{pod=~"demo-app-.*"}[5m])

# Transmit rate
rate(container_network_transmit_bytes_total{pod=~"demo-app-.*"}[5m])
```

## Pod Metrics

### Number of replicas
```promql
# Current running pods
count(container_cpu_usage_seconds_total{pod=~"demo-app-.*"})
```

### Pod restarts
```promql
kube_pod_container_status_restarts_total{namespace="claudescale"}
```

## Aggregations

### Top 5 pods by CPU
```promql
topk(5, rate(container_cpu_usage_seconds_total[5m]))
```

### Average CPU per deployment
```promql
avg by (pod) (rate(container_cpu_usage_seconds_total{namespace="claudescale"}[5m]))
```

## Alerts (for future use)

### High CPU Alert
```promql
avg(rate(container_cpu_usage_seconds_total{pod=~"demo-app-.*"}[5m])) > 0.8
```

### High Memory Alert
```promql
avg(container_memory_usage_bytes{pod=~"demo-app-.*"}) > 500000000  # 500MB
```

### Pod Down Alert
```promql
up{job="kubernetes-pods"} == 0
```

## Tips

- `[5m]` = look back 5 minutes
- `rate()` = per-second rate of increase
- `avg()` = average across all matching series
- `sum()` = total across all matching series
- `by (label)` = group results by label
