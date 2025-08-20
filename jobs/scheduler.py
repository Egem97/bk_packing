import pandas as pd
import schedule
import time
import logging
import sys
import os
from datetime import datetime
from task.flujo import ejecutar_calidad_producto_terminado
from utils.config_loader import get_config_value


# Configurar logging
def setup_logging():
    """Configura el sistema de logging según config.yaml"""
    log_level = get_config_value('logging', 'level') or 'INFO'
    
    # Configurar handlers con encoding UTF-8
    file_handler = logging.FileHandler('scheduler.log', encoding='utf-8')
    console_handler = logging.StreamHandler(sys.stdout)
    
    # Configurar formato
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Configurar logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level))
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logging.getLogger(__name__)


def configurar_scheduler():
    """
    Configura el scheduler según los parámetros del config.yaml
    """
    logger = logging.getLogger(__name__)
    

    logger.info(f"📅 Configurando scheduler: interval={5} minutos")
    
    # Limpiar trabajos anteriores
    schedule.clear()
    
    try:

        schedule.every(5).minutes.do(ejecutar_calidad_producto_terminado)
        logger.info(f"⏰ Programado proceso principal cada 5 minutos")
        
        
    except Exception as e:
        logger.error(f"Error al configurar scheduler: {str(e)}")
        return False

def is_interactive():
    """
    Detecta si el script está ejecutándose en modo interactivo
    """
    return sys.stdin.isatty() and sys.stdout.isatty()

def main():
    """
    Función principal que inicia el sistema automatizado
    """
    # Configurar logging
    logger = setup_logging()
    
    logger.info("🚀 Iniciando sistema automatizado con Schedule...")
    logger.info("📖 Leyendo configuración desde config.yaml...")

    
    # Configurar el scheduler
    configurar_scheduler()
    
    # Decidir si ejecutar proceso inicial
    ejecutar_inicial = False
    
    if is_interactive():
        # Modo interactivo: preguntar al usuario
        print("\n¿Deseas ejecutar el proceso una vez al inicio? (s/n): ", end="")
        try:
            respuesta = input().lower().strip()
            if respuesta in ['s', 'si', 'sí', 'y', 'yes']:
                ejecutar_inicial = True
        except (EOFError, KeyboardInterrupt):
            logger.info("🤖 Modo no interactivo detectado, continuando sin ejecución inicial")
    else:
        # Modo no interactivo (Docker): leer configuración o usar default
        ejecutar_inicial = get_config_value('scheduler', 'ejecutar_inicial') or False
        if ejecutar_inicial:
            logger.info("🤖 Modo no interactivo: ejecutando proceso inicial según configuración")
        else:
            logger.info("🤖 Modo no interactivo: omitiendo proceso inicial")
    
    if ejecutar_inicial:
        logger.info("🔄 Ejecutando procesos iniciales...")
        try:
            ejecutar_calidad_producto_terminado()
            logger.info("✅ Procesos iniciales completados")
        except Exception as e:
            logger.error(f"❌ Error en procesos iniciales: {str(e)}")
        
    
    # Mantener el programa corriendo
    logger.info("⚡ Sistema automatizado en funcionamiento. Presiona Ctrl+C para detener.")
    print("\n" + "="*60)
    print("📅 SISTEMA AUTOMATIZADO ACTIVO")
    print("="*60)
    print("⏰ Próxima ejecución programada según config.yaml")
    print("🛑 Presiona Ctrl+C para detener el sistema")
    print("="*60)
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("🛑 Sistema automatizado detenido por el usuario")
        print("\n✅ Sistema detenido correctamente")
    except Exception as e:
        logger.error(f"❌ Error en el sistema automatizado: {str(e)}")

if __name__ == "__main__":
    main() 
