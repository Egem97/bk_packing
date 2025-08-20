# Guía de Despliegue en VPS

## Descripción del Proyecto
Tu proyecto consiste en:
- **API FastAPI**: Servicio web en el puerto 8001
- **Scheduler**: Servicio de programación de tareas
- **PostgreSQL**: Base de datos en el puerto 5433

## Prerrequisitos del VPS

### 1. Sistema Operativo
- Ubuntu 20.04 LTS o superior (recomendado)
- Debian 11 o superior
- CentOS 8+ o Rocky Linux

### 2. Especificaciones Mínimas Recomendadas
- **CPU**: 2 cores
- **RAM**: 4GB
- **Almacenamiento**: 20GB SSD
- **Red**: Conexión estable a internet

## Pasos de Despliegue

### Paso 1: Conectar al VPS
```bash
ssh usuario@tu-vps-ip
```

### Paso 2: Actualizar el Sistema
```bash
sudo apt update && sudo apt upgrade -y
```

### Paso 3: Instalar Dependencias del Sistema
```bash
# Instalar herramientas básicas
sudo apt install -y curl wget git unzip

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Agregar usuario al grupo docker
sudo usermod -aG docker $USER
```

### Paso 4: Configurar Firewall
```bash
# Instalar UFW si no está instalado
sudo apt install -y ufw

# Configurar reglas básicas
sudo ufw allow ssh
sudo ufw allow 8001  # Puerto de la API
sudo ufw allow 80    # HTTP (para proxy reverso)
sudo ufw allow 443   # HTTPS (para proxy reverso)

# Activar firewall
sudo ufw enable
```

### Paso 5: Crear Directorio del Proyecto
```bash
# Crear directorio para el proyecto
mkdir -p /home/$USER/automatizaciones
cd /home/$USER/automatizaciones
```

### Paso 6: Subir el Código al VPS

#### Opción A: Usando Git (Recomendado)
```bash
# Clonar tu repositorio
git clone https://github.com/tu-usuario/tu-repositorio.git .
```

#### Opción B: Usando SCP desde tu máquina local
```bash
# Desde tu máquina local
scp -r /ruta/a/tu/proyecto/* usuario@tu-vps-ip:/home/usuario/automatizaciones/
```

### Paso 7: Configurar Variables de Entorno
```bash
# Crear archivo de configuración
nano .env
```

Agregar las siguientes variables:
```env
# Base de datos
POSTGRES_DB=pipeline_db
POSTGRES_USER=pipeline_user
POSTGRES_PASSWORD=tu_password_seguro_aqui

# API
API_HOST=0.0.0.0
API_PORT=8000

# Configuraciones adicionales
PYTHONUNBUFFERED=1
```

### Paso 8: Configurar Proxy Reverso (Opcional pero Recomendado)

#### Instalar Nginx
```bash
sudo apt install -y nginx
```

#### Configurar Nginx
```bash
sudo nano /etc/nginx/sites-available/automatizaciones
```

Agregar la configuración:
```nginx
server {
    listen 80;
    server_name tu-dominio.com;  # Cambiar por tu dominio

    location / {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### Activar el sitio
```bash
sudo ln -s /etc/nginx/sites-available/automatizaciones /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Paso 9: Desplegar con Docker Compose
```bash
# Construir y levantar los servicios
docker-compose up -d --build

# Verificar que los servicios estén corriendo
docker-compose ps

# Ver logs si hay problemas
docker-compose logs -f
```

### Paso 10: Configurar SSL con Let's Encrypt (Opcional)
```bash
# Instalar Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtener certificado SSL
sudo certbot --nginx -d tu-dominio.com

# Configurar renovación automática
sudo crontab -e
# Agregar esta línea:
# 0 12 * * * /usr/bin/certbot renew --quiet
```

## Comandos Útiles para el Mantenimiento

### Verificar Estado de los Servicios
```bash
# Ver todos los contenedores
docker-compose ps

# Ver logs de un servicio específico
docker-compose logs api
docker-compose logs scheduler
docker-compose logs pipeline-postgres

# Ver logs en tiempo real
docker-compose logs -f
```

### Reiniciar Servicios
```bash
# Reiniciar todos los servicios
docker-compose restart

# Reiniciar un servicio específico
docker-compose restart api
```

### Actualizar el Código
```bash
# Detener servicios
docker-compose down

# Actualizar código (git pull o subir nuevos archivos)
git pull

# Reconstruir y levantar
docker-compose up -d --build
```

### Backup de la Base de Datos
```bash
# Crear backup
docker-compose exec pipeline-postgres pg_dump -U pipeline_user pipeline_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Restaurar backup
docker-compose exec -T pipeline-postgres psql -U pipeline_user pipeline_db < backup_file.sql
```

## Monitoreo y Logs

### Configurar Logs Persistentes
```bash
# Crear directorio para logs
mkdir -p /home/$USER/automatizaciones/logs

# Modificar docker-compose.yml para agregar volúmenes de logs
```

### Monitoreo Básico
```bash
# Ver uso de recursos
docker stats

# Ver espacio en disco
df -h

# Ver uso de memoria
free -h
```

## Troubleshooting

### Problemas Comunes

1. **Puerto ya en uso**:
   ```bash
   sudo netstat -tulpn | grep :8001
   sudo kill -9 PID
   ```

2. **Problemas de permisos**:
   ```bash
   sudo chown -R $USER:$USER /home/$USER/automatizaciones
   ```

3. **Contenedores no inician**:
   ```bash
   docker-compose logs
   docker system prune -a
   ```

4. **Problemas de red**:
   ```bash
   docker network ls
   docker network inspect automatizaciones_default
   ```

## Seguridad

### Recomendaciones de Seguridad
1. Cambiar contraseñas por defecto
2. Usar variables de entorno para credenciales
3. Configurar firewall correctamente
4. Mantener el sistema actualizado
5. Usar SSL/TLS en producción
6. Configurar backups automáticos

### Configurar Backups Automáticos
```bash
# Crear script de backup
nano backup_script.sh
```

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/$USER/backups"
mkdir -p $BACKUP_DIR

# Backup de la base de datos
docker-compose exec -T pipeline-postgres pg_dump -U pipeline_user pipeline_db > $BACKUP_DIR/db_backup_$DATE.sql

# Backup de archivos de configuración
tar -czf $BACKUP_DIR/config_backup_$DATE.tar.gz *.yml *.yaml .env

# Eliminar backups antiguos (mantener últimos 7 días)
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
```

```bash
chmod +x backup_script.sh

# Agregar a crontab para ejecutar diariamente a las 2 AM
crontab -e
# Agregar: 0 2 * * * /home/usuario/automatizaciones/backup_script.sh
```

## Verificación Final

Después del despliegue, verifica que todo funcione:

1. **API**: `curl http://tu-vps-ip:8001/docs`
2. **Base de datos**: `docker-compose exec pipeline-postgres psql -U pipeline_user -d pipeline_db -c "SELECT version();"`
3. **Scheduler**: `docker-compose logs scheduler`

¡Tu proyecto debería estar funcionando correctamente en tu VPS!
