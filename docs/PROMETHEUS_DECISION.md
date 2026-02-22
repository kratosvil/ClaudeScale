# Prometheus Deployment Decision

## Options Evaluated

### Option 1: Helm (kube-prometheus-stack)
**Pros:**
- ✅ One command install
- ✅ Includes Grafana, Alertmanager
- ✅ Pre-configured dashboards
- ✅ Production-ready defaults

**Cons:**
- ❌ Less control over configuration
- ❌ Harder to understand what's happening
- ❌ Abstracts away learning

### Option 2: Manual Manifests
**Pros:**
- ✅ Full control
- ✅ Learn every component
- ✅ Understand what you're deploying
- ✅ Better for portfolio/learning

**Cons:**
- ❌ More configuration needed
- ❌ More time to set up

## Decision: Manual Manifests ✅

**Reason:** This is a learning project. Understanding each component is more valuable than quick setup.

We'll create:
1. ConfigMap for Prometheus configuration
2. Deployment for Prometheus server
3. Service to access Prometheus
4. PersistentVolumeClaim for data storage (optional for local)

## Installation Method

Using `kubectl apply -f` with custom YAML manifests.
