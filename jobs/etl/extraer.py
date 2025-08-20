import sys
import os
import logging
import pandas as pd
import tempfile
import psycopg2
import json
import uuid
from datetime import datetime, timedelta, time, date
from utils.onedrive_extractor import OneDriveExtractor
from utils.zona_horaria import get_peru_datetime
from utils.config_loader import get_database_config

logger = logging.getLogger(__name__)

def extract_onedrive_files():
    
    extractor = OneDriveExtractor()
        
        # Listar archivos en la carpeta
    files = extractor.listar_archivos_en_carpeta_compartida(
            drive_id="b!k0xKW2h1VkGnxasDN0z40PeA8yi0BwBKgEf_EOEPStmAWVEVjX8MQIydW1yMzk1b", 
            item_id="01SPKVU4I6RWNBBAVFIJF3GHBOYOFMUKZS"
    )
        
    if not files:
        logger.error("❌ No se encontraron archivos en la carpeta")
        raise Exception("No se encontraron archivos en OneDrive")
        
    logger.info(f"✅ Se encontraron {len(files)} archivos en la carpeta")
        
        # Buscar el archivo específico
    target_filename = "BD EVALUACION DE CALIDAD DE PRODUCTO TERMINADO.xlsx"
    download_url = extractor.get_download_url_by_name(files, target_filename)
    return pd.read_excel(download_url, sheet_name="CALIDAD PRODUCTO TERMINADO")

def transform_onedrive_files():
    df = extract_onedrive_files()
    logger.info(f"📊 Datos cargados: {len(df)} filas, {len(df.columns)} columnas")
    logger.info(f"📋 Columnas disponibles: {list(df.columns)}")
    df["FECHA DE MP"] = pd.to_datetime(df["FECHA DE MP"])
    df["FECHA DE PROCESO"] = pd.to_datetime(df["FECHA DE PROCESO"])

        # Fill NaN values with 0 for all float columns
    float_columns = df.select_dtypes(include=['float64']).columns
    df[float_columns] = df[float_columns].fillna(0)

    df["MODULO "] = df["MODULO "].replace({"`1": 1})
    df["TURNO "] = df["TURNO "].fillna(0)
    df["TURNO "] = df["TURNO "].replace({"Dia": 2,111: 11})
    df["VARIEDAD"] = df["VARIEDAD"].fillna("NO ESPECIFICADO")
    df["VARIEDAD"] = df["VARIEDAD"].str.strip()
        #df["TURNO "] = df["TURNO "].astype(int)
    df["PRESENTACION "] = df["PRESENTACION "].fillna("NO ESPECIFICADO")
    df["PRESENTACION "] = df["PRESENTACION "].str.strip()
    df["DESTINO"] = df["DESTINO"].fillna("NO ESPECIFICADO")
    df["DESTINO"] = df["DESTINO"].str.strip()

    df["TIPO DE CAJA"] = df["TIPO DE CAJA"].fillna("-")
    df["TIPO DE CAJA"] = df["TIPO DE CAJA"].str.strip()

    df["N° FCL"] = df["N° FCL"].astype(str)
    df["N° FCL"] = df["N° FCL"].replace(['None', 'nan', 'NaN', 'NULL', 'null', ''], "-")
    df["N° FCL"] = df["N° FCL"].str.strip()
        # Replace None, 'nan', and NaN values with "-"


        # Método más agresivo para reemplazar valores nulos
    df["TRAZABILIDAD"] = df["TRAZABILIDAD"].astype(str)
    df["TRAZABILIDAD"] = df["TRAZABILIDAD"].replace(['None', 'nan', 'NaN', 'NULL', 'null', ''], "-")
    df["TRAZABILIDAD"] = df["TRAZABILIDAD"].fillna("-")
    df["TRAZABILIDAD"] = df["TRAZABILIDAD"].str.strip()

    df["OBSERVACIONES"] = df["OBSERVACIONES"].astype(str)
    df["OBSERVACIONES"] = df["OBSERVACIONES"].replace(['None', 'nan', 'NaN', 'NULL', 'null', ''], "-")
        
    df["EMPRESA"] = df["PRODUCTOR"].replace(
            {'GMH BERRIES S.A.C': 'AGRICOLA BLUE GOLD S.A.C.', 'BIG BERRIES S.A.C': 'AGRICOLA BLUE GOLD S.A.C.', 'CANYON BERRIES S.A.C': 'AGRICOLA BLUE GOLD S.A.C.','AGRICOLA BLUE GOLD S.A.C': 'AGRICOLA BLUE GOLD S.A.C.',
            'EXCELLENCE FRUIT S.A.C': "SAN LUCAR S.A.", 'GAP BERRIES S.A.C': "SAN LUCAR S.A.", 'SAN EFISIO S.A.C': "SAN LUCAR S.A."}
    )
    df = df[df["N° FCL"]!="-"]
        # Limpiar espacios en los nombres de las columnas
    df.columns = df.columns.str.strip()
        
        # Trabajar con todas las columnas - no eliminar filas por valores null
        # Solo rellenar valores null en columnas numéricas con 0
    numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns
    df[numeric_columns] = df[numeric_columns].fillna(0)
        
    logger.info(f"📊 Después de rellenar nulls numéricos: {len(df)} filas")
    processed_records = []
        
    for index, row in df.iterrows():
            # Generar ID único para cada registro
            record_id = f"calidad_{uuid.uuid4().hex[:8]}"
            
            # Convertir fila a diccionario y manejar timestamps y time
            raw_data = {}
            for col, value in row.items():
                if pd.isna(value):
                    raw_data[col] = None
                elif isinstance(value, pd.Timestamp):
                    raw_data[col] = value.isoformat()
                elif isinstance(value, (time, date)):
                    raw_data[col] = str(value)
                else:
                    raw_data[col] = value
            
            # Crear registro en formato JSON
            record = {
                'id': record_id,
                'source_file': 'BD EVALUACION DE CALIDAD DE PRODUCTO TERMINADO.xlsx',
                'data_type': 'calidad_producto_terminado',
                'raw_data': None,
                'processed_data': {
                    'record_id': record_id,
                    'row_index': int(index),
                    'processed_at': get_peru_datetime().isoformat(),
                    'data': raw_data
                }
            }
            
            processed_records.append(record)
        
    logger.info(f"✅ Convertidos {len(processed_records)} registros a formato JSON")
        
        # Mostrar ejemplo del primer registro
    if processed_records:
        logger.info("📋 Ejemplo del primer registro:")
        #logger.info(json.dumps(processed_records[0], indent=2, default=str))
    return processed_records


def load_onedrive_records_to_postgres():

    processed_info = transform_onedrive_files()
    records = processed_info
    total_records = len(processed_info)
    del processed_info
    logger.info(f"📥 Cargando {total_records} registros a PostgreSQL (reemplazando datos existentes)...")
        
        # Obtener configuración de base de datos
    db_config = get_database_config()
    conn = psycopg2.connect(
            host=db_config.get('host', 'pipeline-postgres'),
            port=db_config.get('port', 5432),
            database=db_config.get('name', 'pipeline_db'),
            user=db_config.get('user', 'pipeline_user'),
            password=db_config.get('password', 'pipeline_pass')
        )
        
    cursor = conn.cursor()
    try:
            # Paso 1: Crear tabla temporal
            logger.info("🔄 Creando tabla temporal...")
            # Obtener timestamp actual en zona horaria de Perú
            peru_now = get_peru_datetime()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pipeline.pipeline_data_temp (
                    id VARCHAR(255) PRIMARY KEY,
                    source_file VARCHAR(500),
                    data_type VARCHAR(100),
                    raw_data JSONB,
                    processed_data JSONB,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT %s,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT %s
                )
            """, (peru_now, peru_now))
            
            # Paso 2: Limpiar tabla temporal
            cursor.execute("DELETE FROM pipeline.pipeline_data_temp")
            
            # Paso 3: Insertar nuevos datos en tabla temporal
            logger.info("📝 Insertando datos en tabla temporal...")
            for record in records:
                cursor.execute("""
                    INSERT INTO pipeline.pipeline_data_temp (id, source_file, data_type, raw_data, processed_data, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    record['id'],
                    record['source_file'],
                    record['data_type'],
                    json.dumps(record['raw_data']),
                    json.dumps(record['processed_data']),
                    peru_now,
                    peru_now
                ))
            
            # Paso 4: Verificar que los datos se insertaron correctamente
            cursor.execute("SELECT COUNT(*) FROM pipeline.pipeline_data_temp")
            temp_count = cursor.fetchone()[0]
            
            if temp_count != total_records:
                raise Exception(f"Error: Se insertaron {temp_count} registros en temp, pero se esperaban {total_records}")
            
            logger.info(f"✅ {temp_count} registros insertados en tabla temporal")
            
            # Paso 5: Reemplazar tabla principal de forma atómica
            logger.info("🔄 Reemplazando tabla principal...")
            
            # Obtener conteo de registros existentes para comparación
            cursor.execute("SELECT COUNT(*) FROM pipeline.pipeline_data WHERE data_type = 'calidad_producto_terminado'")
            old_count = cursor.fetchone()[0]
            
            # Eliminar registros existentes del tipo específico
            cursor.execute("DELETE FROM pipeline.pipeline_data WHERE data_type = 'calidad_producto_terminado'")
            
            # Insertar nuevos datos desde la tabla temporal
            cursor.execute("""
                INSERT INTO pipeline.pipeline_data (id, source_file, data_type, raw_data, processed_data, created_at, updated_at)
                SELECT id, source_file, data_type, raw_data, processed_data, created_at, updated_at
                FROM pipeline.pipeline_data_temp
            """)
            
            # Verificar que la inserción fue exitosa
            cursor.execute("SELECT COUNT(*) FROM pipeline.pipeline_data WHERE data_type = 'calidad_producto_terminado'")
            new_count = cursor.fetchone()[0]
            
            if new_count != total_records:
                raise Exception(f"Error: Se insertaron {new_count} registros en principal, pero se esperaban {total_records}")
            
            # Paso 6: Limpiar tabla temporal
            cursor.execute("DROP TABLE IF EXISTS pipeline.pipeline_data_temp")
            
            # Commit de todos los cambios
            conn.commit()
            
            logger.info(f"✅ Reemplazo completado exitosamente:")
            logger.info(f"   - Registros anteriores: {old_count}")
            logger.info(f"   - Registros nuevos: {new_count}")
            logger.info(f"   - Diferencia: {new_count - old_count}")
            
    except Exception as e:
            # Rollback en caso de error
        conn.rollback()
        logger.error(f"❌ Error durante el reemplazo: {e}")
        raise
        
    finally:
        cursor.close()
        conn.close()
    return f"Datos reemplazados exitosamente: {total_records} registros (reemplazó {old_count} anteriores)"
        