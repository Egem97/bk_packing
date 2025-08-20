import pytz
from datetime import datetime

def get_peru_datetime():
    """
    Obtiene la fecha y hora actual en zona horaria de Perú
    """
    peru_tz = pytz.timezone('America/Lima')
    return datetime.now(peru_tz)