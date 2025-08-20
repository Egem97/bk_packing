"""
Service layer for business logic and database operations
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from .schemas import CalidadProductoTerminado

logger = logging.getLogger(__name__)

class DataService:
    """Service for data operations"""
    
    def get_calidad_producto_terminado(
        self,
        db,
        limit: Optional[int] = None,
        offset: int = 0,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[CalidadProductoTerminado]:
        """Get calidad producto terminado data with filtering"""
        try:
            query = """
                SELECT 
                    id,
                    source_file,
                    created_at,
                    updated_at,
                    processed_data
                FROM pipeline.pipeline_data
                WHERE data_type = 'calidad_producto_terminado'
            """
            
            params = []
            
            # Add filters if provided
            if filters:
                for key, value in filters.items():
                    if value is not None:
                        query += f" AND processed_data->'data'->>'{key}' ILIKE %s"
                        params.append(f"%{value}%")
            
            query += " ORDER BY created_at DESC"
            
            if limit:
                query += f" LIMIT %s"
                params.append(limit)
            
            query += f" OFFSET %s"
            params.append(offset)
            
            cursor = db.cursor()
            cursor.execute(query, tuple(params))
            rows = cursor.fetchall()
            
            results = []
            for row in rows:
                results.append(CalidadProductoTerminado(
                    id=row[0],
                    source_file=row[1],
                    created_at=row[2],
                    updated_at=row[3],
                    processed_data=row[4]
                ))
            
            cursor.close()
            return results
            
        except Exception as e:
            logger.error(f"Error getting calidad producto terminado data: {str(e)}")
            raise

    def get_calidad_producto_terminado_by_empresa(
        self,
        db,
        empresa: str,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[CalidadProductoTerminado]:
        """Get calidad producto terminado data filtered by empresa"""
        try:
            query = """
                SELECT 
                    id,
                    source_file,
                    created_at,
                    updated_at,
                    processed_data
                FROM pipeline.pipeline_data
                WHERE data_type = 'calidad_producto_terminado'
                AND processed_data->'data'->>'EMPRESA' ILIKE %s
                ORDER BY created_at DESC
            """
            
            params = [f"%{empresa}%"]
            
            if limit:
                query += f" LIMIT %s"
                params.append(limit)
            
            query += f" OFFSET %s"
            params.append(offset)
            
            cursor = db.cursor()
            cursor.execute(query, tuple(params))
            rows = cursor.fetchall()
            
            results = []
            for row in rows:
                results.append(CalidadProductoTerminado(
                    id=row[0],
                    source_file=row[1],
                    created_at=row[2],
                    updated_at=row[3],
                    processed_data=row[4]
                ))
            
            cursor.close()
            return results
            
        except Exception as e:
            logger.error(f"Error getting calidad producto terminado data by empresa: {str(e)}")
            raise
