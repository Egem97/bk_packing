#!/bin/bash

# Script de Despliegue Automatizado para VPS
# Autor: Tu Nombre
# Fecha: $(date)

set -e  # Salir si hay algún error

echo "🚀 Iniciando despliegue de Automatizaciones..."

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

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

# Verificar si Docker está instalado
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker no está instalado. Instalando..."
        curl -fsSL https://get.docker.com -o get-docker.sh
        sudo sh get-docker.sh
        sudo usermod -aG docker $USER
        print_warning "Docker instalado. Por favor, reinicia la sesión SSH y ejecuta el script nuevamente."
        exit 1
    fi
    print_status "Docker está instalado"
}

# Verificar si Docker Compose está instalado
check_docker_compose() {
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose no está instalado. Instalando..."
        sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
    fi
    print_status "Docker Compose está instalado"
}

# Verificar archivos necesarios
check_files() {
    local required_files=("docker-compose.yml" "api/Dockerfile" "jobs/Dockerfile")
    
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            print_error "Archivo requerido no encontrado: $file"
            exit 1
        fi
    done
    print_status "Todos los archivos requeridos están presentes"
}

# Crear archivo .env si no existe
create_env_file() {
    if [ ! -f ".env" ]; then
        print_status "Creando archivo .env..."
        cat > .env << EOF
# Base de datos
POSTGRES_DB=pipeline_db
POSTGRES_USER=pipeline_user
POSTGRES_PASSWORD=$(openssl rand -base64 32)

# API
API_HOST=0.0.0.0
API_PORT=8000

# Configuraciones adicionales
PYTHONUNBUFFERED=1
EOF
        print_status "Archivo .env creado con contraseña aleatoria"
    else
        print_status "Archivo .env ya existe"
    fi
}

# Detener servicios existentes
stop_services() {
    print_status "Deteniendo servicios existentes..."
    docker-compose down --remove-orphans || true
}

# Limpiar recursos Docker no utilizados
cleanup_docker() {
    print_status "Limpiando recursos Docker no utilizados..."
    docker system prune -f || true
}

# Construir y levantar servicios
build_and_start() {
    print_status "Construyendo y levantando servicios..."
    docker-compose up -d --build
    
    # Esperar a que los servicios estén listos
    print_status "Esperando a que los servicios estén listos..."
    sleep 30
}

# Verificar estado de los servicios
check_services() {
    print_status "Verificando estado de los servicios..."
    
    # Verificar que todos los contenedores estén corriendo
    local containers=$(docker-compose ps -q)
    local running_containers=$(docker-compose ps -q --filter "status=running")
    
    if [ "$containers" = "$running_containers" ]; then
        print_status "✅ Todos los servicios están corriendo correctamente"
    else
        print_error "❌ Algunos servicios no están corriendo"
        docker-compose ps
        docker-compose logs
        exit 1
    fi
}

# Verificar conectividad de la API
check_api() {
    print_status "Verificando conectividad de la API..."
    
    # Esperar un poco más para que la API esté completamente lista
    sleep 10
    
    if curl -f http://localhost:8001/docs > /dev/null 2>&1; then
        print_status "✅ API está respondiendo correctamente"
    else
        print_warning "⚠️  API no responde inmediatamente, revisando logs..."
        docker-compose logs api
    fi
}

# Mostrar información del despliegue
show_deployment_info() {
    echo ""
    echo "🎉 ¡Despliegue completado exitosamente!"
    echo ""
    echo "📋 Información del despliegue:"
    echo "   • API: http://$(hostname -I | awk '{print $1}'):8001"
    echo "   • Documentación API: http://$(hostname -I | awk '{print $1}'):8001/docs"
    echo "   • Base de datos: localhost:5433"
    echo ""
    echo "🔧 Comandos útiles:"
    echo "   • Ver logs: docker-compose logs -f"
    echo "   • Reiniciar: docker-compose restart"
    echo "   • Detener: docker-compose down"
    echo "   • Actualizar: ./deploy.sh"
    echo ""
}

# Función principal
main() {
    echo "=========================================="
    echo "   DESPLIEGUE AUTOMATIZADO - AUTOMATIZACIONES"
    echo "=========================================="
    echo ""
    
    check_docker
    check_docker_compose
    check_files
    create_env_file
    stop_services
    cleanup_docker
    build_and_start
    check_services
    check_api
    show_deployment_info
}

# Ejecutar función principal
main "$@"
