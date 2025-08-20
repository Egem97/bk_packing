import os
import httpx
import json
import tempfile
import shutil
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import msal
import pandas as pd

import logging
import sys

from utils.config_loader import get_microsoft_graph_config

logger = logging.getLogger(__name__)

class OneDriveExtractor:
    """
    Clase para extraer archivos de OneDrive usando Microsoft Graph API
    """
    
    def __init__(self):
        self.access_token = None
        self.config = get_microsoft_graph_config()
    
    def get_access_token(self) -> Optional[str]:
        """
        Obtiene el token de acceso para Microsoft Graph API
        """
        if not self.config:
            logger.error("Error: No se pudo cargar la configuración")
            return None
        
        AUTHORITY = f"https://login.microsoftonline.com/{self.config['tenant_id']}/oauth2/v2.0/token"
        try:
            with httpx.Client() as client:
                response = client.post(AUTHORITY, data={
                    "grant_type": "client_credentials",
                    "client_id": self.config['client_id'],
                    "client_secret": self.config['client_secret'],
                    "scope": "https://graph.microsoft.com/.default"
                })
                
                if response.status_code == 200:
                    token_response = response.json()
                    access_token = token_response.get("access_token")
                    
                    if access_token:
                        logger.info("Token de acceso obtenido exitosamente")
                        self.access_token = access_token
                        return access_token
                    else:
                        logger.error("Error: No se pudo obtener el token de acceso")
                        return None
                else:
                    logger.error(f"Error HTTP {response.status_code}: {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error al obtener el token: {e}")
            return None

    def listar_archivos_en_carpeta_compartida(self, drive_id: str, item_id: str) -> List[Dict[str, Any]]:
        """
        Lista los archivos dentro de una carpeta compartida en OneDrive / SharePoint usando Microsoft Graph.

        :param drive_id: El ID del drive compartido
        :param item_id: El ID de la carpeta compartida
        :return: Lista de archivos o carpetas dentro de esa carpeta
        """
        if not self.access_token:
            self.access_token = self.get_access_token()
            if not self.access_token:
                logger.error("No se pudo obtener el token de acceso")
                return []
        
        url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{item_id}/children"
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }

        with httpx.Client() as client:
            response = client.get(url, headers=headers)

            if response.status_code == 200:
                return response.json().get("value", [])
            else:
                logger.error(f"Error al obtener archivos: {response.status_code}")
                logger.error(response.json())
                return []

    def get_download_url_by_name(self, json_data: List[Dict[str, Any]], name: str) -> Optional[str]:
        """
        Busca en el JSON un archivo por su nombre y retorna su downloadUrl
        
        Args:
            json_data (list): Lista de diccionarios con información de archivos
            name (str): Nombre del archivo a buscar
        
        Returns:
            str: URL de descarga del archivo encontrado, o None si no se encuentra
        """
        for item in json_data:
            if item.get('name') == name:
                return item.get('@microsoft.graph.downloadUrl')
        return None

    def download_file(self, download_url: str, local_path: str) -> bool:
        """
        Descarga un archivo desde OneDrive usando la URL de descarga
        
        Args:
            download_url (str): URL de descarga del archivo
            local_path (str): Ruta local donde guardar el archivo
            
        Returns:
            bool: True si la descarga fue exitosa, False en caso contrario
        """
        try:
            with httpx.Client() as client:
                with client.stream("GET", download_url) as response:
                    response.raise_for_status()
                    
                    with open(local_path, 'wb') as f:
                        for chunk in response.iter_bytes(chunk_size=8192):
                            f.write(chunk)
            
            logger.info(f"Archivo descargado exitosamente: {local_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error al descargar archivo: {e}")
            return False

    def process_onedrive_files(self, drive_id: str, item_id: str, target_filename: str = None) -> Dict[str, Any]:
        """
        Procesa archivos de OneDrive: lista archivos y opcionalmente descarga uno específico
        
        Args:
            drive_id (str): ID del drive de OneDrive
            item_id (str): ID de la carpeta
            target_filename (str, optional): Nombre del archivo específico a descargar
            
        Returns:
            Dict[str, Any]: Resultado del procesamiento
        """
        # Obtener lista de archivos
        files = self.listar_archivos_en_carpeta_compartida(drive_id, item_id)
        
        if not files:
            return {"success": False, "message": "No se encontraron archivos", "files": []}
        
        result = {
            "success": True,
            "files": files,
            "total_files": len(files),
            "downloaded_file": None
        }
        
        # Si se especifica un archivo objetivo, intentar descargarlo
        if target_filename:
            download_url = self.get_download_url_by_name(files, target_filename)
            if download_url:
                # Crear directorio temporal para la descarga
                temp_dir = tempfile.mkdtemp()
                local_path = os.path.join(temp_dir, target_filename)
                
                if self.download_file(download_url, local_path):
                    result["downloaded_file"] = {
                        "local_path": local_path,
                        "filename": target_filename,
                        "temp_dir": temp_dir
                    }
                else:
                    result["success"] = False
                    result["message"] = f"No se pudo descargar el archivo: {target_filename}"
            else:
                result["success"] = False
                result["message"] = f"No se encontró el archivo: {target_filename}"
        
        return result