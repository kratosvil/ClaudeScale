#!/usr/bin/env python3
"""
Manual testing of MCP tools

This script tests each MCP tool individually
without running the full MCP server.

Usage:
    python3 scripts/manual-test-tools.py
    python3 scripts/manual-test-tools.py --no-scale   # skip scaling test
"""
import sys
import asyncio
import json
import argparse

sys.path.insert(0, 'mcp-server')

from utils.kubernetes_client import KubernetesClient
from utils.prometheus_client import PrometheusClient
from tools.scaling_tools import (
    get_current_state,
    get_metrics,
    scale_deployment,
    generate_report
)


async def test_get_current_state(k8s):
    """Test Tool 1: get_current_state"""
    print("\n" + "="*60)
    print("TEST 1: get_current_state()")
    print("="*60)

    result = await get_current_state(k8s)
    print(json.dumps(result, indent=2, default=str))
    return result


async def test_get_metrics(prom):
    """Test Tool 2: get_metrics"""
    print("\n" + "="*60)
    print("TEST 2: get_metrics()")
    print("="*60)
    print("Note: Requires Prometheus on localhost:9090")
    print("")

    try:
        result = await get_metrics(
            prom,
            namespace="claudescale",
            deployment="demo-app"
        )
        print(json.dumps(result, indent=2, default=str))
        return result
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure Prometheus port-forward is running:")
        print("  kubectl port-forward -n claudescale svc/prometheus 9090:9090")
        return None


async def test_scale_deployment(k8s):
    """Test Tool 3: scale_deployment"""
    print("\n" + "="*60)
    print("TEST 3: scale_deployment()")
    print("="*60)

    current = k8s.get_deployment("demo-app")
    current_replicas = current["replicas"]
    test_replicas = 3

    print(f"Current replicas: {current_replicas}")
    print(f"Scaling to: {test_replicas}")
    print("")

    result = await scale_deployment(
        k8s,
        deployment="demo-app",
        replicas=test_replicas,
        reason="Manual test via test script"
    )
    print(json.dumps(result, indent=2, default=str))

    # Restore original
    if result["success"] and result.get("action") != "no_change":
        print(f"\nRestoring to {current_replicas} replicas...")
        await asyncio.sleep(2)
        restore = await scale_deployment(
            k8s,
            deployment="demo-app",
            replicas=current_replicas,
            reason="Restore after test"
        )
        print(f"Restored to {current_replicas} replicas")

    return result


async def test_generate_report(k8s, prom):
    """Test Tool 4: generate_report"""
    print("\n" + "="*60)
    print("TEST 4: generate_report()")
    print("="*60)

    state = await get_current_state(k8s)

    try:
        metrics = await get_metrics(prom, namespace="claudescale", deployment="demo-app")
    except Exception:
        print("Could not get Prometheus metrics, skipping metrics section")
        metrics = None

    if state and metrics:
        report = await generate_report(state, metrics)
        print(report)

        report_path = "/tmp/claudescale-test-report.md"
        with open(report_path, "w") as f:
            f.write(report)
        print(f"\nReport saved to: {report_path}")
    else:
        print("Could not generate full report (missing metrics)")


async def main(skip_scale=False):
    """Run all tests"""
    print("ClaudeScale MCP Tools - Manual Testing")
    print("=" * 60)

    k8s = KubernetesClient(namespace="claudescale", in_cluster=False)
    prom = PrometheusClient(url="http://localhost:9090")

    state = await test_get_current_state(k8s)
    await asyncio.sleep(1)

    metrics = await test_get_metrics(prom)
    await asyncio.sleep(1)

    if not skip_scale:
        await test_scale_deployment(k8s)
        await asyncio.sleep(1)

    await test_generate_report(k8s, prom)

    print("\n" + "="*60)
    print("ALL MANUAL TESTS COMPLETE")
    print("="*60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-scale", action="store_true", help="Skip scaling test")
    args = parser.parse_args()

    asyncio.run(main(skip_scale=args.no_scale))
