# Security Policy

## Versiones soportadas

| Versión | Soportada |
|---------|-----------|
| 1.0.x   | Sí        |
| < 1.0   | No        |

## Reportar una vulnerabilidad

**No abrir issues públicos en GitHub para vulnerabilidades de seguridad.**

Seguir el proceso de responsible disclosure:

1. Describir el problema con detalle (tipo, impacto, pasos para reproducir)
2. Incluir proof-of-concept si aplica
3. Dar un plazo razonable para el fix antes de publicar
4. Se dará crédito al reportador (salvo que prefiera anonimato)

## Consideraciones de seguridad conocidas

### Entorno de desarrollo (actual)
- MCP Server corre fuera del cluster usando kubeconfig personal (admin)
- Sin Network Policies entre pods
- Audit log en `/tmp` (volátil)

### Para producción
- Desplegar MCP Server como Pod dentro del cluster con ServiceAccount
- Implementar Network Policies
- Audit log en PersistentVolume o sistema de logging externo
- Cambiar credenciales de Grafana (actualmente `admin/admin`)

## Referencia

Ver [docs/SECURITY.md](docs/SECURITY.md) para la guía completa de seguridad.
