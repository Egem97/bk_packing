#!/bin/bash

# Script de deployment para desarrollo local
# Usa la configuración estándar de Docker Compose

set -e

echo "🚀 Iniciando deployment local..."

# Detener contenedores existentes
echo "📦 Deteniendo contenedores existentes..."
docker-compose down

# Limpiar contenedores y redes huérfanas
echo "🧹 Limpiando recursos Docker..."
docker system prune -f
docker network prune -f

# Reconstruir imágenes
echo "🔨 Reconstruyendo imágenes..."
docker-compose build --no-cache

# Iniciar servicios
echo "▶️  Iniciando servicios..."
docker-compose up -d

# Esperar a que PostgreSQL esté listo
echo "⏳ Esperando a que PostgreSQL esté listo..."
sleep 30

# Verificar estado de los servicios
echo "🔍 Verificando estado de los servicios..."
docker-compose ps

# Verificar conectividad de red
echo "🌐 Verificando conectividad..."
docker-compose exec -T scheduler ping -c 3 pipeline-postgres || echo "⚠️  Advertencia: No se puede hacer ping al contenedor PostgreSQL"

# Mostrar logs de los servicios
echo "📋 Logs de los servicios:"
echo "=== PostgreSQL ==="
docker-compose logs --tail=10 pipeline-postgres
echo "=== Scheduler ==="
docker-compose logs --tail=10 scheduler
echo "=== API ==="
docker-compose logs --tail=10 api

echo "✅ Deployment local completado!"
echo "🌐 API disponible en: http://localhost:8001"
echo "📊 Base de datos PostgreSQL en puerto: 5433"
