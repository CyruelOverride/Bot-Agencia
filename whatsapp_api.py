import os
import requests
from typing import Optional
from Util.get_type import get_type

WHATSAPP_API_URL = "https://graph.facebook.com/v22.0"
WHATSAPP_ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN") or "<TU_TOKEN_DE_ACCESO>"
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN") or "Chacalitas2025"
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "871681339360716")


def normalizar_numero_telefono(numero: str) -> str:
    numero = numero.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    if not numero.startswith("+"):
        numero = "+" + numero
    return numero


def enviar_mensaje_whatsapp(numero, mensaje):
    url = f"{WHATSAPP_API_URL}/{WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }

    if isinstance(mensaje, str):
        data = {
            "messaging_product": "whatsapp",
            "to": numero,
            "type": "text",
            "text": {"body": mensaje},
        }
    else:
        data = mensaje  

    response = requests.post(url, headers=headers, json=data)
    print(f" Enviado a {numero}")
    print(" Estado:", response.status_code)

    try:
        res_json = response.json()
        return {
            "success": response.status_code == 200,
            "error": res_json.get("error"),
        }
    except Exception as e:
        print(" Error", e)
        return {"success": False, "error": str(e)}


def enviar_imagen_whatsapp(numero, ruta_o_url_imagen, caption=""):
    """
    Envía una imagen por WhatsApp.
    Acepta tanto rutas locales como URLs públicas.
    
    Args:
        numero: Número de teléfono del destinatario
        ruta_o_url_imagen: Ruta local del archivo o URL pública de la imagen
        caption: Texto opcional que acompaña la imagen (máx 1024 caracteres)
    """
    url = f"{WHATSAPP_API_URL}/{WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    
    # Detectar si es URL o ruta local
    es_url = ruta_o_url_imagen.startswith(('http://', 'https://'))
    
    if es_url:
        # Usar URL directamente (más simple y eficiente)
        data = {
            "messaging_product": "whatsapp",
            "to": numero,
            "type": "image",
            "image": {
                "link": ruta_o_url_imagen
            }
        }
        
        if caption:
            data["image"]["caption"] = caption
        
        try:
            response = requests.post(url, headers=headers, json=data)
            print(f"➡️ Enviando imagen desde URL a {numero}")
            print("📨 Estado:", response.status_code)
            
            try:
                res_json = response.json()
                if response.status_code == 200:
                    print("✅ Imagen enviada exitosamente")
                    return {
                        "success": True,
                        "message_id": res_json.get("messages", [{}])[0].get("id")
                    }
                else:
                    print(f"❌ Error enviando imagen: {res_json.get('error', 'Error desconocido')}")
                    return {
                        "success": False,
                        "error": res_json.get("error", "Error desconocido")
                    }
            except Exception as e:
                print("⚠️ Error al interpretar la respuesta:", e)
                return {"success": False, "error": str(e)}
        except Exception as e:
            print(f"❌ Error enviando imagen desde URL: {e}")
            return {"success": False, "error": str(e)}
    else:
        # Código original para archivos locales (subir a media de WhatsApp)
        _imagen = f"{WHATSAPP_API_URL}/{WHATSAPP_PHONE_NUMBER_ID}/media"
        
        try:
            with open(ruta_o_url_imagen, 'rb') as img_file:
                files = {
                    'file': (os.path.basename(ruta_o_url_imagen), img_file, 'image/png'),
                    'messaging_product': (None, 'whatsapp'),
                }
                upload_headers = {
                    "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
                }
                
                print(f"📤 Subiendo imagen local: {ruta_o_url_imagen}")
                respuesta = requests.post(_imagen, headers=upload_headers, files=files)
                
                if respuesta.status_code != 200:
                    print(f"❌ Error subiendo imagen: {respuesta.status_code}")
                    print(f"   Respuesta: {respuesta.text}")
                    return {"success": False, "error": f"Error al subir imagen: {respuesta.text}"}
                
                _imagen = respuesta.json().get("id")
                print(f"✅ Imagen subida. Media ID: {_imagen}")
            
            data = {
                "messaging_product": "whatsapp",
                "to": numero,
                "type": "image",
                "image": {
                    "id": _imagen
                }
            }
            
            if caption:
                data["image"]["caption"] = caption
            
            response = requests.post(url, headers=headers, json=data)
            print(f"➡️ Enviando imagen a {numero}")
            print("📨 Estado:", response.status_code)
            
            try:
                res_json = response.json()
                if response.status_code == 200:
                    print("✅ Imagen enviada exitosamente")
                    return {
                        "success": True,
                        "message_id": res_json.get("messages", [{}])[0].get("id")
                    }
                else:
                    return {
                        "success": False,
                        "error": res_json.get("error", "Error desconocido")
                    }
            except Exception as e:
                print("⚠️ Error al interpretar la respuesta:", e)
                return {"success": False, "error": str(e)}
                
        except FileNotFoundError:
            print(f"❌ Archivo no encontrado: {ruta_o_url_imagen}")
            return {"success": False, "error": f"Archivo no encontrado: {ruta_o_url_imagen}"}
        except Exception as e:
            print(f"❌ Error enviando imagen: {e}")
            return {"success": False, "error": str(e)}


def obtener_nombre_contacto(numero: str) -> Optional[str]:
    """
    Obtiene el nombre del contacto desde WhatsApp Business API.
    Retorna el nombre si está disponible, None en caso contrario.
    """
    try:
        # Normalizar número
        numero_normalizado = normalizar_numero_telefono(numero)
        
        # La API de WhatsApp Business permite obtener información del contacto
        # Nota: Esto requiere que el contacto haya iniciado conversación
        # Alternativamente, podemos extraer el nombre del webhook si está disponible
        
        # Por ahora, retornamos None ya que la API de contactos requiere permisos especiales
        # El nombre se puede obtener del webhook cuando el usuario envía un mensaje
        return None
        
    except Exception as e:
        print(f"⚠️ Error al obtener nombre de contacto: {e}")
        return None


def extraer_nombre_del_webhook(data: dict) -> Optional[str]:
    """
    Extrae el nombre del contacto desde los datos del webhook de WhatsApp.
    El nombre puede estar en contacts dentro del webhook.
    """
    try:
        entry = data.get("entry", [{}])[0]
        value = entry.get("changes", [{}])[0].get("value", {})
        contacts = value.get("contacts", [])
        
        if contacts and len(contacts) > 0:
            profile = contacts[0].get("profile", {})
            nombre = profile.get("name")
            if nombre:
                return nombre
        
        return None
        
    except Exception as e:
        print(f"⚠️ Error al extraer nombre del webhook: {e}")
        return None


def procesar_mensaje_recibido(data):
    try:
        if data.get("object") != "whatsapp_business_account":
            return None

        entry = data.get("entry", [{}])[0]
        value = entry.get("changes", [{}])[0].get("value", {})

        if "statuses" in value:
            return None

        messages = value.get("messages", [])
        if not messages:
            return None

        message = messages[0]
        numero = message.get("from")

        if numero == WHATSAPP_PHONE_NUMBER_ID:
            print(" Ignorando mensaje del propio bot.")
            return None

        tipo, contenido = get_type(message)
        
        if tipo == "audio":
            tipo = "text"
        
        return numero, contenido, tipo

    except Exception as e:
        print(f"⚠️ Error al procesar mensaje recibido: {e}")
        return None
