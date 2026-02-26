# ClaudeScale — Security Guide

## Modelo de seguridad

ClaudeScale expone capacidades de infraestructura a un LLM. El modelo de amenaza principal es:
**el LLM puede ser manipulado, alucinado o simplemente equivocado**. Las defensas no están dirigidas a atacantes externos, sino a contener los efectos de decisiones incorrectas del modelo.

---

## Capas de defensa

```
┌──────────────────────────────────────────────────────┐
│ Capa 1 — Límites hard-coded                         │
│   MIN_REPLICAS=2  MAX_REPLICAS=5                    │
│   El LLM no puede ignorar estos valores             │
└──────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────┐
│ Capa 2 — Guardrails en código (guardrails.py)       │
│   Cooldown 90s (up) / 180s (down)                   │
│   Scale-down: máx 1 réplica por acción              │
│   Scale-down: CPU < 40% obligatorio                 │
│   Scale-down: reason explícito obligatorio          │
└──────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────┐
│ Capa 3 — Snapshot pre-acción (rollback)             │
│   Estado guardado en /tmp/claudescale-snapshot.json │
│   Antes de CADA scaling action                      │
│   Permite recuperación en segundos                  │
└──────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────┐
│ Capa 4 — Audit log persistente                      │
│   /tmp/claudescale-audit.log                        │
│   Cada acción: timestamp, deployment, replicas,     │
│   reason, resultado                                 │
└──────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────┐
│ Capa 5 — RBAC Kubernetes (permisos mínimos)         │
│   ServiceAccount: claudescale-sa                    │
│   Solo: get/list/watch deployments                  │
│       + patch deployments/scale                     │
│       + get/list pods                               │
│   Sin acceso a: secrets, configmaps, otros NS       │
└──────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────┐
│ Capa 6 — Aislamiento de red                         │
│   Todos los servicios: ClusterIP (interno)          │
│   Sin LoadBalancers ni NodePorts expuestos          │
│   Acceso externo solo via port-forward autenticado  │
└──────────────────────────────────────────────────────┘
```

---

## Guardrails del LLM (mcp-server/guardrails.py)

### 1. Cooldown entre acciones

```
Scale-up:   mínimo 90 segundos entre operaciones
Scale-down: mínimo 180 segundos entre operaciones
```

Previene que el LLM ejecute múltiples escalados rápidos en secuencia, ya sea por error de razonamiento o por instrucciones maliciosas en el prompt.

### 2. Protección scale-down

Antes de reducir réplicas, se verifican 3 condiciones:

| Condición | Valor | Bloqueado si |
|-----------|-------|--------------|
| `reason` | obligatorio | vacío o "No reason provided" |
| `cpu_utilization_pct` | < 40% | CPU >= 40% |
| Reducción máxima | 1 réplica por acción | se piden > 1 réplica menos |

### 3. Snapshot pre-acción

Antes de ejecutar cualquier scaling:
1. Se guarda el estado actual en `/tmp/claudescale-snapshot.json`
2. El response incluye `rollback_info` con instrucciones exactas para revertir

**Rollback manual:**
```bash
# Ver último snapshot
cat /tmp/claudescale-snapshot.json

# Revertir (ejemplo: demo-app tenía 3 réplicas)
kubectl scale deployment demo-app -n claudescale --replicas=3
```

### 4. Audit log

Cada acción escribe en `/tmp/claudescale-audit.log`:
```json
{
  "timestamp": "2026-02-26T15:30:00",
  "event": "scale_executed",
  "deployment": "demo-app",
  "namespace": "claudescale",
  "previous_replicas": 2,
  "new_replicas": 4,
  "action": "scaled_up",
  "reason": "CPU al 87%, añadiendo capacidad"
}
```

Eventos registrados:
- `scale_executed` — scaling completado
- `scale_blocked_cooldown` — bloqueado por cooldown
- `scale_blocked_guard` — bloqueado por guardrail de scale-down

---

## RBAC — Permisos del ServiceAccount

```yaml
# Lo que claudescale-sa PUEDE hacer:
- get, list, watch → deployments
- get, patch       → deployments/scale
- get, list        → pods

# Lo que claudescale-sa NO PUEDE hacer:
- delete (ningún recurso)
- create (ningún recurso)
- acceder a secrets
- acceder a configmaps
- acceder a otros namespaces
- modificar RBAC
```

**Peor caso de compromiso:** El LLM solo puede cambiar el número de réplicas de deployments existentes en el namespace `claudescale`, dentro del rango 2-5.

---

## Credenciales y secretos

| Item | Estado | Dónde está |
|------|--------|-----------|
| Grafana admin password | K8s Secret | `grafana-credentials` en namespace `claudescale` |
| `.env` configuración | 600 permisos | local, en `.gitignore` |
| API keys | No existen | No se usan |
| kubeconfig | No en repo | `~/.kube/config` del SO |

**Para producción — cambiar Grafana password:**
```bash
kubectl create secret generic grafana-credentials \
  --from-literal=admin-user=admin \
  --from-literal=admin-password=TU_PASSWORD_SEGURO \
  --namespace=claudescale \
  --dry-run=client -o yaml | kubectl apply -f -
```

---

## Procedimiento de recuperación rápida

### Escenario: LLM escaló incorrectamente

```bash
# 1. Ver qué hizo (audit log)
tail -20 /tmp/claudescale-audit.log | python3 -m json.tool

# 2. Ver el estado previo (snapshot)
cat /tmp/claudescale-snapshot.json

# 3. Revertir
kubectl scale deployment demo-app -n claudescale --replicas=<previous_replicas>

# 4. Verificar
kubectl get pods -n claudescale -l app=demo-app
```

### Escenario: MCP Server bloqueado o en loop

```bash
# Parar el MCP server
pkill -f "mcp-server/server.py"

# El cluster sigue funcionando (MCP es externo)
# HPA continúa operando como fallback
kubectl get hpa -n claudescale
```

### Escenario: Todo el cluster en mal estado

```bash
# Resetear a estado conocido
kubectl scale deployment demo-app -n claudescale --replicas=2
kubectl scale deployment prometheus -n claudescale --replicas=1
kubectl scale deployment grafana -n claudescale --replicas=1

# Verificar
kubectl get pods -n claudescale
```

---

## Limitaciones conocidas (entorno de desarrollo)

| Limitación | Impacto | Mitigación |
|------------|---------|-----------|
| MCP Server fuera del cluster | Usa kubeconfig admin | Solo en desarrollo local |
| Sin Network Policies | Pods pueden comunicarse entre sí | Namespace aislado es suficiente para dev |
| Sin TLS en MCP | stdio local, no HTTP | No expuesto a red |
| audit.log en /tmp | Se pierde al reiniciar | Para producción: usar PersistentVolume |

---

## Mejoras para producción

1. **MCP Server dentro del cluster** como Pod con ServiceAccount (no kubeconfig)
2. **Network Policies** para aislar tráfico entre pods
3. **Pod Security Context** — non-root, readOnlyRootFilesystem
4. **Audit log en PersistentVolume** o servicio de logging externo
5. **Alertas** en Prometheus/Grafana sobre eventos de scaling inesperados
6. **Rate limiting adicional** en la capa de API de Kubernetes
