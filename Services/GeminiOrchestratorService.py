import os
import json
from typing import Dict, Optional, List
from google import genai
from google.genai import types
from Models.usuario import Usuario
from Models.perfil_usuario import PerfilUsuario

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
Perfil actual del usuario:
- Tipo de viaje: {perfil.tipo_viaje or 'No especificado'}
- Acompañantes: {perfil.acompanantes or 'No especificado'}
- Preferencias comida: {perfil.preferencias_comida or 'No especificado'}
- Presupuesto: {perfil.presupuesto or 'No especificado'}
- Interés en regalos: {perfil.interes_regalos or 'No especificado'}
- Duración estadía: {perfil.duracion_estadia or 'No especificado'} días
"""
        
        prompt = f"""Eres un asistente de viaje que ayuda a usuarios a planificar su estadía en una ciudad.

Estado actual de la conversación: {estado_actual}
Intereses seleccionados: {', '.join(usuario.intereses) if usuario.intereses else 'Ninguno'}
{contexto_perfil}

Mensaje del usuario: "{mensaje}"

Tu tarea es:
1. Identificar la intención del mensaje
2. Si el usuario está respondiendo una pregunta sobre su perfil, detectar qué campo está respondiendo
3. Extraer el valor de la respuesta
4. Generar una respuesta natural y amigable

Campos posibles del perfil:
- tipo_viaje: "solo", "pareja", "familia", "amigos", "negocios"
- acompanantes: "solo", "pareja", "familia", "amigos"
- preferencias_comida: "local", "internacional", "vegetariano", "vegano", "sin_restricciones"
- presupuesto: "economico", "medio", "alto", "premium"
- interes_regalos: true/false
- duracion_estadia: número de días

Responde SOLO con un JSON válido en este formato:
{{
    "intencion": "responder_perfil" | "pregunta" | "saludo" | "otro",
    "respuesta_detectada": true/false,
    "campo_perfil": "nombre_del_campo" o null,
    "valor_detectado": "valor_extraido" o null,
    "mensaje_respuesta": "respuesta natural y amigable" o null
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
        """
        perfil = usuario.perfil
        if not perfil:
            return "¿Qué tipo de viaje estás haciendo? (solo, pareja, familia, amigos, negocios)"
        
        campos_faltantes = perfil.obtener_campos_faltantes()
        
        # Priorizar preguntas según intereses
        preguntas_prioritarias = []
        
        if "restaurantes" in intereses and "preferencias_comida" in campos_faltantes:
            preguntas_prioritarias.append(("preferencias_comida", "¿Qué tipo de comida te gusta más? (local, internacional, vegetariano, vegano)"))
        
        if "compras" in intereses or "regalos" in intereses and "interes_regalos" in campos_faltantes:
            preguntas_prioritarias.append(("interes_regalos", "¿Buscás algo para vos o para regalar?"))
        
        if "acompanantes" in campos_faltantes:
            preguntas_prioritarias.append(("acompanantes", "¿Viajás solo o acompañado?"))
        
        if "presupuesto" in campos_faltantes:
            preguntas_prioritarias.append(("presupuesto", "¿Qué presupuesto tenés en mente? (económico, medio, alto, premium)"))
        
        if "duracion_estadia" in campos_faltantes:
            preguntas_prioritarias.append(("duracion_estadia", "¿Cuántos días vas a estar en la ciudad?"))
        
        if "tipo_viaje" in campos_faltantes:
            preguntas_prioritarias.append(("tipo_viaje", "¿Qué tipo de viaje estás haciendo?"))
        
        if preguntas_prioritarias:
            return preguntas_prioritarias[0][1]
        
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
Perfil del usuario:
- Tipo de viaje: {perfil.tipo_viaje or 'No especificado'}
- Acompañantes: {perfil.acompanantes or 'No especificado'}
- Preferencias comida: {perfil.preferencias_comida or 'No especificado'}
- Presupuesto: {perfil.presupuesto or 'No especificado'}
- Duración: {perfil.duracion_estadia or 'No especificado'} días
"""
        
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

Genera un resumen natural, amigable y personalizado (máximo 200 palabras) que:
1. Mencione el nombre del usuario si está disponible
2. Haga referencia a sus intereses y preferencias
3. Presente las recomendaciones de forma entusiasta pero no invasiva
4. Use emojis apropiados
5. Sea conversacional y cálido

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

