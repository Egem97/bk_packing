#!/bin/bash

# Script de deployment para VPS
# Soluciona problemas de resolución de hostname en Docker

set -e

echo "🚀 Iniciando deployment en VPS..."

# Detener contenedores existentes
echo "📦 Deteniendo contenedores existentes..."
docker-compose -f docker-compose.vps.yml down

# Limpiar contenedores y redes huérfanas
echo "🧹 Limpiando recursos Docker..."
docker system prune -f
docker network prune -f

# Crear red personalizada si no existe
echo "🌐 Configurando red Docker..."
docker network create pipeline-network 2>/dev/null || echo "Red ya existe"

# Reconstruir imágenes
echo "🔨 Reconstruyendo imágenes..."
docker-compose -f docker-compose.vps.yml build --no-cache

# Iniciar servicios
echo "▶️  Iniciando servicios..."
docker-compose -f docker-compose.vps.yml up -d

# Esperar a que PostgreSQL esté listo
echo "⏳ Esperando a que PostgreSQL esté listo..."
sleep 30

# Verificar estado de los servicios
echo "🔍 Verificando estado de los servicios..."
docker-compose -f docker-compose.vps.yml ps

# Verificar conectividad de red
echo "🌐 Verificando conectividad..."
docker-compose -f docker-compose.vps.yml exec -T scheduler ping -c 3 localhost || echo "⚠️  Advertencia: No se puede hacer ping a localhost"

# Mostrar logs de los servicios
echo "📋 Logs de los servicios:"
echo "=== PostgreSQL ==="
docker-compose -f docker-compose.vps.yml logs --tail=10 pipeline-postgres
echo "=== Scheduler ==="
docker-compose -f docker-compose.vps.yml logs --tail=10 scheduler
echo "=== API ==="
docker-compose -f docker-compose.vps.yml logs --tail=10 api

echo "✅ Deployment completado!"
echo "🌐 API disponible en: http://localhost:8001"
echo "📊 Base de datos PostgreSQL en puerto: 5433"
