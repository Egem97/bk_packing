import pandas as pd
import logging
from datetime import datetime
from etl.extraer import load_onedrive_records_to_postgres

def ejecutar_calidad_producto_terminado():
    """
    Función TIEMPOS PACKING
    """
    logger = logging.getLogger(__name__)
    try:
        inicio = datetime.now()
        logger.info("🚀 Iniciando proceso automatizado...")
        
        
        load_onedrive_records_to_postgres()
        
            
    except Exception as e:
        logger.error(f"❌ Error en el proceso principal: {str(e)}")
        return False
