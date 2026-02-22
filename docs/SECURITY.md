# ClaudeScale Security

## RBAC (Role-Based Access Control)

ClaudeScale follows the **principle of least privilege**.

### ServiceAccount: `claudescale-sa`

Identity used by the MCP server when running in Kubernetes.

### Role: `claudescale-scaler-role`

**Permissions granted:**
- ✅ `get`, `list`, `watch` deployments (read-only)
- ✅ `get` deployment scale (read current replica count)
- ✅ `update`, `patch` deployment scale (change replica count)
- ✅ `get`, `list` pods (verify state)

**Permissions NOT granted:**
- ❌ Cannot delete deployments
- ❌ Cannot create new deployments
- ❌ Cannot modify deployment specs (only scale)
- ❌ Cannot access other namespaces
- ❌ Cannot read secrets
- ❌ Cannot modify RBAC itself

### Scope

All permissions are limited to the `claudescale` namespace only.

## Network Security

### Services Type

All services use `ClusterIP` (internal only):
- Prometheus: `prometheus:9090` (internal)
- Grafana: `grafana:3000` (internal)
- Demo app: `demo-app:80` (internal)

No external load balancers or public IPs.

### Access Method

External access via `kubectl port-forward` only (requires authenticated kubectl access).

## Environment Variables

Sensitive data stored in:
- `.env` file (local development, **never committed**)
- Kubernetes Secrets (cluster deployment)

See `.env.example` for required variables.

## Best Practices Applied

1. ✅ **Minimal permissions** (RBAC)
2. ✅ **Namespace isolation**
3. ✅ **No secrets in code**
4. ✅ **Service accounts** (not default)
5. ✅ **ClusterIP** services (no external exposure)
6. ✅ **Resource limits** on all pods
7. ✅ **Audit logging** of all scaling operations

## Security Checklist

- [ ] Never commit `.env` files
- [ ] Always use ServiceAccount in production
- [ ] Review RBAC permissions regularly
- [ ] Scan Docker images for vulnerabilities
- [ ] Use network policies (optional, advanced)
- [ ] Enable audit logging in production
- [ ] Rotate credentials regularly

## Vulnerability Scanning
```bash
# Scan Docker images
docker scan claudescale-mcp:latest

# Check for hardcoded secrets
git secrets --scan
```

---

**Security is not a feature, it's a requirement.**
