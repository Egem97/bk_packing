#!/bin/bash

# Script de Backup Automático para Automatizaciones
# Autor: Tu Nombre
# Fecha: $(date)

set -e

# Configuración
BACKUP_DIR="/home/$USER/backups"
RETENTION_DAYS=7
DATE=$(date +%Y%m%d_%H%M%S)
PROJECT_DIR="/home/$USER/automatizaciones"

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Función para imprimir mensajes
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Crear directorio de backup si no existe
create_backup_dir() {
    if [ ! -d "$BACKUP_DIR" ]; then
        mkdir -p "$BACKUP_DIR"
        print_status "Directorio de backup creado: $BACKUP_DIR"
    fi
}

# Backup de la base de datos
backup_database() {
    print_status "Iniciando backup de la base de datos..."
    
    cd "$PROJECT_DIR"
    
    # Verificar si los contenedores están corriendo
    if ! docker-compose ps | grep -q "pipeline-postgres.*Up"; then
        print_error "La base de datos no está corriendo. No se puede hacer backup."
        return 1
    fi
    
    # Crear backup de la base de datos
    docker-compose exec -T pipeline-postgres pg_dump -U pipeline_user pipeline_db > "$BACKUP_DIR/db_backup_$DATE.sql"
    
    if [ $? -eq 0 ]; then
        print_status "✅ Backup de base de datos completado: db_backup_$DATE.sql"
        
        # Comprimir el backup
        gzip "$BACKUP_DIR/db_backup_$DATE.sql"
        print_status "✅ Backup comprimido: db_backup_$DATE.sql.gz"
    else
        print_error "❌ Error al crear backup de la base de datos"
        return 1
    fi
}

# Backup de archivos de configuración
backup_config() {
    print_status "Iniciando backup de archivos de configuración..."
    
    cd "$PROJECT_DIR"
    
    # Crear backup de archivos importantes
    tar -czf "$BACKUP_DIR/config_backup_$DATE.tar.gz" \
        docker-compose.yml \
        .env \
        api/ \
        jobs/ \
        db/ \
        --exclude='api/__pycache__' \
        --exclude='jobs/__pycache__' \
        --exclude='*.pyc' \
        --exclude='.git'
    
    if [ $? -eq 0 ]; then
        print_status "✅ Backup de configuración completado: config_backup_$DATE.tar.gz"
    else
        print_error "❌ Error al crear backup de configuración"
        return 1
    fi
}

# Backup de logs (si existen)
backup_logs() {
    if [ -d "$PROJECT_DIR/logs" ]; then
        print_status "Iniciando backup de logs..."
        
        tar -czf "$BACKUP_DIR/logs_backup_$DATE.tar.gz" -C "$PROJECT_DIR" logs/
        
        if [ $? -eq 0 ]; then
            print_status "✅ Backup de logs completado: logs_backup_$DATE.tar.gz"
        else
            print_warning "⚠️  Error al crear backup de logs"
        fi
    else
        print_status "No hay directorio de logs para hacer backup"
    fi
}

# Limpiar backups antiguos
cleanup_old_backups() {
    print_status "Limpiando backups antiguos (más de $RETENTION_DAYS días)..."
    
    # Eliminar backups de base de datos antiguos
    find "$BACKUP_DIR" -name "db_backup_*.sql.gz" -mtime +$RETENTION_DAYS -delete 2>/dev/null || true
    
    # Eliminar backups de configuración antiguos
    find "$BACKUP_DIR" -name "config_backup_*.tar.gz" -mtime +$RETENTION_DAYS -delete 2>/dev/null || true
    
    # Eliminar backups de logs antiguos
    find "$BACKUP_DIR" -name "logs_backup_*.tar.gz" -mtime +$RETENTION_DAYS -delete 2>/dev/null || true
    
    print_status "✅ Limpieza de backups antiguos completada"
}

# Mostrar información del backup
show_backup_info() {
    echo ""
    echo "📊 Información del backup:"
    echo "   • Fecha: $(date)"
    echo "   • Directorio: $BACKUP_DIR"
    echo "   • Tamaño total: $(du -sh "$BACKUP_DIR" | cut -f1)"
    echo ""
    echo "📁 Archivos de backup creados:"
    ls -lh "$BACKUP_DIR"/*"$DATE"* 2>/dev/null || echo "   No se encontraron archivos de backup"
    echo ""
    echo "🗑️  Retención: $RETENTION_DAYS días"
    echo ""
}

# Función para restaurar backup (opcional)
restore_backup() {
    if [ -z "$1" ]; then
        print_error "Debe especificar el archivo de backup a restaurar"
        echo "Uso: $0 restore <archivo_backup>"
        exit 1
    fi
    
    local backup_file="$1"
    
    if [ ! -f "$backup_file" ]; then
        print_error "Archivo de backup no encontrado: $backup_file"
        exit 1
    fi
    
    print_warning "⚠️  ¿Está seguro de que desea restaurar desde $backup_file? (y/N)"
    read -r response
    
    if [[ "$response" =~ ^[Yy]$ ]]; then
        print_status "Iniciando restauración..."
        
        cd "$PROJECT_DIR"
        
        # Detener servicios
        docker-compose down
        
        # Restaurar base de datos
        if [[ "$backup_file" == *"db_backup"* ]]; then
            print_status "Restaurando base de datos..."
            docker-compose up -d pipeline-postgres
            
            # Esperar a que la base de datos esté lista
            sleep 10
            
            # Restaurar
            gunzip -c "$backup_file" | docker-compose exec -T pipeline-postgres psql -U pipeline_user pipeline_db
        fi
        
        # Restaurar configuración
        if [[ "$backup_file" == *"config_backup"* ]]; then
            print_status "Restaurando configuración..."
            tar -xzf "$backup_file" -C "$PROJECT_DIR"
        fi
        
        print_status "✅ Restauración completada"
    else
        print_status "Restauración cancelada"
    fi
}

# Función principal
main() {
    echo "=========================================="
    echo "   BACKUP AUTOMÁTICO - AUTOMATIZACIONES"
    echo "=========================================="
    echo ""
    
    # Verificar si se solicita restauración
    if [ "$1" = "restore" ]; then
        restore_backup "$2"
        exit 0
    fi
    
    create_backup_dir
    backup_database
    backup_config
    backup_logs
    cleanup_old_backups
    show_backup_info
    
    echo "🎉 ¡Backup completado exitosamente!"
}

# Ejecutar función principal
main "$@"
