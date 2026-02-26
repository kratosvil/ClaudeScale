"""
Prometheus client utilities for ClaudeScale
"""
from prometheus_api_client import PrometheusConnect
from typing import Dict, List
from datetime import datetime


class PrometheusClient:
    """
    Wrapper around Prometheus API client
    """

    def __init__(self, url: str = "http://localhost:9090"):
        """
        Initialize Prometheus client

        Args:
            url: Prometheus server URL
        """
        self.url = url
        self.client = PrometheusConnect(url=url, disable_ssl=True)

    def query(self, query: str) -> List[Dict]:
        """
        Execute a PromQL query

        Args:
            query: PromQL query string

        Returns:
            List of metric results
        """
        return self.client.custom_query(query=query)

    def get_cpu_usage(self, namespace: str, pod_filter: str = "demo-app.*") -> Dict:
        """
        Get CPU usage for pods

        Args:
            namespace: Kubernetes namespace
            pod_filter: Regex filter for pod names

        Returns:
            Dict with CPU metrics
        """
        query = (
            f'rate(container_cpu_usage_seconds_total{{'
            f'namespace="{namespace}", pod=~"{pod_filter}", cpu="total"}}[5m])'
        )

        result = self.client.custom_query(query=query)

        metrics = []
        for item in result:
            metrics.append({
                "pod": item["metric"].get("pod", "unknown"),
                "value": float(item["value"][1]),
                "timestamp": datetime.fromtimestamp(item["value"][0]).isoformat()
            })

        avg_cpu = sum(m["value"] for m in metrics) / len(metrics) if metrics else 0

        return {
            "query": query,
            "pods": metrics,
            "average_cpu": avg_cpu,
            "count": len(metrics)
        }

    def get_memory_usage(self, namespace: str, pod_filter: str = "demo-app.*") -> Dict:
        """
        Get memory usage for pods

        Args:
            namespace: Kubernetes namespace
            pod_filter: Regex filter for pod names

        Returns:
            Dict with memory metrics
        """
        query = (
            f'container_memory_usage_bytes{{'
            f'namespace="{namespace}", pod=~"{pod_filter}"}}'
        )

        result = self.client.custom_query(query=query)

        metrics = []
        for item in result:
            metrics.append({
                "pod": item["metric"].get("pod", "unknown"),
                "value_bytes": float(item["value"][1]),
                "value_mb": float(item["value"][1]) / 1024 / 1024,
                "timestamp": datetime.fromtimestamp(item["value"][0]).isoformat()
            })

        avg_memory_mb = sum(m["value_mb"] for m in metrics) / len(metrics) if metrics else 0

        return {
            "query": query,
            "pods": metrics,
            "average_memory_mb": avg_memory_mb,
            "count": len(metrics)
        }

    def get_network_traffic(self, namespace: str, pod_filter: str = "demo-app.*") -> Dict:
        """
        Get network traffic for pods

        Args:
            namespace: Kubernetes namespace
            pod_filter: Regex filter for pod names

        Returns:
            Dict with network metrics
        """
        rx_query = (
            f'rate(container_network_receive_bytes_total{{'
            f'namespace="{namespace}", pod=~"{pod_filter}"}}[5m])'
        )
        tx_query = (
            f'rate(container_network_transmit_bytes_total{{'
            f'namespace="{namespace}", pod=~"{pod_filter}"}}[5m])'
        )

        rx_result = self.client.custom_query(query=rx_query)
        tx_result = self.client.custom_query(query=tx_query)

        return {
            "receive_bps": sum(float(item["value"][1]) for item in rx_result) if rx_result else 0,
            "transmit_bps": sum(float(item["value"][1]) for item in tx_result) if tx_result else 0
        }
