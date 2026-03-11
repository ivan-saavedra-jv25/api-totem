#!/bin/bash

# Script de rollback para VPS - Totem API
# Uso: ./rollback.sh [backup_name]

set -e

# Configuración
PROJECT_NAME="totem-api"
DEPLOY_DIR="/opt/$PROJECT_NAME"
BACKUP_DIR="/opt/backups/$PROJECT_NAME"
LOG_FILE="/var/log/$PROJECT_NAME-rollback.log"

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

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

# Listar backups disponibles si no se especifica uno
if [ $# -eq 0 ]; then
    log "Backups disponibles:"
    ls -la "$BACKUP_DIR" | grep "^d" | awk '{print $9}' | grep -v "^\.$\|^\..$"
    echo ""
    read -p "Ingrese el nombre del backup a restaurar: " BACKUP_NAME
else
    BACKUP_NAME=$1
fi

if [ -z "$BACKUP_NAME" ]; then
    error "Debe especificar un nombre de backup"
fi

BACKUP_PATH="$BACKUP_DIR/$BACKUP_NAME"

if [ ! -d "$BACKUP_PATH" ]; then
    error "El backup $BACKUP_NAME no existe en $BACKUP_PATH"
fi

log "Iniciando rollback a backup: $BACKUP_NAME"

# Detener servicios actuales
log "Deteniendo servicios actuales..."
cd "$DEPLOY_DIR" || error "No se puede acceder al directorio $DEPLOY_DIR"

if [ -f "docker-compose.prod.yml" ]; then
    sudo docker-compose -f docker-compose.prod.yml down || true
fi

# Backup de la versión actual antes de rollback
CURRENT_BACKUP="$PROJECT_NAME-rollback-$(date +%Y%m%d-%H%M%S)"
log "Creando backup de la versión actual como: $CURRENT_BACKUP"
sudo cp -r "$DEPLOY_DIR" "$BACKUP_DIR/$CURRENT_BACKUP"

# Restaurar backup
log "Restaurando backup $BACKUP_NAME..."
sudo rm -rf "$DEPLOY_DIR"/*
sudo cp -r "$BACKUP_PATH"/* "$DEPLOY_DIR"/

# Iniciar servicios con el backup restaurado
log "Iniciando servicios con backup restaurado..."
sudo docker-compose -f docker-compose.prod.yml up -d

# Health check
log "Realizando health check..."
sleep 30

if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    log "✅ Rollback completado exitosamente"
else
    error "❌ Health check falló después del rollback"
fi

log "🔄 Rollback a $BACKUP_NAME completado exitosamente"
