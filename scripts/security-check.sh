#!/bin/bash
# ClaudeScale — Security Audit Script

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PASS=0
WARN=0
FAIL=0

pass() { echo "  PASS  $1"; PASS=$((PASS + 1)); }
warn() { echo "  WARN  $1"; WARN=$((WARN + 1)); }
fail() { echo "  FAIL  $1"; FAIL=$((FAIL + 1)); }

echo "ClaudeScale Security Audit"
echo "=========================="
echo ""

# ── 1. RBAC ──────────────────────────────────────────────────────────────────
echo "1. RBAC"

kubectl get sa claudescale-sa -n claudescale > /dev/null 2>&1 \
  && pass "ServiceAccount claudescale-sa existe" \
  || fail "ServiceAccount claudescale-sa NO encontrado"

kubectl get role claudescale-scaler-role -n claudescale > /dev/null 2>&1 \
  && pass "Role claudescale-scaler-role existe" \
  || fail "Role NO encontrado"

kubectl get rolebinding claudescale-scaler-binding -n claudescale > /dev/null 2>&1 \
  && pass "RoleBinding existe" \
  || fail "RoleBinding NO encontrado"

# Verificar que delete no está en los verbos
VERBS=$(kubectl get role claudescale-scaler-role -n claudescale -o jsonpath='{.rules[*].verbs}' 2>/dev/null)
if echo "$VERBS" | grep -q "delete"; then
  fail "Role contiene verbo 'delete' — revisar permisos"
else
  pass "Role no contiene 'delete' (mínimo privilegio)"
fi

echo ""

# ── 2. Secrets ────────────────────────────────────────────────────────────────
echo "2. Secrets"

kubectl get secret grafana-credentials -n claudescale > /dev/null 2>&1 \
  && pass "Secret grafana-credentials existe (password no en plain text)" \
  || fail "Secret grafana-credentials NO encontrado"

# Verificar que grafana-deployment.yaml ya no tiene password hardcoded
if grep -q "value: \"admin\"" "$PROJECT_DIR/k8s-manifests/grafana-deployment.yaml" 2>/dev/null; then
  fail "grafana-deployment.yaml tiene credenciales en plain text"
else
  pass "grafana-deployment.yaml usa secretKeyRef"
fi

# Verificar .env no está en git
if git -C "$PROJECT_DIR" ls-files --error-unmatch .env > /dev/null 2>&1; then
  fail ".env está trackeado en git"
else
  pass ".env NO está en git"
fi

# Verificar permisos .env
if [ -f "$PROJECT_DIR/.env" ]; then
  PERMS=$(stat -c '%a' "$PROJECT_DIR/.env")
  if [ "$PERMS" = "600" ]; then
    pass ".env permisos 600 (solo propietario)"
  else
    warn ".env permisos $PERMS (recomendado: 600)"
  fi
fi

# Buscar secrets hardcoded en código Python
if grep -rn --include="*.py" -iE "password\s*=\s*['\"][^'\"]{4,}" \
    "$PROJECT_DIR/mcp-server/" 2>/dev/null | grep -v "test\|example\|comment"; then
  warn "Posibles credentials hardcoded en código Python — revisar manualmente"
else
  pass "Sin credentials hardcoded en código Python"
fi

echo ""

# ── 3. Red ───────────────────────────────────────────────────────────────────
echo "3. Red"

LB=$(kubectl get svc -n claudescale -o jsonpath='{.items[?(@.spec.type=="LoadBalancer")].metadata.name}' 2>/dev/null)
if [ -z "$LB" ]; then
  pass "Sin servicios LoadBalancer (solo ClusterIP)"
else
  warn "Servicios LoadBalancer encontrados: $LB"
fi

NP=$(kubectl get svc -n claudescale -o jsonpath='{.items[?(@.spec.type=="NodePort")].metadata.name}' 2>/dev/null)
if [ -z "$NP" ]; then
  pass "Sin servicios NodePort"
else
  warn "Servicios NodePort encontrados: $NP"
fi

echo ""

# ── 4. Guardrails del código ──────────────────────────────────────────────────
echo "4. Guardrails MCP"

if [ -f "$PROJECT_DIR/mcp-server/guardrails.py" ]; then
  pass "guardrails.py existe"
else
  fail "guardrails.py NO encontrado"
fi

if grep -q "COOLDOWN_SECONDS" "$PROJECT_DIR/mcp-server/guardrails.py" 2>/dev/null; then
  pass "Cooldown configurado en guardrails"
else
  fail "Sin cooldown en guardrails"
fi

if grep -q "validate_scaledown" "$PROJECT_DIR/mcp-server/guardrails.py" 2>/dev/null; then
  pass "Scale-down guard implementado"
else
  fail "Sin scale-down guard"
fi

if grep -q "save_snapshot" "$PROJECT_DIR/mcp-server/guardrails.py" 2>/dev/null; then
  pass "Snapshot pre-acción implementado (rollback disponible)"
else
  fail "Sin snapshot/rollback"
fi

if grep -q "audit_log" "$PROJECT_DIR/mcp-server/tools/scaling_tools.py" 2>/dev/null; then
  pass "Audit log integrado en scaling_tools"
else
  fail "Sin audit log en scaling_tools"
fi

echo ""

# ── 5. Límites de réplicas ────────────────────────────────────────────────────
echo "5. Límites de réplicas"

HPA_MAX=$(kubectl get hpa demo-app-hpa -n claudescale -o jsonpath='{.spec.maxReplicas}' 2>/dev/null)
if [ -n "$HPA_MAX" ] && [ "$HPA_MAX" -le 5 ]; then
  pass "HPA max replicas: $HPA_MAX (dentro del límite)"
else
  warn "HPA max replicas: ${HPA_MAX:-no disponible}"
fi

if grep -q "MAX_REPLICAS = 5" "$PROJECT_DIR/mcp-server/tools/scaling_tools.py" 2>/dev/null; then
  pass "MAX_REPLICAS=5 en scaling_tools"
else
  warn "Verificar MAX_REPLICAS en scaling_tools.py"
fi

if grep -q "MIN_REPLICAS = 2" "$PROJECT_DIR/mcp-server/tools/scaling_tools.py" 2>/dev/null; then
  pass "MIN_REPLICAS=2 en scaling_tools"
else
  warn "Verificar MIN_REPLICAS en scaling_tools.py"
fi

echo ""

# ── 6. Datos sensibles en repo ────────────────────────────────────────────────
echo "6. Datos sensibles"

SENSITIVE=$(git -C "$PROJECT_DIR" log --all --full-history --oneline -- .env 2>/dev/null | head -1)
if [ -n "$SENSITIVE" ]; then
  warn ".env aparece en historial git — considerar git-filter-repo para limpiar"
else
  pass ".env nunca fue commiteado"
fi

# Buscar IPs internas en archivos trackeados
if git -C "$PROJECT_DIR" grep -iE "192\.168\.|10\.\d+\.\d+\.\d+" -- "*.yaml" "*.py" "*.md" 2>/dev/null | grep -v "example\|#\|comment"; then
  warn "IPs privadas encontradas en archivos trackeados — revisar"
else
  pass "Sin IPs privadas hardcoded en archivos trackeados"
fi

echo ""
echo "=================================="
printf "Resultado:  PASS=%d  WARN=%d  FAIL=%d\n" "$PASS" "$WARN" "$FAIL"
echo ""

if [ "$FAIL" -gt 0 ]; then
  echo "ESTADO: CRITICO — corregir los FAIL antes de continuar"
  exit 2
elif [ "$WARN" -gt 0 ]; then
  echo "ESTADO: ADVERTENCIAS — revisar los WARN"
  exit 1
else
  echo "ESTADO: OK — todos los checks pasaron"
  exit 0
fi
