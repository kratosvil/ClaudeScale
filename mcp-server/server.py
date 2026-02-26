#!/usr/bin/env python3
"""
ClaudeScale MCP Server

This MCP server exposes 4 tools to Claude AI for intelligent Kubernetes scaling:
1. get_current_state - View current deployment status
2. get_metrics       - Query Prometheus for CPU/Memory/Network metrics
3. scale_deployment  - Scale a deployment up or down
4. generate_report   - Create a markdown report of actions

Usage:
    python server.py

Configuration:
    Set environment variables or create .env file:
    - PROMETHEUS_URL (default: http://localhost:9090)
    - KUBERNETES_NAMESPACE (default: claudescale)
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastmcp import FastMCP
from config import settings
from utils.kubernetes_client import KubernetesClient
from utils.prometheus_client import PrometheusClient
from tools.scaling_tools import (
    get_current_state,
    get_metrics,
    scale_deployment,
    generate_report
)
from typing import Dict, Any, Optional

# Initialize MCP server
mcp = FastMCP(settings.SERVER_NAME)

# Initialize clients
k8s_client = KubernetesClient(
    namespace=settings.KUBERNETES_NAMESPACE,
    in_cluster=settings.KUBERNETES_IN_CLUSTER
)

prom_url = settings.PROMETHEUS_LOCAL_URL if not settings.KUBERNETES_IN_CLUSTER else settings.PROMETHEUS_URL
prom_client = PrometheusClient(url=prom_url)


@mcp.tool()
async def claudescale_get_current_state(namespace: str = "claudescale") -> Dict[str, Any]:
    """
    Get current state of all deployments in the namespace.

    Returns information about:
    - All deployments and replica counts
    - Pod readiness
    - Overall health

    Args:
        namespace: Kubernetes namespace (default: claudescale)

    Returns:
        Dict with deployment state
    """
    return await get_current_state(k8s_client, namespace)


@mcp.tool()
async def claudescale_get_metrics(
    namespace: str = "claudescale",
    deployment: str = "demo-app",
    lookback_minutes: int = 5
) -> Dict[str, Any]:
    """
    Get metrics from Prometheus for analysis.

    Returns:
    - CPU usage (average, min, max, utilization %)
    - Memory usage
    - Network traffic
    - Analysis and recommendations

    Args:
        namespace: Kubernetes namespace
        deployment: Deployment name
        lookback_minutes: Minutes of history to consider

    Returns:
        Dict with comprehensive metrics
    """
    return await get_metrics(
        prom_client,
        namespace=namespace,
        deployment=deployment,
        lookback_minutes=lookback_minutes
    )


@mcp.tool()
async def claudescale_scale_deployment(
    deployment: str,
    replicas: int,
    namespace: str = "claudescale",
    reason: Optional[str] = None
) -> Dict[str, Any]:
    """
    Scale a deployment to the specified number of replicas.

    Constraints:
    - Minimum: 2 replicas
    - Maximum: 5 replicas

    Args:
        deployment: Deployment name (e.g., "demo-app")
        replicas: Desired number of replicas (2-5)
        namespace: Kubernetes namespace
        reason: Explanation for why scaling is needed

    Returns:
        Dict with scaling result
    """
    return await scale_deployment(
        k8s_client,
        deployment=deployment,
        replicas=replicas,
        namespace=namespace,
        reason=reason
    )


@mcp.tool()
async def claudescale_generate_report(
    include_state: bool = True,
    include_metrics: bool = True,
    deployment: str = "demo-app",
    namespace: str = "claudescale"
) -> str:
    """
    Generate a comprehensive markdown report of current system state.

    The report includes:
    - Current deployment status
    - Metrics analysis
    - Recommendations

    Args:
        include_state: Include current state in report
        include_metrics: Include metrics in report
        deployment: Deployment to analyze
        namespace: Kubernetes namespace

    Returns:
        Markdown formatted report
    """
    state = None
    metrics = None

    if include_state:
        state = await get_current_state(k8s_client, namespace)

    if include_metrics:
        metrics = await get_metrics(prom_client, namespace, deployment)

    if state and metrics:
        return await generate_report(state, metrics)
    elif state:
        return f"# Current State\n\n{state}"
    elif metrics:
        return f"# Metrics\n\n{metrics}"
    else:
        return "# No data available"


if __name__ == "__main__":
    print(f"Starting {settings.SERVER_NAME} v{settings.SERVER_VERSION}")
    print(f"Namespace: {settings.KUBERNETES_NAMESPACE}")
    print(f"Prometheus: {prom_url}")
    print("")
    print("Tools:")
    print("  1. claudescale_get_current_state")
    print("  2. claudescale_get_metrics")
    print("  3. claudescale_scale_deployment")
    print("  4. claudescale_generate_report")
    print("")

    mcp.run()
