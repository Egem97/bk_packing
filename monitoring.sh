#!/bin/bash

# Script de Monitoreo para Automatizaciones
# Autor: Tu Nombre
# Fecha: $(date)

# Configuración
PROJECT_DIR="/home/$USER/automatizaciones"
LOG_FILE="/home/$USER/automatizaciones/monitoring.log"

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Función para imprimir mensajes
print_status() {
    echo -e "${GREEN}[OK]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Función para log
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

# Verificar estado de Docker
check_docker() {
    print_info "Verificando estado de Docker..."
    
    if ! systemctl is-active --quiet docker; then
        print_error "Docker no está corriendo"
        log_message "ERROR: Docker no está corriendo"
        return 1
    else
        print_status "Docker está corriendo"
        log_message "INFO: Docker está corriendo"
    fi
}

# Verificar contenedores
check_containers() {
    print_info "Verificando contenedores..."
    
    cd "$PROJECT_DIR"
    
    # Obtener estado de los contenedores
    local containers=$(docker-compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}")
    
    echo "$containers" | while IFS= read -r line; do
        if [[ $line == *"Up"* ]]; then
            print_status "$line"
            log_message "INFO: Contenedor funcionando - $line"
        elif [[ $line == *"Exit"* ]] || [[ $line == *"Down"* ]]; then
            print_error "$line"
            log_message "ERROR: Contenedor caído - $line"
        else
            print_warning "$line"
            log_message "WARNING: Contenedor con problemas - $line"
        fi
    done
}

# Verificar conectividad de la API
check_api() {
    print_info "Verificando conectividad de la API..."
    
    if curl -f http://localhost:8001/docs > /dev/null 2>&1; then
        print_status "API está respondiendo correctamente"
        log_message "INFO: API está respondiendo correctamente"
    else
        print_error "API no responde"
        log_message "ERROR: API no responde"
        return 1
    fi
}

# Verificar base de datos
check_database() {
    print_info "Verificando conectividad de la base de datos..."
    
    cd "$PROJECT_DIR"
    
    if docker-compose exec -T pipeline-postgres pg_isready -U pipeline_user -d pipeline_db > /dev/null 2>&1; then
        print_status "Base de datos está respondiendo correctamente"
        log_message "INFO: Base de datos está respondiendo correctamente"
    else
        print_error "Base de datos no responde"
        log_message "ERROR: Base de datos no responde"
        return 1
    fi
}

# Verificar uso de recursos
check_resources() {
    print_info "Verificando uso de recursos..."
    
    # Uso de CPU y memoria
    local cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
    local memory_usage=$(free | grep Mem | awk '{printf "%.1f", $3/$2 * 100.0}')
    local disk_usage=$(df / | tail -1 | awk '{print $5}' | cut -d'%' -f1)
    
    echo "   • CPU: ${cpu_usage}%"
    echo "   • Memoria: ${memory_usage}%"
    echo "   • Disco: ${disk_usage}%"
    
    # Verificar si el uso es alto
    if (( $(echo "$cpu_usage > 80" | bc -l) )); then
        print_warning "Uso de CPU alto: ${cpu_usage}%"
        log_message "WARNING: Uso de CPU alto - ${cpu_usage}%"
    fi
    
    if (( $(echo "$memory_usage > 80" | bc -l) )); then
        print_warning "Uso de memoria alto: ${memory_usage}%"
        log_message "WARNING: Uso de memoria alto - ${memory_usage}%"
    fi
    
    if (( $(echo "$disk_usage > 80" | bc -l) )); then
        print_warning "Uso de disco alto: ${disk_usage}%"
        log_message "WARNING: Uso de disco alto - ${disk_usage}%"
    fi
    
    log_message "INFO: Recursos - CPU: ${cpu_usage}%, Memoria: ${memory_usage}%, Disco: ${disk_usage}%"
}

# Verificar logs de errores recientes
check_logs() {
    print_info "Verificando logs de errores recientes..."
    
    cd "$PROJECT_DIR"
    
    # Buscar errores en los últimos 10 minutos
    local error_count=$(docker-compose logs --since=10m 2>&1 | grep -i "error\|exception\|failed" | wc -l)
    
    if [ "$error_count" -gt 0 ]; then
        print_warning "Se encontraron $error_count errores en los últimos 10 minutos"
        log_message "WARNING: $error_count errores encontrados en logs recientes"
        
        # Mostrar los últimos errores
        echo "Últimos errores:"
        docker-compose logs --since=10m 2>&1 | grep -i "error\|exception\|failed" | tail -5
    else
        print_status "No se encontraron errores recientes"
        log_message "INFO: No se encontraron errores recientes"
    fi
}

# Verificar conectividad de red
check_network() {
    print_info "Verificando conectividad de red..."
    
    # Verificar conectividad a internet
    if ping -c 1 8.8.8.8 > /dev/null 2>&1; then
        print_status "Conectividad a internet: OK"
        log_message "INFO: Conectividad a internet OK"
    else
        print_error "Sin conectividad a internet"
        log_message "ERROR: Sin conectividad a internet"
        return 1
    fi
    
    # Verificar puertos abiertos
    local api_port=$(netstat -tuln | grep :8001 | wc -l)
    local db_port=$(netstat -tuln | grep :5433 | wc -l)
    
    if [ "$api_port" -gt 0 ]; then
        print_status "Puerto API (8001): Abierto"
        log_message "INFO: Puerto API (8001) abierto"
    else
        print_error "Puerto API (8001): Cerrado"
        log_message "ERROR: Puerto API (8001) cerrado"
    fi
    
    if [ "$db_port" -gt 0 ]; then
        print_status "Puerto DB (5433): Abierto"
        log_message "INFO: Puerto DB (5433) abierto"
    else
        print_error "Puerto DB (5433): Cerrado"
        log_message "ERROR: Puerto DB (5433) cerrado"
    fi
}

# Generar reporte
generate_report() {
    local report_file="/home/$USER/automatizaciones/monitoring_report_$(date +%Y%m%d_%H%M%S).txt"
    
    echo "=== REPORTE DE MONITOREO - $(date) ===" > "$report_file"
    echo "" >> "$report_file"
    
    # Estado de servicios
    echo "ESTADO DE SERVICIOS:" >> "$report_file"
    cd "$PROJECT_DIR"
    docker-compose ps >> "$report_file" 2>&1
    echo "" >> "$report_file"
    
    # Uso de recursos
    echo "USO DE RECURSOS:" >> "$report_file"
    echo "CPU: $(top -bn1 | grep 'Cpu(s)' | awk '{print $2}' | cut -d'%' -f1)%" >> "$report_file"
    echo "Memoria: $(free | grep Mem | awk '{printf "%.1f", $3/$2 * 100.0}')%" >> "$report_file"
    echo "Disco: $(df / | tail -1 | awk '{print $5}' | cut -d'%' -f1)%" >> "$report_file"
    echo "" >> "$report_file"
    
    # Logs recientes
    echo "LOGS RECIENTES (últimos 10 minutos):" >> "$report_file"
    docker-compose logs --since=10m >> "$report_file" 2>&1
    
    print_status "Reporte generado: $report_file"
    log_message "INFO: Reporte generado - $report_file"
}

# Función principal
main() {
    echo "=========================================="
    echo "   MONITOREO - AUTOMATIZACIONES"
    echo "=========================================="
    echo ""
    
    # Crear archivo de log si no existe
    touch "$LOG_FILE"
    
    # Ejecutar verificaciones
    check_docker
    check_containers
    check_api
    check_database
    check_resources
    check_logs
    check_network
    
    echo ""
    print_info "Generando reporte..."
    generate_report
    
    echo ""
    echo "📊 Resumen del monitoreo:"
    echo "   • Log file: $LOG_FILE"
    echo "   • Últimas 10 líneas del log:"
    tail -10 "$LOG_FILE" | sed 's/^/   /'
    echo ""
}

# Verificar si se solicita reporte
if [ "$1" = "report" ]; then
    generate_report
    exit 0
fi

# Ejecutar función principal
main "$@"
