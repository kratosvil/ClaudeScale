# ClaudeScale 🚀

> Intelligent Kubernetes autoscaling powered by Claude AI

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Kubernetes](https://img.shields.io/badge/kubernetes-1.28+-326CE5.svg)](https://kubernetes.io/)

## 🎯 What is ClaudeScale?

ClaudeScale is an AI-powered Kubernetes autoscaler that uses Claude (Anthropic's LLM) to make intelligent scaling decisions based on real-time metrics from Prometheus. Unlike traditional autoscalers that use simple threshold rules, ClaudeScale analyzes patterns, understands context, and makes human-like decisions about when and how to scale your applications.

## ✨ Features

- 🤖 **AI-Driven Decisions**: Claude analyzes metrics and makes intelligent scaling choices
- 📊 **Real-time Monitoring**: Prometheus integration for accurate metrics collection
- 📈 **Beautiful Dashboards**: Grafana visualization of scaling events and metrics
- 🔐 **Secure by Design**: RBAC-based permissions, minimal attack surface
- 📝 **Audit Trail**: Every scaling decision is logged and explained
- 🛠️ **MCP Protocol**: Built on Model Context Protocol for extensibility

## 🏗️ Architecture
```
┌─────────────┐
│   Claude AI │  ← Makes scaling decisions
└──────┬──────┘
       │
       │ MCP Protocol
       │
┌──────▼──────────┐
│   MCP Server    │  ← Python FastMCP
│  (ClaudeScale)  │
└──────┬──────────┘
       │
       ├─────────────┐
       │             │
┌──────▼──────┐  ┌──▼────────────┐
│ Kubernetes  │  │  Prometheus   │
│   API       │  │   Metrics     │
└─────────────┘  └───────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Kubernetes cluster (Minikube/Docker Desktop)
- Python 3.11+
- kubectl
- Docker

### Installation
```bash
# Clone the repository
git clone https://github.com/kratosvil/claudescale.git
cd claudescale

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Linux/Mac
# venv\Scripts\activate   # On Windows

# Install dependencies
pip install -r requirements.txt

# Run setup script
./scripts/setup.sh
```

## 📖 Documentation

- [Architecture Overview](docs/ARCHITECTURE.md)
- [Setup Guide](docs/SETUP.md)
- [Usage Examples](docs/USAGE_EXAMPLES.md)
- [Development Roadmap](docs/ROADMAP.md)

## 🛠️ Tech Stack

- **AI/ML**: Claude (Anthropic), MCP Protocol
- **Container Orchestration**: Kubernetes
- **Monitoring**: Prometheus, Grafana
- **Backend**: Python 3.11+, FastMCP
- **IaC**: Kubernetes YAML manifests

## 📊 Project Status

🚧 **Under Active Development**

See [ROADMAP.md](docs/ROADMAP.md) for current progress.

## 🤝 Contributing

Contributions are welcome! This is a learning project showcasing DevOps + AI integration.

## 📝 License

MIT License - see [LICENSE](LICENSE) for details

## 👤 Author

**Kratosvil**
- DevOps Engineer with 8+ years of experience
- Specializing in AWS, Terraform, Kubernetes, and AI/DevOps integration

## 🙏 Acknowledgments

- Anthropic for Claude and the MCP protocol
- CNCF for Kubernetes and Prometheus
- The open-source community

---

**Built by Kratosvil**
