"""
Módulo helper para obtener y generar códigos QR de restaurantes/comercios.
Integra con el sistema QR BACK para generar y obtener QRs.
"""

import os
import sys
from typing import Optional

# Obtener la ruta base del proyecto (directorio padre de AGENCIA)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QR_BACK_DIR = os.path.join(BASE_DIR, "AGENCIA QR BACK")
QR_CODES_DIR = os.path.join(QR_BACK_DIR, "qr_codes")

# URL base para los QRs (configurable mediante variable de entorno)
QR_BASE_URL = os.getenv("QR_BASE_URL", "http://localhost:8000")


def debe_enviar_qr(categoria: str) -> bool:
    """
    Verifica si se debe enviar QR para una categoría específica.
    Solo se envía QR para restaurantes y comercios.
    
    Args:
        categoria: Categoría de la excursión (ej: "restaurantes", "comercios")
        
    Returns:
        bool: True si se debe enviar QR, False en caso contrario
    """
    return categoria in ["restaurantes", "comercios"]


def obtener_ruta_qr(excursion_id: str, base_url: Optional[str] = None, usar_html_estatico: bool = True) -> Optional[str]:
    """
    Obtiene la ruta del archivo QR para un restaurante/comercio.
    Si el QR no existe, lo genera automáticamente.
    
    Args:
        excursion_id: ID de la excursión (ej: "rest_001", "com_001")
        base_url: URL base donde está alojado el HTML estático (opcional, para cuando uses un servidor)
        usar_html_estatico: Si True, genera QR que apunta al HTML estático. Si False, apunta al backend.
        
    Returns:
        str: Ruta absoluta del archivo QR, o None si hay error
    """
    # Ruta del archivo QR (cada restaurante tiene su propio archivo QR, pero todos apuntan al mismo HTML)
    filename = f"{excursion_id}.png"
    qr_filepath = os.path.join(QR_CODES_DIR, filename)
    
    # Si el archivo ya existe, retornar su ruta absoluta
    if os.path.exists(qr_filepath):
        return os.path.abspath(qr_filepath)
    
    # Si no existe, generarlo
    try:
        # Agregar el directorio QR BACK al path para importar el módulo
        if QR_BACK_DIR not in sys.path:
            sys.path.insert(0, QR_BACK_DIR)
        
        # Importar el módulo de generación de QR
        from qr_generator import generar_qr
        
        # Generar el QR (todos apuntan al HTML estático, pero cada uno tiene su archivo)
        ruta_relativa = generar_qr(excursion_id, base_url, usar_html_estatico=usar_html_estatico)
        
        # Convertir a ruta absoluta
        if os.path.isabs(ruta_relativa):
            return ruta_relativa
        else:
            # Si es relativa, construir la ruta absoluta
            return os.path.abspath(os.path.join(QR_BACK_DIR, ruta_relativa))
            
    except ImportError as e:
        print(f"⚠️ Error al importar qr_generator: {e}")
        print(f"   Asegúrate de que qrcode[pil] esté instalado")
        return None
    except Exception as e:
        print(f"⚠️ Error al generar QR para {excursion_id}: {e}")
        return None

