"""
Configuration loader for Pipeline APG Air
Reads configuration from config.yaml file and provides unified access to settings
"""

import yaml
import os
from pathlib import Path

def load_config():
    """Load configuration from config.yaml file"""
    config_path =  "config.yaml"

    with open(config_path, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
    
    return config

def get_database_config():
    """Get database configuration from config.yaml"""
    config = load_config()
    return config.get('database', {})

def get_microsoft_graph_config():
    """Get Microsoft Graph API configuration from config.yaml"""
    config = load_config()
    return config.get('microsoft_graph', {})

def get_airflow_config():
    """Get Airflow configuration from config.yaml"""
    config = load_config()
    return config.get('airflow', {})

def get_api_config():
    """Get API configuration from config.yaml"""
    config = load_config()
    return config.get('api', {})

def get_etl_config():
    """Get ETL configuration from config.yaml"""
    config = load_config()
    return config.get('etl', {})

def get_logging_config():
    """Get logging configuration from config.yaml"""
    config = load_config()
    return config.get('logging', {})

def get_config_value(section: str, key: str = None):
    """
    Obtiene un valor específico de la configuración
    
    Args:
        section: Sección del config (ej: 'microsoft_graph', 'onedrive', etc.)
        key: Clave específica dentro de la sección (opcional)
    
    Returns:
        El valor solicitado o None si no existe
    """
    config = load_config()
    if not config:
        return None
    
    if section not in config:
        return None
    
    if key is None:
        return config[section]
    
    if key not in config[section]:
        return None
    
    return config[section][key]