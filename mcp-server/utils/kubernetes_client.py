"""
Kubernetes client utilities for ClaudeScale
"""
from kubernetes import client, config
from kubernetes.client.rest import ApiException
from typing import Dict, List, Optional


class KubernetesClient:
    """
    Wrapper around Kubernetes Python client
    """

    def __init__(self, namespace: str = "claudescale", in_cluster: bool = False):
        """
        Initialize Kubernetes client

        Args:
            namespace: Kubernetes namespace to operate in
            in_cluster: Whether running inside a Kubernetes cluster
        """
        self.namespace = namespace

        if in_cluster:
            config.load_incluster_config()
        else:
            config.load_kube_config()

        self.apps_v1 = client.AppsV1Api()
        self.core_v1 = client.CoreV1Api()
        self.autoscaling_v1 = client.AutoscalingV1Api()

    def get_deployment(self, name: str) -> Optional[Dict]:
        """
        Get deployment information

        Args:
            name: Deployment name

        Returns:
            Deployment info dict or None if not found
        """
        try:
            deployment = self.apps_v1.read_namespaced_deployment(
                name=name,
                namespace=self.namespace
            )

            return {
                "name": deployment.metadata.name,
                "namespace": deployment.metadata.namespace,
                "replicas": deployment.spec.replicas,
                "ready_replicas": deployment.status.ready_replicas or 0,
                "available_replicas": deployment.status.available_replicas or 0,
                "updated_replicas": deployment.status.updated_replicas or 0,
                "labels": deployment.metadata.labels,
                "selector": deployment.spec.selector.match_labels,
                "creation_timestamp": deployment.metadata.creation_timestamp.isoformat()
            }
        except ApiException as e:
            if e.status == 404:
                return None
            raise

    def list_deployments(self) -> List[Dict]:
        """
        List all deployments in namespace

        Returns:
            List of deployment info dicts
        """
        deployments = self.apps_v1.list_namespaced_deployment(
            namespace=self.namespace
        )

        result = []
        for dep in deployments.items:
            result.append({
                "name": dep.metadata.name,
                "replicas": dep.spec.replicas,
                "ready_replicas": dep.status.ready_replicas or 0,
                "available_replicas": dep.status.available_replicas or 0
            })

        return result

    def scale_deployment(self, name: str, replicas: int) -> Dict:
        """
        Scale a deployment to specified number of replicas

        Args:
            name: Deployment name
            replicas: Desired number of replicas

        Returns:
            Updated deployment info
        """
        body = {"spec": {"replicas": replicas}}

        self.apps_v1.patch_namespaced_deployment_scale(
            name=name,
            namespace=self.namespace,
            body=body
        )

        return self.get_deployment(name)

    def get_pods(self, deployment_name: str) -> List[Dict]:
        """
        Get pods for a deployment

        Args:
            deployment_name: Deployment name

        Returns:
            List of pod info dicts
        """
        deployment = self.get_deployment(deployment_name)
        if not deployment:
            return []

        label_selector = ",".join([f"{k}={v}" for k, v in deployment["selector"].items()])
        pods = self.core_v1.list_namespaced_pod(
            namespace=self.namespace,
            label_selector=label_selector
        )

        result = []
        for pod in pods.items:
            result.append({
                "name": pod.metadata.name,
                "status": pod.status.phase,
                "ready": all(c.ready for c in pod.status.container_statuses) if pod.status.container_statuses else False,
                "restarts": sum(c.restart_count for c in pod.status.container_statuses) if pod.status.container_statuses else 0,
                "node": pod.spec.node_name,
                "ip": pod.status.pod_ip
            })

        return result
