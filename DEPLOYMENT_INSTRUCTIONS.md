# Instrucciones de Deployment

Este proyecto soporta dos entornos de deployment: **desarrollo local** y **VPS/producción**.

## 🏠 Desarrollo Local

### Requisitos
- Docker y Docker Compose instalados
- Git

### Pasos para deployment local

1. **Clonar el repositorio**:
   ```bash
   git clone <tu-repositorio>
   cd Automatizaciones
   ```

2. **Ejecutar el script de deployment local**:
   ```bash
   chmod +x deploy_local.sh
   ./deploy_local.sh
   ```

3. **O manualmente**:
   ```bash
   docker-compose down
   docker-compose build --no-cache
   docker-compose up -d
   ```

### Configuración local
- **API**: http://localhost:8001
- **PostgreSQL**: localhost:5433
- **Red**: Docker Compose network (contenedores se comunican por nombre)

## 🚀 VPS/Producción

### Requisitos
- VPS con Docker y Docker Compose instalados
- Acceso SSH al servidor

### Pasos para deployment en VPS

1. **Subir código al VPS**:
   ```bash
   git clone <tu-repositorio>
   cd Automatizaciones
   ```

2. **Ejecutar el script de deployment para VPS**:
   ```bash
   chmod +x deploy_vps.sh
   ./deploy_vps.sh
   ```

3. **O manualmente**:
   ```bash
   docker-compose -f docker-compose.vps.yml down
   docker-compose -f docker-compose.vps.yml build --no-cache
   docker-compose -f docker-compose.vps.yml up -d
   ```

### Configuración VPS
- **API**: http://tu-ip-vps:8001
- **PostgreSQL**: localhost:5433
- **Red**: `network_mode: host` (contenedores usan red del host)

## 🔧 Diferencias entre entornos

| Aspecto | Desarrollo Local | VPS/Producción |
|---------|------------------|----------------|
| Archivo Docker Compose | `docker-compose.yml` | `docker-compose.vps.yml` |
| Red de contenedores | Docker network | `network_mode: host` |
| Hostname DB | `pipeline-postgres` | `localhost` |
| Puerto DB | `5432` (interno) | `5433` (host) |
| Variable ENVIRONMENT | `development` | `production` |

## 🐛 Solución de problemas

### Error: "could not translate host name to address"

**Causa**: Problema de resolución de hostname en VPS.

**Solución**: 
1. Usar `docker-compose.vps.yml` en lugar de `docker-compose.yml`
2. Verificar que la variable `ENVIRONMENT=production` esté configurada

### Error: "Connection refused" en desarrollo local

**Causa**: Contenedores no pueden comunicarse entre sí.

**Solución**:
1. Usar `docker-compose.yml` (no el archivo .vps.yml)
2. Verificar que todos los contenedores estén en la misma red

### Verificar estado de servicios

```bash
# Desarrollo local
docker-compose ps

# VPS
docker-compose -f docker-compose.vps.yml ps
```

### Ver logs

```bash
# Desarrollo local
docker-compose logs -f [servicio]

# VPS
docker-compose -f docker-compose.vps.yml logs -f [servicio]
```

## 📝 Notas importantes

1. **Configuración automática**: El sistema detecta automáticamente el entorno usando la variable `ENVIRONMENT`
2. **Puertos**: En VPS, PostgreSQL está expuesto en el puerto 5433 del host
3. **Red**: En VPS se usa `network_mode: host` para evitar problemas de DNS
4. **Volúmenes**: Los datos de PostgreSQL se mantienen en ambos entornos

## 🔄 Actualizaciones

Para actualizar el código:

### Desarrollo local
```bash
git pull
./deploy_local.sh
```

### VPS
```bash
git pull
./deploy_vps.sh
```
