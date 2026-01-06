"""
Módulo helper para obtener y generar códigos QR de restaurantes/comercios.
Integra con el sistema QR BACK para generar y obtener QRs.
"""

import os
import sys
from typing import Optional

# Obtener la ruta base del proyecto (directorio padre de AGENCIA)
# Intentar múltiples rutas posibles para desarrollo y producción
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Rutas posibles para AGENCIA QR BACK
POSIBLES_RUTAS_QR_BACK = [
    os.path.join(BASE_DIR, "AGENCIA QR BACK"),  # Desarrollo local
    os.path.join(BASE_DIR, "..", "AGENCIA QR BACK"),  # Alternativa
    os.path.join(os.getcwd(), "AGENCIA QR BACK"),  # Desde directorio actual
    "AGENCIA QR BACK",  # Relativo al directorio actual
]

# Buscar el directorio que existe
QR_BACK_DIR = None
for ruta in POSIBLES_RUTAS_QR_BACK:
    ruta_abs = os.path.abspath(ruta)
    if os.path.exists(ruta_abs) and os.path.isdir(ruta_abs):
        QR_BACK_DIR = ruta_abs
        break

# Si no se encuentra, usar la primera opción por defecto
if QR_BACK_DIR is None:
    QR_BACK_DIR = os.path.abspath(os.path.join(BASE_DIR, "AGENCIA QR BACK"))

QR_CODES_DIR = os.path.join(QR_BACK_DIR, "qr_codes")

# URL base para los QRs (configurable mediante variable de entorno)
QR_BASE_URL = os.getenv("QR_BASE_URL", "https://agencia-qr.vercel.app")


def _generar_qr_directo(excursion_id: str, base_url: Optional[str] = None, usar_html_estatico: bool = True) -> Optional[str]:
    """
    Genera un QR directamente sin depender del módulo externo.
    Útil cuando AGENCIA QR BACK no está disponible (producción).
    """
    try:
        import qrcode
        
        # Asegurar que la carpeta existe
        if not os.path.exists(QR_CODES_DIR):
            os.makedirs(QR_CODES_DIR, exist_ok=True)
        
        # Construir URL
        if base_url is None:
            base_url = QR_BASE_URL
        
        # Asegurar que la URL tenga protocolo https://
        if not base_url.startswith(('http://', 'https://')):
            base_url = f"https://{base_url}"
        
        if usar_html_estatico:
            # Incluir el ID del restaurante en la URL para que el HTML estático sepa qué mostrar
            # Formato: https://agencia-qr.vercel.app?rest=rest_001
            url = f"{base_url.rstrip('/')}?rest={excursion_id}"
        else:
            url = f"{base_url.rstrip('/')}/{excursion_id}"
        
        print(f"🔗 URL generada para QR: {url}")
        
        # Generar QR con configuración mejorada (tamaño mayor para mejor legibilidad)
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,  # Mayor corrección de errores
            box_size=15,  # Aumentado de 10 a 15 para mejor legibilidad
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)
        
        # Crear imagen con formato RGB explícito para mejor compatibilidad
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convertir a RGB si es necesario (algunas versiones de PIL devuelven imágenes en modo diferente)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Guardar archivo con formato PNG explícito
        filename = f"{excursion_id}.png"
        filepath = os.path.join(QR_CODES_DIR, filename)
        img.save(filepath, format='PNG', optimize=False)
        
        # Verificar que el archivo se guardó correctamente
        if not os.path.exists(filepath):
            print(f"⚠️ Error: El archivo QR no se guardó correctamente: {filepath}")
            return None
        
        file_size = os.path.getsize(filepath)
        if file_size < 100:  # Un QR válido debería tener al menos 100 bytes
            print(f"⚠️ Advertencia: El archivo QR es muy pequeño ({file_size} bytes). Puede estar corrupto.")
        
        print(f"✅ QR generado: {filepath} ({file_size} bytes)")
        return os.path.abspath(filepath)
        
    except ImportError:
        print(f"⚠️ qrcode no está instalado. Ejecuta: pip install qrcode[pil]")
        return None
    except Exception as e:
        print(f"⚠️ Error al generar QR directamente: {e}")
        return None


def debe_enviar_qr(categoria: str) -> bool:
    """
    Verifica si se debe enviar QR para una categoría específica.
    Solo se envía QR para restaurantes y comercios.
    
    Args:
        categoria: Categoría de la excursión (ej: "restaurantes", "comercios")
        
    Returns:
        bool: True si se debe enviar QR, False en caso contrario
    """
    return categoria in ["museo","restaurantes", "comercios"]


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
    
    # Si el archivo ya existe, verificar que sea válido antes de retornarlo
    # NOTA: Los QRs antiguos pueden tener URLs incorrectas (sin el ID del restaurante)
    # Si necesitas regenerar todos los QRs, elimina la carpeta qr_codes
    if os.path.exists(qr_filepath):
        file_size = os.path.getsize(qr_filepath)
        # Si el archivo es muy pequeño (menos de 100 bytes), probablemente está corrupto
        if file_size < 100:
            print(f"⚠️ Archivo QR existente parece corrupto ({file_size} bytes). Regenerando...")
            try:
                os.remove(qr_filepath)
            except Exception as e:
                print(f"⚠️ No se pudo eliminar archivo corrupto: {e}")
        else:
            # Verificar que sea un PNG válido
            try:
                with open(qr_filepath, 'rb') as f:
                    header = f.read(8)
                    if header[:8] == b'\x89PNG\r\n\x1a\n':
                        print(f"✅ QR existente válido: {qr_filepath} ({file_size} bytes)")
                        print(f"⚠️ NOTA: Si el QR no funciona correctamente, elimina este archivo para regenerarlo con la nueva URL")
                        return os.path.abspath(qr_filepath)
                    else:
                        print(f"⚠️ Archivo QR no es un PNG válido. Regenerando...")
                        try:
                            os.remove(qr_filepath)
                        except Exception as e:
                            print(f"⚠️ No se pudo eliminar archivo inválido: {e}")
            except Exception as e:
                print(f"⚠️ Error al verificar archivo QR: {e}. Regenerando...")
                try:
                    os.remove(qr_filepath)
                except:
                    pass
    
    # Si no existe, generarlo
    try:
        # Buscar qr_generator.py en múltiples ubicaciones
        qr_generator_path = None
        posibles_rutas_generator = [
            os.path.join(QR_BACK_DIR, "qr_generator.py"),
            os.path.join(BASE_DIR, "AGENCIA QR BACK", "qr_generator.py"),
            os.path.join(os.getcwd(), "AGENCIA QR BACK", "qr_generator.py"),
        ]
        
        for ruta in posibles_rutas_generator:
            if os.path.exists(ruta):
                qr_generator_path = ruta
                break
        
        # Si no encontramos el módulo externo, generar QR directamente
        if qr_generator_path is None:
            print(f"⚠️ qr_generator.py no encontrado, generando QR directamente")
            return _generar_qr_directo(excursion_id, base_url, usar_html_estatico)
        
        # Importar el módulo de generación de QR usando importlib
        import importlib.util
        spec = importlib.util.spec_from_file_location("qr_generator", qr_generator_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"No se pudo cargar el módulo desde {qr_generator_path}")
        
        qr_generator_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(qr_generator_module)
        generar_qr = qr_generator_module.generar_qr
        
        # Asegurar que la carpeta de QRs existe
        if not os.path.exists(QR_CODES_DIR):
            os.makedirs(QR_CODES_DIR, exist_ok=True)
        
        # Modificar temporalmente el QR_CODES_DIR en el módulo importado
        qr_generator_module.QR_CODES_DIR = QR_CODES_DIR
        
        # Generar el QR (todos apuntan al HTML estático, pero cada uno tiene su archivo)
        if base_url is None:
            base_url = QR_BASE_URL
        ruta_relativa = generar_qr(excursion_id, base_url, usar_html_estatico=usar_html_estatico)
        
        # Convertir a ruta absoluta
        if os.path.isabs(ruta_relativa):
            return ruta_relativa
        else:
            # Si es relativa, construir la ruta absoluta
            return os.path.abspath(ruta_relativa)
            
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

