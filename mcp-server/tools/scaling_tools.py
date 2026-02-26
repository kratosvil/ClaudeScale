"""
MCP Tools for ClaudeScale
These tools will be available to Claude for intelligent scaling decisions
"""
from typing import Dict, Any, Optional
from datetime import datetime


async def get_current_state(k8s_client, namespace: str = "claudescale") -> Dict[str, Any]:
    """
    Tool 1: Get current state of all deployments

    This tool allows Claude to see:
    - How many deployments exist
    - Current replica count for each
    - How many pods are ready
    - Overall health status

    Args:
        k8s_client: Kubernetes client instance
        namespace: Kubernetes namespace

    Returns:
        Dict with deployment information
    """
    deployments = k8s_client.list_deployments()

    return {
        "namespace": namespace,
        "timestamp": datetime.now().isoformat(),
        "deployments": deployments,
        "total_deployments": len(deployments),
        "total_pods": sum(d["replicas"] for d in deployments),
        "total_ready_pods": sum(d["ready_replicas"] for d in deployments)
    }


async def get_metrics(
    prom_client,
    namespace: str = "claudescale",
    deployment: str = "demo-app",
    lookback_minutes: int = 5
) -> Dict[str, Any]:
    """
    Tool 2: Get metrics from Prometheus

    This tool allows Claude to analyze:
    - CPU usage patterns
    - Memory consumption
    - Network traffic
    - Trends over time

    Args:
        prom_client: Prometheus client instance
        namespace: Kubernetes namespace
        deployment: Deployment name
        lookback_minutes: How many minutes of history to consider

    Returns:
        Dict with comprehensive metrics
    """
    pod_filter = f"{deployment}.*"

    cpu_metrics = prom_client.get_cpu_usage(namespace, pod_filter)
    memory_metrics = prom_client.get_memory_usage(namespace, pod_filter)
    network_metrics = prom_client.get_network_traffic(namespace, pod_filter)

    cpu_values = [p["value"] for p in cpu_metrics["pods"]]
    cpu_avg = cpu_metrics["average_cpu"]
    cpu_max = max(cpu_values) if cpu_values else 0
    cpu_min = min(cpu_values) if cpu_values else 0

    cpu_limit = 0.2  # 200m = 0.2 cores
    cpu_utilization_pct = (cpu_avg / cpu_limit) * 100 if cpu_limit > 0 else 0

    return {
        "timestamp": datetime.now().isoformat(),
        "namespace": namespace,
        "deployment": deployment,
        "lookback_minutes": lookback_minutes,
        "cpu": {
            "average_cores": round(cpu_avg, 4),
            "max_cores": round(cpu_max, 4),
            "min_cores": round(cpu_min, 4),
            "limit_cores": cpu_limit,
            "utilization_percent": round(cpu_utilization_pct, 2),
            "pods": cpu_metrics["pods"]
        },
        "memory": {
            "average_mb": round(memory_metrics["average_memory_mb"], 2),
            "pods": memory_metrics["pods"]
        },
        "network": {
            "receive_bps": round(network_metrics["receive_bps"], 2),
            "transmit_bps": round(network_metrics["transmit_bps"], 2)
        },
        "analysis": {
            "cpu_high": cpu_utilization_pct > 75,
            "cpu_very_high": cpu_utilization_pct > 90,
            "recommendation": "scale_up" if cpu_utilization_pct > 75 else "stable"
        }
    }


async def scale_deployment(
    k8s_client,
    deployment: str,
    replicas: int,
    namespace: str = "claudescale",
    reason: Optional[str] = None
) -> Dict[str, Any]:
    """
    Tool 3: Scale a deployment

    This tool allows Claude to:
    - Increase replica count (scale up)
    - Decrease replica count (scale down)
    - Execute scaling decisions

    Args:
        k8s_client: Kubernetes client instance
        deployment: Deployment name
        replicas: Desired number of replicas
        namespace: Kubernetes namespace
        reason: Why scaling is being performed (for audit trail)

    Returns:
        Dict with scaling result
    """
    current = k8s_client.get_deployment(deployment)

    if not current:
        return {
            "success": False,
            "error": f"Deployment '{deployment}' not found in namespace '{namespace}'"
        }

    current_replicas = current["replicas"]

    MIN_REPLICAS = 2
    MAX_REPLICAS = 5

    if replicas < MIN_REPLICAS:
        return {
            "success": False,
            "error": f"Cannot scale below minimum of {MIN_REPLICAS} replicas"
        }

    if replicas > MAX_REPLICAS:
        return {
            "success": False,
            "error": f"Cannot scale above maximum of {MAX_REPLICAS} replicas"
        }

    if replicas == current_replicas:
        return {
            "success": True,
            "action": "no_change",
            "message": f"Deployment already at {replicas} replicas",
            "current_replicas": current_replicas,
            "desired_replicas": replicas
        }

    result = k8s_client.scale_deployment(deployment, replicas)

    return {
        "success": True,
        "action": "scaled_up" if replicas > current_replicas else "scaled_down",
        "namespace": namespace,
        "deployment": deployment,
        "previous_replicas": current_replicas,
        "new_replicas": replicas,
        "change": replicas - current_replicas,
        "reason": reason or "No reason provided",
        "timestamp": datetime.now().isoformat(),
        "result": result
    }


async def generate_report(
    state: Dict,
    metrics: Dict,
    scaling_action: Optional[Dict] = None
) -> str:
    """
    Tool 4: Generate markdown report

    This tool allows Claude to:
    - Create audit trail
    - Explain scaling decisions
    - Document system state

    Args:
        state: Current state from get_current_state()
        metrics: Metrics from get_metrics()
        scaling_action: Scaling action from scale_deployment() (if any)

    Returns:
        Markdown formatted report
    """
    report = f"""# ClaudeScale Scaling Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Current State

- **Namespace:** {state['namespace']}
- **Total Deployments:** {state['total_deployments']}
- **Total Pods:** {state['total_pods']}
- **Ready Pods:** {state['total_ready_pods']}

### Deployments
"""

    for dep in state['deployments']:
        report += f"- **{dep['name']}:** {dep['ready_replicas']}/{dep['replicas']} ready\n"

    report += f"""
## Metrics Analysis

### CPU Usage
- **Average:** {metrics['cpu']['average_cores']:.4f} cores ({metrics['cpu']['utilization_percent']:.1f}% of limit)
- **Range:** {metrics['cpu']['min_cores']:.4f} - {metrics['cpu']['max_cores']:.4f} cores
- **Limit per pod:** {metrics['cpu']['limit_cores']} cores

### Memory Usage
- **Average:** {metrics['memory']['average_mb']:.2f} MB

### Network
- **Receive:** {metrics['network']['receive_bps']:.2f} bytes/sec
- **Transmit:** {metrics['network']['transmit_bps']:.2f} bytes/sec

"""

    if scaling_action:
        report += f"""## Scaling Action

**Action:** {scaling_action['action'].replace('_', ' ').title()}
**Deployment:** {scaling_action['deployment']}
**Previous Replicas:** {scaling_action['previous_replicas']}
**New Replicas:** {scaling_action['new_replicas']}
**Change:** {scaling_action['change']:+d}
**Reason:** {scaling_action['reason']}
**Timestamp:** {scaling_action['timestamp']}
"""

    report += "\n## Recommendation\n\n"

    if metrics['analysis']['cpu_very_high']:
        report += "URGENT: CPU usage is very high (>90%). Immediate scaling recommended."
    elif metrics['analysis']['cpu_high']:
        report += "ACTION: CPU usage is high (>75%). Scaling up recommended."
    elif metrics['cpu']['utilization_percent'] < 30:
        report += "OPTIMIZE: CPU usage is low (<30%). Consider scaling down to save resources."
    else:
        report += "STABLE: System is operating within normal parameters."

    return report
