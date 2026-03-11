# Estrategia de Versionado y Docker para Totem API

## 🏷️ Estrategia de Versionado de Imágenes Docker

### Convención de Tags

Utilizamos una estrategia semántica de versionado combinada con el flujo de Git:

```bash
# Formato: [environment]-[version]-[commit-sha]
ghcr.io/username/totem-api:main-latest
ghcr.io/username/totem-api:develop-latest
ghcr.io/username/totem-api:main-a1b2c3d
ghcr.io/username/totem-api:develop-a1b2c3d
ghcr.io/username/totem-api:v1.0.0
ghcr.io/username/totem-api:v1.1.0-beta
```

### Tipos de Tags

#### 1. **Branch Tags**
- `main-latest`: Última versión del branch main (producción)
- `develop-latest`: Última versión del branch develop (staging)

#### 2. **Commit SHA Tags**
- `main-a1b2c3d`: Commit específico del branch main
- `develop-a1b2c3d`: Commit específico del branch develop

#### 3. **Version Tags**
- `v1.0.0`: Release oficial
- `v1.1.0-beta`: Beta release
- `v1.2.0-rc1`: Release candidate

## 🔄 Flujo de Deploy

### Development → Staging → Production

```mermaid
graph LR
    A[Developer Push] --> B[CI/CD Pipeline]
    B --> C{Branch?}
    C -->|develop| D[Build & Test]
    C -->|main| E[Build & Test]
    D --> F[Deploy to Staging]
    E --> G[Deploy to Production]
    F --> H[Health Check]
    G --> I[Health Check]
    H --> J[Manual Promote]
    J --> G
```

### Proceso Detallado

#### 1. **Development Flow**
```bash
# Developer hace push a develop
git checkout develop
git commit -m "feat: add new endpoint"
git push origin develop

# CI/CD Pipeline:
# - Build imagen: develop-latest, develop-a1b2c3d
# - Run tests
# - Deploy a staging
# - Health check
```

#### 2. **Production Flow**
```bash
# Merge a main (con pull request)
git checkout main
git merge develop
git push origin main

# CI/CD Pipeline:
# - Build imagen: main-latest, main-a1b2c3d
# - Run tests + security scan
# - Deploy a producción
# - Health check
```

## 📦 Gestión de Imágenes

### Lifecycle Management

#### Retención de Imágenes
```yaml
# Política de retención (GitHub Container Registry)
main-latest:        Mantener siempre (últimas 10)
main-*.sha:         Mantener 30 días
develop-latest:      Mantener siempre (últimas 5)
develop-*.sha:      Mantener 7 días
v*.*.*:             Mantener siempre (releases)
```

#### Limpieza Automática
```bash
# Script de limpieza (ejecutado semanalmente)
#!/bin/bash
# Eliminar imágenes antiguas de develop
docker images --format "table {{.Repository}}:{{.Tag}}\t{{.CreatedAt}}" | \
  grep "develop-" | \
  awk '$2 !~ /latest$/ && $3 < "'$(date -d '7 days ago' '+%Y-%m-%d')'" {print $1}' | \
  xargs -r docker rmi
```

### Optimización de Build

#### Multi-stage Build Strategy
```dockerfile
# Stage 1: Builder (con herramientas de compilación)
FROM python:3.11-slim as builder
# Instalar dependencias y compilar

# Stage 2: Runtime (solo lo necesario)
FROM python:3.11-slim as runtime
# Copiar solo lo necesario del builder
```

#### Layer Caching
```dockerfile
# Orden óptimo para caché
1. Copiar requirements.txt
2. Instalar dependencias (cambia poco)
3. Copiar código fuente (cambia seguido)
4. Copiar configuración específica
```

## 🚀 Estrategia de Deploy

### Blue-Green Deploy (Producción)

```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  api-blue:
    image: ghcr.io/username/totem-api:main-latest
    container_name: totem-api-blue
    environment:
      - APP_ENV=production
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.api.rule=Host(`api.totem.com`) && Headers(`X-Version`, `blue`)"

  api-green:
    image: ghcr.io/username/totem-api:main-previous
    container_name: totem-api-green
    environment:
      - APP_ENV=production
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.api.rule=Host(`api.totem.com`) && Headers(`X-Version`, `green`)"
```

### Rolling Update (Staging)

```bash
# Script de rolling update
#!/bin/bash
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d --no-deps api
docker-compose -f docker-compose.prod.yml up -d
```

## 🔍 Monitoreo y Observabilidad

### Health Checks

#### Application Health Check
```python
# main.py
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "version": os.getenv("APP_VERSION", "unknown"),
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {
            "database": check_database(),
            "memory": check_memory(),
            "disk": check_disk_space()
        }
    }
```

#### Container Health Check
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1
```

### Métricas y Logging

#### Structured Logging
```python
import structlog

logger = structlog.get_logger()

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    logger.info(
        "request_processed",
        method=request.method,
        url=str(request.url),
        status_code=response.status_code,
        process_time=process_time
    )
    
    return response
```

#### Prometheus Metrics
```python
from prometheus_client import Counter, Histogram, generate_latest

REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    REQUEST_DURATION.observe(duration)
    
    return response
```

## 🛡️ Seguridad en el Pipeline

### Image Scanning

#### Trivy Integration
```yaml
# .github/workflows/ci-cd.yml
- name: 🔍 Run Trivy vulnerability scanner
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:latest
    format: 'sarif'
    output: 'trivy-results.sarif'
    exit-code: '1'
    ignore-unfixed: true
    vuln-type: 'os,library'
```

#### SBOM Generation
```yaml
- name: 📋 Generate SBOM
  run: |
    docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
      aquasec/trivy:latest image --format spdx-json \
      --output sbom.spdx.json ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:latest
```

### Secret Management

#### Environment-Specific Configs
```bash
# .env.production
DATABASE_URL=postgresql://totem:${POSTGRES_PASSWORD}@postgres:5432/totem
SECRET_KEY=${SECRET_KEY}
DEBUG=false
LOG_LEVEL=INFO
SENTRY_DSN=${SENTRY_DSN}

# .env.staging
DATABASE_URL=sqlite:///./totem.db
SECRET_KEY=staging-secret-key
DEBUG=true
LOG_LEVEL=DEBUG
```

## 📊 Métricas de Pipeline

### KPIs a Monitorear

#### Build Performance
- **Build Time**: < 5 minutos
- **Image Size**: < 200MB
- **Test Coverage**: > 80%
- **Security Scan**: 0 critical vulnerabilities

#### Deploy Performance
- **Deploy Time**: < 2 minutos
- **Downtime**: < 30 segundos
- **Rollback Success Rate**: 100%
- **Health Check Time**: < 10 segundos

#### Alertas
```yaml
# Ejemplo de alerta en GitHub Actions
- name: 🚨 Alert on slow build
  if: steps.build.outputs.duration > 300
  run: |
    curl -X POST -H 'Content-type: application/json' \
      --data '{"text":"⚠️ Build time exceeded 5 minutes for ${{ github.repository }}"}' \
      "${{ secrets.SLACK_WEBHOOK }}"
```

## 🔄 Mejores Prácticas

### Development
1. **Commits atómicos** con mensajes claros
2. **Pull requests** con revisión obligatoria
3. **Tests unitarios** para cada nuevo feature
4. **Documentación** actualizada

### CI/CD
1. **Fast feedback** con builds rápidos
2. **Parallel execution** de tests
3. **Caching inteligente** de dependencias
4. **Fail fast** en errores críticos

### Production
1. **Zero downtime** con rolling updates
2. **Automated rollback** en health checks fallidos
3. **Monitoring** de métricas en tiempo real
4. **Disaster recovery** plan documentado

## 📚 Referencias

- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Kubernetes Deployment Strategies](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
- [Semantic Versioning](https://semver.org/)
