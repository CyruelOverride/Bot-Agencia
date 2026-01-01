import os
import json
from typing import Dict, Optional, List
from google import genai
from google.genai import types
from Models.usuario import Usuario
from Models.perfil_usuario import PerfilUsuario
from Util.estado import get_pregunta_actual

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


class GeminiOrchestratorService:
    @staticmethod
    def interpretar_mensaje_usuario(
        mensaje: str,
        usuario: Usuario,
        contexto_adicional: Optional[Dict] = None
    ) -> Dict:
        """
        Interpreta el mensaje del usuario usando Gemini.
        Retorna: {
            "intencion": str,
            "respuesta_detectada": bool,
            "campo_perfil": Optional[str],
            "valor_detectado": Optional[any],
            "mensaje_respuesta": Optional[str]
        }
        """
        estado_actual = usuario.estado_conversacion
        perfil = usuario.perfil
        
        contexto_perfil = ""
        if perfil:
            contexto_perfil = f"""
Perfil actual:
- Tipo de viaje: {perfil.tipo_viaje or 'No especificado'}
- Acompañantes: {perfil.acompanantes or 'No especificado'}
- Duración: {perfil.duracion_estadia or 'No especificado'} días
- Preferencias comida: {perfil.preferencias_comida or 'No especificado'}
- Interés regalos: {perfil.interes_regalos or 'No especificado'}
- Interés ropa: {perfil.interes_ropa or 'No especificado'}
- Viaja con niños: {perfil.viaja_con_ninos or 'No especificado'}
"""
        
        # Obtener pregunta actual para contexto
        pregunta_actual = get_pregunta_actual(usuario.telefono) if hasattr(usuario, 'telefono') else None
        
        prompt = f"""Eres un asistente de viaje que ayuda a usuarios a planificar su estadía en una ciudad.

Estado actual: {estado_actual}
Intereses: {', '.join(usuario.intereses) if usuario.intereses else 'Ninguno'}
{contexto_perfil}
Pregunta actual que se está haciendo: {pregunta_actual or 'Ninguna específica'}

Mensaje del usuario: "{mensaje}"

IMPORTANTE: Si el usuario está respondiendo una pregunta, detecta SOLO UN campo a la vez. 
Si el mensaje menciona múltiples campos, prioriza el que corresponde a la pregunta actual.

Tu tarea:
1. Identificar si el mensaje responde a la pregunta actual
2. Detectar SOLO UN campo del perfil (el más relevante según la pregunta actual)
3. Extraer el valor correspondiente
4. NO generar mensaje_respuesta si no es necesario (solo si es muy relevante)

Campos posibles:
- tipo_viaje: "solo", "pareja", "familia", "amigos", "negocios"
- acompanantes: "solo", "pareja", "familia", "amigos"
- duracion_estadia: número entero (días)
- preferencias_comida: "local", "internacional", "vegetariano", "vegano", "sin_restricciones"
- interes_regalos: true/false
- interes_ropa: true/false
- viaja_con_ninos: true/false (solo si acompanantes="familia")

REGLA CRÍTICA: Si el mensaje menciona "familia" o "con mi familia", puede referirse a:
- tipo_viaje="familia" (si la pregunta actual es sobre tipo de viaje)
- acompanantes="familia" (si la pregunta actual es sobre acompañantes)
- viaja_con_ninos=true (si ya tiene acompanantes="familia" y la pregunta es sobre niños)

SIEMPRE prioriza el campo que corresponde a la pregunta actual.

Responde SOLO con JSON válido:
{{
    "intencion": "responder_perfil" | "pregunta" | "saludo" | "otro",
    "respuesta_detectada": true/false,
    "campo_perfil": "nombre_del_campo" o null,
    "valor_detectado": "valor_extraido" o null,
    "mensaje_respuesta": null
}}"""

        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[prompt, "Responde SOLO con JSON válido, sin explicaciones adicionales."],
                config=types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(thinking_budget=0)
                )
            )
            
            response_text = response.text.strip()
            
            # Limpiar respuesta de markdown si existe
            if "```json" in response_text:
                start = response_text.find("```json") + 7
                end = response_text.find("```", start)
                if end != -1:
                    response_text = response_text[start:end].strip()
            elif "```" in response_text:
                start = response_text.find("```") + 3
                end = response_text.find("```", start)
                if end != -1:
                    response_text = response_text[start:end].strip()
            
            # Extraer JSON
            first_brace = response_text.find("{")
            last_brace = response_text.rfind("}")
            if first_brace != -1 and last_brace != -1:
                response_text = response_text[first_brace:last_brace + 1]
            
            resultado = json.loads(response_text)
            return resultado
            
        except Exception as e:
            print(f"⚠️ Error al interpretar mensaje con Gemini: {e}")
            return {
                "intencion": "otro",
                "respuesta_detectada": False,
                "campo_perfil": None,
                "valor_detectado": None,
                "mensaje_respuesta": None
            }
    
    @staticmethod
    def detectar_respuesta_implicita(
        mensaje: str,
        pregunta_actual: Optional[str],
        perfil: Optional[PerfilUsuario]
    ) -> Optional[Dict]:
        """
        Detecta si el mensaje contiene una respuesta implícita a la pregunta actual.
        Retorna: {"campo": str, "valor": any} o None
        """
        if not pregunta_actual:
            return None
        
        prompt = f"""El usuario está respondiendo a esta pregunta sobre su perfil de viaje: "{pregunta_actual}"

Mensaje del usuario: "{mensaje}"

¿El mensaje contiene una respuesta a la pregunta? Si es así, extrae el valor.

Responde SOLO con JSON:
{{
    "tiene_respuesta": true/false,
    "campo": "nombre_del_campo" o null,
    "valor": "valor_extraido" o null
}}"""

        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[prompt, "Responde SOLO con JSON válido."],
                config=types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(thinking_budget=0)
                )
            )
            
            response_text = response.text.strip()
            if "```json" in response_text:
                start = response_text.find("```json") + 7
                end = response_text.find("```", start)
                if end != -1:
                    response_text = response_text[start:end].strip()
            
            first_brace = response_text.find("{")
            last_brace = response_text.rfind("}")
            if first_brace != -1 and last_brace != -1:
                response_text = response_text[first_brace:last_brace + 1]
            
            resultado = json.loads(response_text)
            
            if resultado.get("tiene_respuesta"):
                return {
                    "campo": resultado.get("campo"),
                    "valor": resultado.get("valor")
                }
            
            return None
            
        except Exception as e:
            print(f"⚠️ Error al detectar respuesta implícita: {e}")
            return None
    
    @staticmethod
    def generar_pregunta_siguiente(
        usuario: Usuario,
        intereses: List[str]
    ) -> Optional[str]:
        """
        Genera la siguiente pregunta conversacional basada en los intereses y perfil actual.
        Retorna la pregunta como string o None si ya hay suficiente información.
        
        Prioriza preguntas según:
        1. Campos obligatorios primero (tipo_viaje, acompanantes, duracion_estadia)
        2. Campos condicionales según intereses
        """
        perfil = usuario.perfil
        if not perfil:
            return "¿Qué tipo de viaje estás haciendo?"
        
        # Obtener campos faltantes considerando intereses (nueva lógica)
        campos_faltantes = perfil.obtener_campos_faltantes(intereses)
        
        if not campos_faltantes:
            return None  # Perfil completo
        
        # Mapeo de campos a preguntas (tono directo, amigable, medio formal)
        preguntas_map = {
            "tipo_viaje": "¿Qué tipo de viaje estás haciendo? (solo, con pareja, con familia, con amigos, negocios)",
            "duracion_estadia": "¿Cuántos días vas a estar?",
            "preferencias_comida": "¿Qué tipo de comida preferís?",
            "interes_regalos": "¿Buscás algo para vos o para regalar?",
            "interes_ropa": "¿Te interesa comprar ropa?",
            "interes_tipo_comercios": "¿Qué tipo de comercios te interesan?",
            "interes_tipo_cultura": "¿Qué tipo de actividades culturales te interesan?",
            "viaja_con_ninos": "¿Viajás con niños o familiares chicos?"
        }
        
        # Priorizar: primero campos obligatorios, luego condicionales
        campos_obligatorios = ["tipo_viaje", "duracion_estadia"]
        campos_condicionales = ["preferencias_comida", "interes_regalos", "interes_ropa", "interes_tipo_comercios", "interes_tipo_cultura"]
        
        # Solo agregar "viaja_con_ninos" si el tipo de viaje es "familia"
        if perfil.tipo_viaje == "familia":
            campos_condicionales.append("viaja_con_ninos")
        
        # Buscar primero campos obligatorios faltantes
        for campo in campos_obligatorios:
            if campo in campos_faltantes:
                return preguntas_map.get(campo, f"¿Puedes completar {campo}?")
        
        # Luego campos condicionales
        for campo in campos_condicionales:
            if campo in campos_faltantes:
                return preguntas_map.get(campo, f"¿Puedes completar {campo}?")
        
        # Si hay algún campo faltante que no está en el mapa, preguntar genérico
        if campos_faltantes:
            return f"¿Puedes completar {campos_faltantes[0]}?"
        
        return None
    
    @staticmethod
    def generar_resumen_plan(
        usuario: Usuario,
        excursiones: List
    ) -> str:
        """
        Genera un resumen personalizado del plan usando Gemini.
        """
        intereses_texto = ", ".join(usuario.intereses) if usuario.intereses else "varios intereses"
        perfil_texto = ""
        
        if usuario.perfil:
            perfil = usuario.perfil
            perfil_texto = f"""
Perfil:
- Tipo de viaje: {perfil.tipo_viaje or 'No especificado'}
- Duración: {perfil.duracion_estadia or 'No especificado'} días"""
            
            # Agregar campos condicionales según intereses
            if "restaurantes" in usuario.intereses:
                perfil_texto += f"\n- Preferencias comida: {perfil.preferencias_comida or 'No especificado'}"
            
            if "compras" in usuario.intereses:
                perfil_texto += f"\n- Interés regalos: {perfil.interes_regalos or 'No especificado'}"
                perfil_texto += f"\n- Interés ropa: {perfil.interes_ropa or 'No especificado'}"
            
            if perfil.viaja_con_ninos is not None:
                perfil_texto += f"\n- Viaja con niños: {perfil.viaja_con_ninos}"
        
        excursiones_texto = "\n".join([
            f"- {exc.nombre} ({exc.categoria}): {exc.descripcion}"
            for exc in excursiones[:10]  # Limitar a 10 para no sobrecargar
        ])
        
        prompt = f"""Eres un asistente de viaje. Genera un resumen personalizado y amigable del plan de viaje.

Usuario: {usuario.nombre or 'Usuario'}
Ciudad: {usuario.ciudad}
Intereses: {intereses_texto}
{perfil_texto}

Excursiones recomendadas:
{excursiones_texto}

Genera un resumen directo, amigable y medio formal (máximo 150 palabras) que:
1. Sea conciso y no robe tiempo al usuario
2. Mencione el nombre si está disponible
3. Haga referencia breve a sus intereses
4. Presente las recomendaciones de forma clara y directa
5. Use emojis moderados
6. Mantenga tono amigable pero profesional

Responde SOLO con el texto del resumen, sin explicaciones adicionales."""

        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[prompt],
                config=types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(thinking_budget=0)
                )
            )
            
            return response.text.strip()
            
        except Exception as e:
            print(f"⚠️ Error al generar resumen con Gemini: {e}")
            return f"Perfecto {usuario.nombre or ''}, armé un plan pensado especialmente para vos basado en tus intereses: {intereses_texto}."
    
    @staticmethod
    def generar_respuesta_amigable(
        mensaje: str,
        usuario: Usuario,
        contexto_estado: str = None
    ) -> str:
        """
        Genera una respuesta amigable usando Gemini cuando el usuario envía texto libre
        que no coincide con keywords específicas.
        
        Args:
            mensaje: Mensaje del usuario
            usuario: Usuario actual
            contexto_estado: Estado actual del bot (opcional)
        
        Returns:
            Respuesta amigable generada por Gemini
        """
        try:
            nombre = usuario.nombre or "viajero"
            ciudad = usuario.ciudad or "Colonia"
            
            contexto = ""
            if contexto_estado:
                contexto = f"\nEstado actual del bot: {contexto_estado}"
            
            if usuario.perfil:
                perfil_info = f"""
Perfil del usuario:
- Tipo de viaje: {usuario.perfil.tipo_viaje or 'No especificado'}
- Acompañantes: {usuario.perfil.acompanantes or 'No especificado'}
- Duración: {usuario.perfil.duracion_estadia or 'No especificado'} días
"""
            else:
                perfil_info = "El usuario aún no ha completado su perfil."
            
            prompt = f"""Eres un asistente virtual amigable y profesional que ayuda a usuarios a planificar su viaje a {ciudad}.

Contexto:
{perfil_info}
{contexto}

Mensaje del usuario: "{mensaje}"

Tu tarea es generar una respuesta amigable, útil y directa. Debes:
1. Ser amigable pero profesional (tono medio formal)
2. Ser conciso (no más de 3-4 líneas)
3. Si el mensaje es una pregunta, intentar responderla de forma útil
4. Si no entiendes bien, ofrecer ayuda de forma amigable
5. Si es un saludo, responder cordialmente
6. Si es una consulta sobre lugares/restaurantes/actividades, ser útil y sugerir que puede ajustar su plan

NO uses emojis excesivos (máximo 1-2 si es apropiado).
NO ofrezcas opciones que no están disponibles.
Mantén un tono cálido pero directo.

Responde SOLO con el texto de la respuesta, sin explicaciones adicionales."""

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[prompt],
                config=types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(thinking_budget=0)
                )
            )
            
            respuesta = response.text.strip()
            
            # Limpiar la respuesta si tiene formato JSON o comillas
            if respuesta.startswith('"') and respuesta.endswith('"'):
                respuesta = respuesta[1:-1]
            if respuesta.startswith("'") and respuesta.endswith("'"):
                respuesta = respuesta[1:-1]
            
            return respuesta
            
        except Exception as e:
            print(f"⚠️ Error al generar respuesta amigable con Gemini: {e}")
            # Respuesta de fallback amigable
            return (
                "Gracias por tu mensaje. Si necesitás ayuda con tu plan de viaje, "
                "podés ajustar tu plan, generar uno nuevo, o consultarme sobre lugares y actividades. "
                "¿En qué te puedo ayudar?"
            )

