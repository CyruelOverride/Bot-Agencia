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
QR_BASE_URL = os.getenv("QR_BASE_URL", "https://agencia-qr.vercel.app")


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
        # Verificar que el directorio existe
        if not os.path.exists(QR_BACK_DIR):
            print(f"⚠️ Directorio QR BACK no encontrado: {QR_BACK_DIR}")
            return None
        
        # Agregar el directorio QR BACK al path para importar el módulo
        if QR_BACK_DIR not in sys.path:
            sys.path.insert(0, QR_BACK_DIR)
        
        # Verificar que el archivo existe
        qr_generator_path = os.path.join(QR_BACK_DIR, "qr_generator.py")
        if not os.path.exists(qr_generator_path):
            print(f"⚠️ Archivo qr_generator.py no encontrado en: {QR_BACK_DIR}")
            return None
        
        # Importar el módulo de generación de QR usando importlib para mayor compatibilidad
        import importlib.util
        spec = importlib.util.spec_from_file_location("qr_generator", qr_generator_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"No se pudo cargar el módulo desde {qr_generator_path}")
        
        qr_generator_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(qr_generator_module)
        generar_qr = qr_generator_module.generar_qr
        
        # Generar el QR (todos apuntan al HTML estático, pero cada uno tiene su archivo)
        if base_url is None:
            base_url = QR_BASE_URL
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
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")
        return None
    except Exception as e:
        print(f"⚠️ Error al generar QR para {excursion_id}: {e}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")
        return None

