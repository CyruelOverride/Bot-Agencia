from typing import Any, Optional, Dict, Callable
from datetime import datetime
from whatsapp_api import enviar_mensaje_whatsapp, extraer_nombre_del_webhook
from Util.estado import (
    get_estado, reset_estado, get_waiting_for, set_waiting_for, clear_waiting_for,
    get_estado_bot, set_estado_bot, ESTADOS_BOT,
    get_intereses_seleccionados, set_intereses_seleccionados,
    get_pregunta_actual, set_pregunta_actual, clear_pregunta_actual
)
from Util.calificacion_util import manejar_calificacion
from Services.UsuarioService import UsuarioService
from Services.ExcursionService import ExcursionService
from Services.PlanViajeService import PlanViajeService
from Services.GeminiOrchestratorService import GeminiOrchestratorService
from Models.usuario import Usuario


class Chat:
    def __init__(self, id_chat=None, id_cliente=None):
        self.id_chat = id_chat
        self.id_cliente = id_cliente
        self.conversation_data: Dict[str, Any] = {}
        
        # Mapeo de funciones de flujo
        self.function_map = {
            "flujo_inicio": self.flujo_inicio,
            "flujo_seleccion_intereses": self.flujo_seleccion_intereses,
            "flujo_armando_perfil": self.flujo_armando_perfil,
            "flujo_generando_plan": self.flujo_generando_plan,
            "flujo_plan_presentado": self.flujo_plan_presentado,
            "flujo_seguimiento": self.flujo_seguimiento
        }
        
        self.function_graph = {
            "ayuda": {
                'function': self.funcion_ayuda,
                'name': 'funcion_ayuda',
                'doc': self.funcion_ayuda.__doc__,
                'command': 'ayuda'
            },
            "reiniciar": {
                'function': self.funcion_reiniciar,
                'name': 'funcion_reiniciar',
                'doc': self.funcion_reiniciar.__doc__,
                'command': 'reiniciar'
            }
        }
    
    def get_session(self, numero):
        estado = get_estado(numero)
        return estado
    
    def reset_session(self, numero):
        reset_estado(numero)
    
    def clear_state(self, numero):
        self.reset_session(numero)
        self.reset_conversation(numero)
    
    def set_waiting_for(self, numero, func_name: str, context_data=None):
        set_waiting_for(numero, func_name, context_data)
        print(f"{numero}: Esperando respuesta para: {func_name}")
    
    def set_conversation_data(self, key: str, value: Any):
        self.conversation_data[key] = value
    
    def get_conversation_data(self, key: str, default: Any = None) -> Any:
        return self.conversation_data.get(key, default)
    
    def clear_conversation_data(self):
        self.conversation_data = {}
    
    def reset_conversation(self, numero):
        clear_waiting_for(numero)
        self.conversation_data = {}
        print("Conversación reseteada.")
    
    def is_waiting_response(self, numero) -> bool:
        return get_waiting_for(numero) is not None
    
    def get_waiting_function(self, numero) -> Optional[Callable]:
        func_name = get_waiting_for(numero)
        if func_name and func_name in self.function_map:
            return self.function_map[func_name]
        return None
    
    def funcion_ayuda(self, numero, texto):
        """Muestra ayuda sobre cómo usar el bot"""
        ayuda_texto = (
            "🤖 *Bot Asistente de Viaje*\n\n"
            "Soy tu guía virtual para ayudarte a disfrutar al máximo tu estadía.\n\n"
            "*Comandos disponibles:*\n"
            "/ayuda - Mostrar esta ayuda\n"
            "/reiniciar - Comenzar de nuevo\n\n"
            "Solo escribime y te ayudo a armar tu plan personalizado 😊"
        )
        return enviar_mensaje_whatsapp(numero, ayuda_texto)
    
    def funcion_reiniciar(self, numero, texto):
        """Reinicia la conversación"""
        self.clear_state(numero)
        usuario = UsuarioService.obtener_usuario_por_telefono(numero)
        if usuario:
            usuario.estado_conversacion = ESTADOS_BOT["INICIO"]
            usuario.intereses = []
            usuario.perfil = None
            UsuarioService.actualizar_usuario(usuario)
        return self.flujo_inicio(numero, texto)
    
    def handle_text(self, numero, texto):
        """Maneja mensajes de texto del usuario"""
        texto_strip = texto.strip()
        texto_lower = texto_strip.lower()
        
        # Manejar calificaciones (mantener funcionalidad existente)
        if texto_strip.startswith("calificar_"):
            return manejar_calificacion(numero, texto_strip)
        
        # Obtener o crear usuario
        usuario = UsuarioService.obtener_o_crear_usuario(numero)
        
        if not self.id_chat:
            self.id_chat = f"chat_{numero}"
        
        # Comandos especiales
        if texto_lower in ("/ayuda", "ayuda", "help"):
            return self.funcion_ayuda(numero, texto)
        
        if texto_lower in ("/reiniciar", "reiniciar", "empezar de nuevo", "comenzar"):
            return self.funcion_reiniciar(numero, texto)
        
        if texto_lower in ("cancelar", "salir", "cancel"):
            self.clear_state(numero)
            usuario.estado_conversacion = ESTADOS_BOT["INICIO"]
            UsuarioService.actualizar_usuario(usuario)
            return enviar_mensaje_whatsapp(numero, "✅ Conversación cancelada. Escribí cualquier cosa para comenzar de nuevo.")
        
        # Obtener estado actual del bot
        estado_bot = get_estado_bot(numero)
        if not estado_bot or estado_bot not in ESTADOS_BOT.values():
            estado_bot = usuario.estado_conversacion or ESTADOS_BOT["INICIO"]
            set_estado_bot(numero, estado_bot)
        
        # Enrutar según estado
        if estado_bot == ESTADOS_BOT["INICIO"]:
            return self.flujo_inicio(numero, texto)
        elif estado_bot == ESTADOS_BOT["SELECCION_INTERESES"]:
            return self.flujo_seleccion_intereses(numero, texto)
        elif estado_bot == ESTADOS_BOT["ARMANDO_PERFIL"]:
            return self.flujo_armando_perfil(numero, texto)
        elif estado_bot == ESTADOS_BOT["GENERANDO_PLAN"]:
            return self.flujo_generando_plan(numero, texto)
        elif estado_bot == ESTADOS_BOT["PLAN_PRESENTADO"]:
            return self.flujo_plan_presentado(numero, texto)
        elif estado_bot == ESTADOS_BOT["SEGUIMIENTO"]:
            return self.flujo_seguimiento(numero, texto)
        else:
            # Estado desconocido, reiniciar
            return self.flujo_inicio(numero, texto)
    
    def handle_location(self, numero, contenido):
        """Maneja mensajes de ubicación (por ahora solo para detección de ciudad)"""
        try:
            partes = [p.strip() for p in contenido.split(",")]
            if len(partes) != 2:
                return enviar_mensaje_whatsapp(numero, "⚠️ Enviá la ubicación usando el botón de ubicación de WhatsApp.")
            
            lat = float(partes[0])
            lon = float(partes[1])
            
            # Por ahora, si recibe ubicación en estado INICIO, puede usarse para detectar ciudad
            # Esto se puede mejorar con geocoding inverso
            usuario = UsuarioService.obtener_usuario_por_telefono(numero)
            if usuario and not usuario.ciudad:
                # Asumir Canelones por defecto (a futuro será configurable por BDD)
                usuario.ciudad = "Canelones"
                UsuarioService.actualizar_usuario(usuario)
            
            return self.handle_text(numero, "continuar")
            
        except Exception as e:
            print(f"Error en handle_location: {e}")
            return enviar_mensaje_whatsapp(numero, "⚠️ No pude procesar la ubicación correctamente.")
    
    # ============================================================
    # FLUJOS DEL BOT DE VIAJE
    # ============================================================
    
    def flujo_inicio(self, numero, texto):
        """Flujo inicial: saludo y asignación automática de ciudad (Canelones)"""
        usuario = UsuarioService.obtener_o_crear_usuario(numero)
        
        # Si es la primera vez, obtener nombre si está disponible
        if not usuario.nombre:
            nombre = "viajero"
        else:
            nombre = usuario.nombre
        
        # Asignar automáticamente Canelones si no tiene ciudad
        if not usuario.ciudad:
            usuario.ciudad = "Canelones"
            UsuarioService.actualizar_usuario(usuario)
        
        # Si tiene ciudad pero no intereses, pasar directamente a selección de intereses
        if not usuario.intereses or len(usuario.intereses) == 0:
            return self.flujo_seleccion_intereses(numero, texto)
        
        # Si ya tiene intereses pero no perfil completo, continuar con perfil
        if not usuario.tiene_perfil_completo():
            return self.flujo_armando_perfil(numero, texto)
        
        # Si tiene todo, puede estar en seguimiento
        return self.flujo_seguimiento(numero, texto)
    
    def flujo_seleccion_intereses(self, numero, texto):
        """Flujo de selección de intereses con menú interactivo"""
        usuario = UsuarioService.obtener_o_crear_usuario(numero)
        
        # Si el texto es una selección interactiva
        if texto.startswith("interes_"):
            interes = texto.replace("interes_", "")
            intereses_validos = ["restaurantes", "comercios", "recreacion", "cultura", "compras"]
            
            if interes in intereses_validos:
                # Toggle: si ya está seleccionado, quitarlo; si no, agregarlo
                if interes in usuario.intereses:
                    usuario.intereses.remove(interes)
                else:
                    usuario.agregar_interes(interes)
                UsuarioService.actualizar_usuario(usuario)
                
                # Actualizar estado local
                intereses_actuales = usuario.intereses.copy()
                set_intereses_seleccionados(numero, intereses_actuales)
                
                # Mostrar menú actualizado
                return self.flujo_seleccion_intereses(numero, "actualizar")
        
        # Si el texto es "continuar_intereses" o "continuar" y hay intereses seleccionados
        if (texto == "continuar_intereses" or texto.lower() in ("continuar", "listo", "siguiente", "listo, continuar")) and usuario.intereses:
            set_estado_bot(numero, ESTADOS_BOT["ARMANDO_PERFIL"])
            usuario.estado_conversacion = ESTADOS_BOT["ARMANDO_PERFIL"]
            UsuarioService.actualizar_usuario(usuario)
            clear_waiting_for(numero)
            return self.flujo_armando_perfil(numero, texto)
        
        # Si el texto es "actualizar", solo refrescar el menú sin cambiar estado
        if texto == "actualizar":
            # Continuar para mostrar menú actualizado
            pass
        
        # Mostrar menú de intereses
        intereses_actuales = usuario.intereses
        rows = []
        
        intereses_opciones = [
            {"id": "restaurantes", "title": "🍽️ Restaurantes", "description": "Lugares para comer"},
            {"id": "comercios", "title": "🛍️ Comercios", "description": "Tiendas y negocios"},
            {"id": "recreacion", "title": "🌳 Zonas de Recreación", "description": "Parques y espacios al aire libre"},
            {"id": "cultura", "title": "🏛️ Cultura / Paseos", "description": "Museos, teatros, plazas"},
            {"id": "compras", "title": "🛒 Compras / Regalos", "description": "Shopping y souvenirs"}
        ]
        
        for opcion in intereses_opciones:
            esta_seleccionado = opcion["id"] in intereses_actuales
            titulo = f"{'✅ ' if esta_seleccionado else ''}{opcion['title']}"
            rows.append({
                "id": f"interes_{opcion['id']}",
                "title": titulo,
                "description": opcion["description"]
            })
        
        # Agregar opción para continuar si hay al menos un interés seleccionado
        if intereses_actuales:
            rows.append({
                "id": "continuar_intereses",
                "title": "✅ Continuar",
                "description": f"Listo con {len(intereses_actuales)} interés/es seleccionado/s"
            })
        
        secciones = [{
            "title": "Seleccioná tus intereses",
            "rows": rows
        }]
        
        mensaje_inicial = (
            f"Hola {usuario.nombre or 'viajero'} 👋\n\n"
            f"Estoy acá para ayudarte a disfrutar al máximo tu recorrido por {usuario.ciudad or 'la ciudad'}.\n\n"
            f"Para empezar, contame qué tipo de cosas te interesan durante este viaje 👇"
        ) if not intereses_actuales else (
            f"Seleccionaste: {', '.join([i.capitalize() for i in intereses_actuales])}\n\n"
            f"¿Querés agregar más intereses o continuar?"
        )
        
        payload = {
            "messaging_product": "whatsapp",
            "to": numero,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "header": {
                    "type": "text",
                    "text": "🎯 ¿Qué te interesa?"
                },
                "body": {
                    "text": mensaje_inicial
                },
                "footer": {
                    "text": "Podés seleccionar múltiples opciones"
                },
                "action": {
                    "button": "Ver opciones",
                    "sections": secciones
                }
            }
        }
        
        set_estado_bot(numero, ESTADOS_BOT["SELECCION_INTERESES"])
        usuario.estado_conversacion = ESTADOS_BOT["SELECCION_INTERESES"]
        UsuarioService.actualizar_usuario(usuario)
        
        return enviar_mensaje_whatsapp(numero, payload)
    
    def flujo_armando_perfil(self, numero, texto):
        """Flujo para armar el perfil del usuario con preguntas progresivas"""
        usuario = UsuarioService.obtener_o_crear_usuario(numero)
        
        # Inicializar perfil si no existe
        if not usuario.perfil:
            UsuarioService.inicializar_perfil(numero)
            usuario = UsuarioService.obtener_usuario_por_telefono(numero)
        
        # Interpretar respuesta del usuario usando Gemini
        interpretacion = GeminiOrchestratorService.interpretar_mensaje_usuario(
            texto,
            usuario
        )
        
        # Si detectó una respuesta a un campo del perfil
        if interpretacion.get("respuesta_detectada") and interpretacion.get("campo_perfil"):
            campo = interpretacion.get("campo_perfil")
            valor = interpretacion.get("valor_detectado")
            
            # Actualizar perfil
            UsuarioService.actualizar_perfil(numero, campo, valor)
            usuario = UsuarioService.obtener_usuario_por_telefono(numero)
            
            # Mensaje de confirmación si Gemini generó uno
            if interpretacion.get("mensaje_respuesta"):
                enviar_mensaje_whatsapp(numero, interpretacion.get("mensaje_respuesta"))
        
        # Verificar si el perfil está completo
        if usuario.tiene_perfil_completo():
            # Pasar a generación de plan
            set_estado_bot(numero, ESTADOS_BOT["GENERANDO_PLAN"])
            usuario.estado_conversacion = ESTADOS_BOT["GENERANDO_PLAN"]
            UsuarioService.actualizar_usuario(usuario)
            return self.flujo_generando_plan(numero, texto)
        
        # Generar siguiente pregunta
        siguiente_pregunta = GeminiOrchestratorService.generar_pregunta_siguiente(
            usuario,
            usuario.intereses
        )
        
        if siguiente_pregunta:
            # Guardar qué pregunta se está haciendo
            # Extraer el campo de la pregunta (simplificado)
            campo_pregunta = None
            if "tipo de viaje" in siguiente_pregunta.lower():
                campo_pregunta = "tipo_viaje"
            elif "acompañado" in siguiente_pregunta.lower() or ("solo" in siguiente_pregunta.lower() and "viajás" in siguiente_pregunta.lower()):
                campo_pregunta = "acompanantes"
            elif "comida" in siguiente_pregunta.lower():
                campo_pregunta = "preferencias_comida"
            elif "presupuesto" in siguiente_pregunta.lower():
                campo_pregunta = "presupuesto"
            elif "regalar" in siguiente_pregunta.lower() or ("vos" in siguiente_pregunta.lower() and "regalar" in siguiente_pregunta.lower()):
                campo_pregunta = "interes_regalos"
            elif "ropa" in siguiente_pregunta.lower():
                campo_pregunta = "interes_ropa"
            elif "recreación" in siguiente_pregunta.lower() or "recreacion" in siguiente_pregunta.lower():
                campo_pregunta = "interes_tipo_recreacion"
            elif "días" in siguiente_pregunta.lower() or "dias" in siguiente_pregunta.lower():
                campo_pregunta = "duracion_estadia"
            
            set_pregunta_actual(numero, campo_pregunta)
            set_estado_bot(numero, ESTADOS_BOT["ARMANDO_PERFIL"])
            usuario.estado_conversacion = ESTADOS_BOT["ARMANDO_PERFIL"]
            UsuarioService.actualizar_usuario(usuario)
            self.set_waiting_for(numero, "flujo_armando_perfil")
            
            return enviar_mensaje_whatsapp(numero, siguiente_pregunta)
        else:
            # No hay más preguntas, pasar a generación de plan
            set_estado_bot(numero, ESTADOS_BOT["GENERANDO_PLAN"])
            usuario.estado_conversacion = ESTADOS_BOT["GENERANDO_PLAN"]
            UsuarioService.actualizar_usuario(usuario)
            return self.flujo_generando_plan(numero, texto)
    
    def flujo_generando_plan(self, numero, texto):
        """Genera el plan personalizado usando Gemini y ExcursionService"""
        usuario = UsuarioService.obtener_usuario_por_telefono(numero)
        
        if not usuario:
            return self.flujo_inicio(numero, texto)
        
        try:
            # Generar plan
            plan = PlanViajeService.generar_plan_personalizado(usuario)
            
            # Guardar plan en conversation_data
            self.conversation_data['plan_viaje'] = plan
            
            # Pasar a presentación del plan
            set_estado_bot(numero, ESTADOS_BOT["PLAN_PRESENTADO"])
            usuario.estado_conversacion = ESTADOS_BOT["PLAN_PRESENTADO"]
            UsuarioService.actualizar_usuario(usuario)
            
            return self.flujo_plan_presentado(numero, texto)
            
        except Exception as e:
            print(f"Error al generar plan: {e}")
            return enviar_mensaje_whatsapp(
                numero,
                "⚠️ Hubo un error al generar tu plan. Por favor, intentá de nuevo o escribí /reiniciar para comenzar de nuevo."
            )
    
    def flujo_plan_presentado(self, numero, texto):
        """Presenta el plan generado al usuario con imagen si está disponible"""
        plan = self.conversation_data.get('plan_viaje')
        
        if not plan:
            return self.flujo_generando_plan(numero, texto)
        
        # Enviar plan con imagen (si está disponible) y texto detallado
        # El método maneja errores silenciosamente si no hay imagen
        PlanViajeService.enviar_plan_con_imagen(numero, plan)
        
        # Pasar a seguimiento
        set_estado_bot(numero, ESTADOS_BOT["SEGUIMIENTO"])
        usuario = UsuarioService.obtener_usuario_por_telefono(numero)
        if usuario:
            usuario.estado_conversacion = ESTADOS_BOT["SEGUIMIENTO"]
            UsuarioService.actualizar_usuario(usuario)
        
        return self.flujo_seguimiento(numero, texto)
    
    def flujo_seguimiento(self, numero, texto):
        """Ofrece ayuda adicional después de presentar el plan"""
        usuario = UsuarioService.obtener_usuario_por_telefono(numero)
        
        texto_lower = texto.lower()
        
        # Opciones de seguimiento
        if texto_lower in ("ajustar", "modificar", "cambiar", "otro plan"):
            # Volver a armando perfil
            set_estado_bot(numero, ESTADOS_BOT["ARMANDO_PERFIL"])
            if usuario:
                usuario.estado_conversacion = ESTADOS_BOT["ARMANDO_PERFIL"]
                UsuarioService.actualizar_usuario(usuario)
            return self.flujo_armando_perfil(numero, "ajustar plan")
        
        if texto_lower in ("nuevo plan", "otro", "generar otro"):
            # Generar nuevo plan
            set_estado_bot(numero, ESTADOS_BOT["GENERANDO_PLAN"])
            if usuario:
                usuario.estado_conversacion = ESTADOS_BOT["GENERANDO_PLAN"]
                UsuarioService.actualizar_usuario(usuario)
            return self.flujo_generando_plan(numero, texto)
        
        # Mensaje de seguimiento
        mensaje = (
            "Si querés, puedo ayudarte a:\n"
            "• Elegir qué hacer hoy\n"
            "• Buscar algo cerca de tu ubicación\n"
            "• Ajustar el plan según tus preferencias\n\n"
            "Solo escribime lo que necesitás 👌"
        )
        
        set_estado_bot(numero, ESTADOS_BOT["SEGUIMIENTO"])
        if usuario:
            usuario.estado_conversacion = ESTADOS_BOT["SEGUIMIENTO"]
            UsuarioService.actualizar_usuario(usuario)
        
        return enviar_mensaje_whatsapp(numero, mensaje)
