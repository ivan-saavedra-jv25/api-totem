#!/bin/bash

# Script de deploy para VPS - Totem API
# Uso: ./deploy.sh [staging|production]

set -e  # Exit on error

# Configuración
PROJECT_NAME="totem-api"
DEPLOY_DIR="/opt/$PROJECT_NAME"
BACKUP_DIR="/opt/backups/$PROJECT_NAME"
LOG_FILE="/var/log/$PROJECT_NAME-deploy.log"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Funciones de logging
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}" | tee -a "$LOG_FILE"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}" | tee -a "$LOG_FILE"
    exit 1
}

# Validar argumentos
if [ $# -eq 0 ]; then
    error "Debe especificar el entorno: staging o production"
fi

ENVIRONMENT=$1

if [ "$ENVIRONMENT" != "staging" ] && [ "$ENVIRONMENT" != "production" ]; then
    error "Entorno inválido. Use: staging o production"
fi

log "Iniciando deploy a $ENVIRONMENT"

# Verificar si estamos en el servidor correcto
if [ "$ENVIRONMENT" = "production" ] && [ ! -f "/etc/production-server" ]; then
    error "Este script no debe ejecutarse en producción desde este servidor"
fi

# Crear directorios si no existen
sudo mkdir -p "$DEPLOY_DIR"
sudo mkdir -p "$BACKUP_DIR"
sudo mkdir -p "$(dirname "$LOG_FILE")"

# Backup de la versión actual
if [ -d "$DEPLOY_DIR" ]; then
    log "Creando backup de la versión actual..."
    BACKUP_NAME="$PROJECT_NAME-$(date +%Y%m%d-%H%M%S)"
    sudo cp -r "$DEPLOY_DIR" "$BACKUP_DIR/$BACKUP_NAME"
    log "Backup creado en $BACKUP_DIR/$BACKUP_NAME"
fi

# Navegar al directorio de deploy
cd "$DEPLOY_DIR" || error "No se puede acceder al directorio $DEPLOY_DIR"

# Descargar última versión del código
log "Descargando última versión del código..."
if [ -d ".git" ]; then
    sudo git fetch origin
    sudo git reset --hard origin/main
else
    sudo git clone https://github.com/$(whoami)/$PROJECT_NAME.git .
fi

# Verificar si hay cambios
if sudo git diff --quiet HEAD~1 HEAD; then
    warn "No hay cambios nuevos. Abortando deploy."
    exit 0
fi

# Detener servicios existentes
log "Deteniendo servicios existentes..."
if [ -f "docker-compose.prod.yml" ]; then
    sudo docker-compose -f docker-compose.prod.yml down || true
fi

# Limpiar imágenes antiguas
log "Limpiando imágenes Docker antiguas..."
sudo docker image prune -f

# Descargar nuevas imágenes
log "Descargando nuevas imágenes Docker..."
if [ "$ENVIRONMENT" = "production" ]; then
    # Usar imagen específica para producción
    IMAGE_TAG="latest"
    sudo docker pull ghcr.io/$(whoami)/$PROJECT_NAME:$IMAGE_TAG
    
    # Actualizar el tag en docker-compose
    sudo sed -i "s|image: totem-api:latest|image: ghcr.io/$(whoami)/$PROJECT_NAME:$IMAGE_TAG|g" docker-compose.prod.yml
else
    # Build local para staging
    sudo docker-compose -f docker-compose.prod.yml build
fi

# Iniciar servicios
log "Iniciando servicios..."
if [ "$ENVIRONMENT" = "production" ]; then
    sudo docker-compose -f docker-compose.prod.yml up -d
else
    sudo docker-compose -f docker-compose.yml up -d
fi

# Esperar a que los servicios inicien
log "Esperando a que los servicios inicien..."
sleep 30

# Health check
log "Realizando health check..."
MAX_RETRIES=10
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        log "✅ Health check exitoso"
        break
    else
        RETRY_COUNT=$((RETRY_COUNT + 1))
        warn "Health check fallido, reintentando... ($RETRY_COUNT/$MAX_RETRIES)"
        sleep 10
    fi
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    error "❌ Health check falló después de $MAX_RETRIES intentos"
fi

# Limpiar logs antiguos (mantener últimos 7 días)
log "Limpiando logs antiguos..."
find /var/log -name "$PROJECT_NAME*.log" -mtime +7 -delete 2>/dev/null || true

# Mostrar estado final
log "Estado final de los contenedores:"
sudo docker ps -a --filter "name=$PROJECT_NAME"

log "🚉 Deploy completado exitosamente a $ENVIRONMENT"

# Enviar notificación (opcional)
if command -v curl &> /dev/null && [ -n "$SLACK_WEBHOOK" ]; then
    curl -X POST -H 'Content-type: application/json' \
        --data "{\"text\":\"✅ Deploy de $PROJECT_NAME a $ENVIRONMENT completado exitosamente\"}" \
        "$SLACK_WEBHOOK" 2>/dev/null || true
fi

log "Deploy finalizado. Logs disponibles en: $LOG_FILE"
