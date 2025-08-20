# 🚀 Despliegue Rápido en VPS

## Resumen del Proyecto
Tu proyecto de automatizaciones incluye:
- **API FastAPI** (puerto 8001)
- **Scheduler de tareas**
- **Base de datos PostgreSQL** (puerto 5433)

## ⚡ Despliegue Rápido (5 minutos)

### 1. Conectar al VPS
```bash
ssh usuario@tu-vps-ip
```

### 2. Preparar el entorno
```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Docker y Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
sudo usermod -aG docker $USER

# Reiniciar sesión SSH
exit
# Conectar nuevamente: ssh usuario@tu-vps-ip
```

### 3. Subir el proyecto
```bash
# Crear directorio
mkdir -p /home/$USER/automatizaciones
cd /home/$USER/automatizaciones

# Opción A: Clonar desde Git
git clone https://github.com/tu-usuario/tu-repositorio.git .

# Opción B: Subir archivos manualmente
# (Desde tu máquina local)
scp -r /ruta/a/tu/proyecto/* usuario@tu-vps-ip:/home/usuario/automatizaciones/
```

### 4. Desplegar automáticamente
```bash
# Hacer ejecutables los scripts
chmod +x deploy.sh backup_script.sh monitoring.sh

# Ejecutar despliegue automático
./deploy.sh
```

### 5. Verificar el despliegue
```bash
# Verificar servicios
docker-compose ps

# Verificar API
curl http://localhost:8001/docs

# Ejecutar monitoreo
./monitoring.sh
```

## 🔧 Comandos Útiles

### Gestión de Servicios
```bash
# Ver estado
docker-compose ps

# Ver logs
docker-compose logs -f

# Reiniciar
docker-compose restart

# Detener
docker-compose down

# Actualizar
git pull && docker-compose up -d --build
```

### Monitoreo
```bash
# Monitoreo completo
./monitoring.sh

# Solo generar reporte
./monitoring.sh report

# Ver logs en tiempo real
docker-compose logs -f api
docker-compose logs -f scheduler
```

### Backup
```bash
# Backup manual
./backup_script.sh

# Restaurar backup
./backup_script.sh restore /ruta/al/backup.sql.gz

# Configurar backup automático (diario a las 2 AM)
crontab -e
# Agregar: 0 2 * * * /home/usuario/automatizaciones/backup_script.sh
```

## 🌐 Configuración de Dominio (Opcional)

### 1. Instalar Nginx
```bash
sudo apt install -y nginx
```

### 2. Configurar proxy reverso
```bash
sudo nano /etc/nginx/sites-available/automatizaciones
```

```nginx
server {
    listen 80;
    server_name tu-dominio.com;

    location / {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 3. Activar sitio
```bash
sudo ln -s /etc/nginx/sites-available/automatizaciones /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 4. Configurar SSL
```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d tu-dominio.com
```

## 🔒 Seguridad

### Firewall
```bash
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

### Variables de Entorno
```bash
# Editar archivo .env
nano .env

# Cambiar contraseñas por defecto
POSTGRES_PASSWORD=tu_password_seguro_aqui
```

## 📊 Monitoreo y Mantenimiento

### Verificación Diaria
```bash
# Agregar a crontab para verificación diaria
crontab -e
# Agregar: 0 8 * * * /home/usuario/automatizaciones/monitoring.sh
```

### Logs Persistentes
```bash
# Crear directorio para logs
mkdir -p /home/$USER/automatizaciones/logs

# Ver logs del sistema
journalctl -u docker.service -f
```

## 🆘 Troubleshooting

### Problemas Comunes

1. **Puerto ocupado**:
   ```bash
   sudo netstat -tulpn | grep :8001
   sudo kill -9 PID
   ```

2. **Contenedores no inician**:
   ```bash
   docker-compose logs
   docker system prune -a
   ```

3. **Problemas de permisos**:
   ```bash
   sudo chown -R $USER:$USER /home/$USER/automatizaciones
   ```

4. **Base de datos no conecta**:
   ```bash
   docker-compose exec pipeline-postgres psql -U pipeline_user -d pipeline_db
   ```

### Logs de Error
```bash
# Ver errores específicos
docker-compose logs | grep -i error

# Ver logs de los últimos 10 minutos
docker-compose logs --since=10m
```

## 📞 Soporte

Si tienes problemas:
1. Revisa los logs: `docker-compose logs`
2. Ejecuta el monitoreo: `./monitoring.sh`
3. Verifica el estado: `docker-compose ps`

## 🎯 URLs de Acceso

- **API**: `http://tu-vps-ip:8001`
- **Documentación**: `http://tu-vps-ip:8001/docs`
- **Base de datos**: `localhost:5433`

¡Tu proyecto debería estar funcionando correctamente! 🎉
