"""
Configuration for ClaudeScale MCP Server
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """

    # Kubernetes Configuration
    KUBERNETES_IN_CLUSTER: bool = False  # Set to True when running inside K8s
    KUBECONFIG_PATH: Optional[str] = None  # Path to kubeconfig (for local dev)
    KUBERNETES_NAMESPACE: str = "claudescale"

    # Prometheus Configuration
    PROMETHEUS_URL: str = "http://prometheus:9090"  # Internal cluster URL
    PROMETHEUS_LOCAL_URL: str = "http://localhost:9090"  # For local development

    # Scaling Configuration
    MIN_REPLICAS: int = 2
    MAX_REPLICAS: int = 5
    DEFAULT_DEPLOYMENT: str = "demo-app"

    # MCP Server Configuration
    SERVER_NAME: str = "claudescale-mcp"
    SERVER_VERSION: str = "1.0.0"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()
