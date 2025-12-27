from typing import Any, Optional, Dict, Callable, List
from datetime import datetime
import re
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
            "flujo_confirmacion_servicio": self.flujo_confirmacion_servicio,
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
        
        # VERIFICACIÓN TEMPRANA: Detectar mensajes del bot ANTES de procesar
        # Esto previene que Gemini se active con mensajes del bot
        if texto_strip:
            texto_len = len(texto_strip)
            
            # Patrones específicos de mensajes del bot
            patrones_bot_exactos_early = [
                "código qr -",
                "📱 código qr -",
                "📱 *código qr -",
                "escanea este código",
                "escanea el código qr",
            ]
            
            # Verificar si empieza con patrón del bot
            empieza_con_bot_early = any(texto_lower.startswith(patron) for patron in patrones_bot_exactos_early)
            
            # Verificar si contiene patrón completo de QR
            es_mensaje_qr_completo_early = ("código qr -" in texto_lower or "codigo qr -" in texto_lower) and "escanea" in texto_lower
            
            # Verificar si es mensaje corto con QR
            contiene_qr_early = any(patron in texto_lower for patron in ["código qr", "codigo qr", "qr -", "📱 código", "📱 *código"])
            es_mensaje_corto_qr_early = texto_len < 50 and contiene_qr_early
            
            # DETECCIÓN AGRESIVA: Si contiene "QR" y "escanea" en cualquier parte, es del bot
            es_mensaje_qr_agresivo_early = ("qr" in texto_lower or "codigo" in texto_lower) and "escanea" in texto_lower and texto_len < 150
            
            # Si parece ser mensaje del bot, NO procesar
            if empieza_con_bot_early or es_mensaje_qr_completo_early or es_mensaje_corto_qr_early or es_mensaje_qr_agresivo_early:
                print(f"🚫 [handle_text] BLOQUEANDO mensaje del bot antes de procesar:")
                print(f"   - Empieza con patrón bot: {empieza_con_bot_early}")
                print(f"   - Mensaje QR completo: {es_mensaje_qr_completo_early}")
                print(f"   - Mensaje corto con QR: {es_mensaje_corto_qr_early}")
                print(f"   - Mensaje QR agresivo: {es_mensaje_qr_agresivo_early}")
                print(f"   - Mensaje: {texto[:100]}...")
                return None  # No procesar, no responder
        
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
        
        # Comando #Iniciar para testing: reinicia todo y envía mensaje de apertura
        if texto_lower == "#iniciar" or texto_strip == "#Iniciar":
            # RESETEAR COMPLETAMENTE EL ESTADO DE SESIÓN
            # reset_estado ya limpia todo: estado_bot, waiting_for, context_data, pregunta_actual, intereses_seleccionados
            reset_estado(numero)
            
            # Asegurar que el estado del bot esté en INICIO (reset_estado ya lo hace, pero por si acaso)
            set_estado_bot(numero, ESTADOS_BOT["INICIO"])
            clear_waiting_for(numero)
            clear_pregunta_actual(numero)
            set_intereses_seleccionados(numero, [])
            
            # Limpiar datos del usuario en BD
            usuario.estado_conversacion = ESTADOS_BOT["INICIO"]
            usuario.intereses = []
            usuario.perfil = None
            UsuarioService.actualizar_usuario(usuario)
            
            # Obtener usuario actualizado para asegurar que los cambios se aplicaron
            usuario = UsuarioService.obtener_usuario_por_telefono(numero)
            
            # Verificar que los intereses estén realmente vacíos
            if usuario.intereses:
                usuario.intereses = []
                UsuarioService.actualizar_usuario(usuario)
                usuario = UsuarioService.obtener_usuario_por_telefono(numero)
            
            # Verificar que el estado esté realmente en INICIO
            estado_verificacion = get_estado_bot(numero)
            waiting_verificacion = get_waiting_for(numero)
            if estado_verificacion != ESTADOS_BOT["INICIO"] or waiting_verificacion is not None:
                # Forzar reset si no está limpio
                reset_estado(numero)
                set_estado_bot(numero, ESTADOS_BOT["INICIO"])
                clear_waiting_for(numero)
            
            # Ir a flujo_inicio para enviar el mensaje de apertura
            return self.flujo_inicio(numero, "")
        
        # Comando #QR para testing: envía info de restaurante predefinido con QR
        if texto_lower == "#qr" or texto_strip == "#QR":
            from Util.datos_lugares import DATOS_LUGARES
            from Util.qr_helper import obtener_ruta_qr, debe_enviar_qr
            from whatsapp_api import enviar_imagen_whatsapp
            import os
            import time
            
            # Restaurante predefinido para testing (rest_001 - El Buen Suspiro)
            restaurante_id = "rest_001"
            ciudad = "Colonia"
            
            # Buscar el restaurante en los datos
            restaurante = None
            if ciudad in DATOS_LUGARES:
                for exc in DATOS_LUGARES[ciudad].get("restaurantes", []):
                    if exc.id == restaurante_id:
                        restaurante = exc
                        break
            
            if not restaurante:
                return enviar_mensaje_whatsapp(numero, "❌ Restaurante de prueba no encontrado")
            
            try:
                # Obtener/generar QR
                print(f"🧪 [TEST] Generando QR para {restaurante.nombre} (ID: {restaurante.id})")
                ruta_qr = obtener_ruta_qr(restaurante.id)
                
                # Construir mensaje
                descripcion = restaurante.descripcion if restaurante.descripcion else "Sin descripción disponible"
                ubicacion = restaurante.ubicacion if restaurante.ubicacion else None
                
                # Enviar imagen del restaurante
                if restaurante.imagen_url:
                    caption = f"*{restaurante.nombre}*\n\n{descripcion}"
                    if ubicacion:
                        caption += f"\n\n📍 {ubicacion}"
                    if ruta_qr:
                        caption += f"\n\n📱 Escanea el código QR para obtener un descuento del 5%"
                    
                    # Limitar caption a 1024 caracteres
                    if len(caption) > 1024:
                        caption = caption[:1021] + "..."
                    
                    resultado = enviar_imagen_whatsapp(numero, restaurante.imagen_url, caption)
                    
                    if resultado.get("success"):
                        print(f"🧪 [TEST] ✅ Imagen del restaurante enviada con información completa")
                        
                        # Enviar QR después en mensaje separado
                        if ruta_qr and os.path.exists(ruta_qr):
                            time.sleep(2)  # Pausa más larga para evitar problemas con WhatsApp
                            print(f"🧪 [TEST] 📱 Enviando QR en mensaje separado: {ruta_qr}")
                            print(f"🧪 [TEST] 📱 Archivo existe: {os.path.exists(ruta_qr)}")
                            
                            # Enviar QR con caption simple
                            caption_qr = f"📱 Código QR - {restaurante.nombre}\n\nEscanea este código para obtener un descuento del 5%"
                            print(f"🧪 [TEST] 📱 Enviando QR con caption...")
                            resultado_qr = enviar_imagen_whatsapp(numero, ruta_qr, caption_qr)
                            print(f"🧪 [TEST] 📱 Resultado del envío QR: {resultado_qr}")
                            
                            if resultado_qr.get("success"):
                                print(f"🧪 [TEST] ✅ QR enviado exitosamente")
                            else:
                                # Si falla con caption, intentar sin caption
                                print(f"🧪 [TEST] ⚠️ Falló con caption, intentando sin caption...")
                                resultado_qr = enviar_imagen_whatsapp(numero, ruta_qr, "")
                                if resultado_qr.get("success"):
                                    print(f"🧪 [TEST] ✅ QR enviado exitosamente (sin caption)")
                                else:
                                    error_qr = resultado_qr.get('error', 'Error desconocido')
                                    print(f"🧪 [TEST] ❌ Error al enviar QR: {error_qr}")
                                    print(f"🧪 [TEST] Respuesta completa: {resultado_qr}")
                        else:
                            print(f"🧪 [TEST] ⚠️ QR no disponible o no existe")
                            if ruta_qr:
                                print(f"🧪 [TEST] Ruta QR: {ruta_qr}")
                                print(f"🧪 [TEST] Existe: {os.path.exists(ruta_qr) if ruta_qr else 'N/A'}")
                    else:
                        # Fallback a texto
                        mensaje = f"*{restaurante.nombre}*\n\n{descripcion}"
                        if ubicacion:
                            mensaje += f"\n\n📍 {ubicacion}"
                        if ruta_qr:
                            mensaje += f"\n\n📱 Escanea el código QR para obtener un descuento del 5%"
                        enviar_mensaje_whatsapp(numero, mensaje)
                        
                        if ruta_qr and os.path.exists(ruta_qr):
                            time.sleep(2)
                            caption_qr = f"Código QR - {restaurante.nombre}\n\nEscanea este código para obtener un descuento del 5%"
                            print(f"🧪 [TEST] 📱 Enviando QR después del texto: {ruta_qr}")
                            print(f"🧪 [TEST] 📱 Caption del QR: {caption_qr}")
                            resultado_qr = enviar_imagen_whatsapp(numero, ruta_qr, caption_qr)
                            print(f"🧪 [TEST] 📱 Resultado del envío QR: {resultado_qr}")
                            if resultado_qr.get("success"):
                                print(f"🧪 [TEST] ✅ QR enviado exitosamente")
                            else:
                                print(f"🧪 [TEST] ❌ Error: {resultado_qr.get('error')}")
                else:
                    # Sin imagen, solo texto + QR
                    mensaje = f"*{restaurante.nombre}*\n\n{descripcion}"
                    if ubicacion:
                        mensaje += f"\n\n📍 {ubicacion}"
                    if ruta_qr:
                        mensaje += f"\n\n📱 Escanea el código QR para obtener un descuento del 5%"
                    enviar_mensaje_whatsapp(numero, mensaje)
                    
                    if ruta_qr and os.path.exists(ruta_qr):
                        time.sleep(2)
                        caption_qr = f"Código QR - Descuento 5% en {restaurante.nombre}"
                        print(f"🧪 [TEST] 📱 Enviando QR (sin imagen restaurante): {ruta_qr}")
                        resultado_qr = enviar_imagen_whatsapp(numero, ruta_qr, caption_qr)
                        if resultado_qr.get("success"):
                            print(f"🧪 [TEST] ✅ QR enviado exitosamente")
                        else:
                            print(f"🧪 [TEST] ❌ Error: {resultado_qr.get('error')}")
                
                return None  # Ya se envió el mensaje
                
            except Exception as e:
                import traceback
                print(f"🧪 [TEST] ❌ Error: {e}")
                print(traceback.format_exc())
                return enviar_mensaje_whatsapp(numero, f"❌ Error al enviar restaurante de prueba: {str(e)}")
        
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
        elif estado_bot == ESTADOS_BOT["ESPERANDO_CONFIRMACION"]:
            return self.flujo_confirmacion_servicio(numero, texto)
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
                # Asumir Colonia por defecto (a futuro será configurable por BDD)
                usuario.ciudad = "Colonia"
                UsuarioService.actualizar_usuario(usuario)
            
            return self.handle_text(numero, "continuar")
            
        except Exception as e:
            print(f"Error en handle_location: {e}")
            return enviar_mensaje_whatsapp(numero, "⚠️ No pude procesar la ubicación correctamente.")
    
    # ============================================================
    # FLUJOS DEL BOT DE VIAJE
    # ============================================================
    
    def flujo_inicio(self, numero, texto):
        """Flujo inicial: saludo cálido y confirmación de servicio"""
        usuario = UsuarioService.obtener_o_crear_usuario(numero)
        
        # Verificar estado actual
        estado_actual = get_estado_bot(numero)
        waiting_for = get_waiting_for(numero)
        
        # Si el estado es INICIO y no hay waiting_for, SIEMPRE mostrar mensaje inicial
        # Esto permite que #Iniciar funcione correctamente
        if estado_actual == ESTADOS_BOT["INICIO"] and not waiting_for:
            # Forzar mostrar mensaje inicial - resetear cualquier estado previo
            pass  # Continuar con el mensaje de bienvenida
        # Si el usuario ya confirmó el servicio y tiene intereses Y hay waiting_for, continuar con el flujo normal
        elif usuario.intereses and len(usuario.intereses) > 0 and waiting_for and estado_actual != ESTADOS_BOT["INICIO"]:
            # Ya pasó por la confirmación, continuar con flujo normal
            if not usuario.tiene_perfil_completo():
                return self.flujo_armando_perfil(numero, texto)
            return self.flujo_seguimiento(numero, texto)
        
        # Si es la primera vez, obtener nombre si está disponible
        if not usuario.nombre:
            nombre = "viajero"
        else:
            nombre = usuario.nombre
        
        # Asignar automáticamente Colonia si no tiene ciudad
        if not usuario.ciudad:
            usuario.ciudad = "Colonia"
            UsuarioService.actualizar_usuario(usuario)
        
        # Si no ha confirmado, enviar mensaje de bienvenida con confirmación automáticamente
        # (sin importar qué texto envió el usuario, incluso "Hola")
        mensaje = (
            f"¡Hola! 👋\n\n"
            f"Soy tu asistente virtual de viaje y estoy acá para ayudarte a aprovechar al máximo tu estadía en {usuario.ciudad}.\n\n"
            f"A continuación te voy a hacer unas breves preguntas para conocerte mejor y poder recomendarte "
            f"lugares, actividades y opciones que se adapten a tus gustos.\n\n"
            f"La idea es sacarte de un apuro y ahorrarte horas buscando en Google \n\n"
            f"¿Quieres que te proporcione este servicio sin costo adicional?"
        )
        
        # Enviar mensaje con botones de confirmación
        payload = {
            "messaging_product": "whatsapp",
            "to": numero,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": mensaje
                },
                "action": {
                    "buttons": [
                        {
                            "type": "reply",
                            "reply": {
                                "id": "confirmar_servicio_si",
                                "title": "✅ Sí, quiero"
                            }
                        },
                        {
                            "type": "reply",
                            "reply": {
                                "id": "confirmar_servicio_no",
                                "title": "❌ No, gracias"
                            }
                        }
                    ]
                }
            }
        }
        
        set_estado_bot(numero, ESTADOS_BOT["ESPERANDO_CONFIRMACION"])
        usuario.estado_conversacion = ESTADOS_BOT["ESPERANDO_CONFIRMACION"]
        UsuarioService.actualizar_usuario(usuario)
        self.set_waiting_for(numero, "flujo_confirmacion_servicio")
        
        return enviar_mensaje_whatsapp(numero, payload)
    
    def flujo_confirmacion_servicio(self, numero, texto):
        """Maneja la confirmación del servicio por parte del usuario"""
        usuario = UsuarioService.obtener_o_crear_usuario(numero)
        
        texto_lower = texto.lower()
        
        # Verificar si es respuesta afirmativa (botón o texto)
        es_afirmativo = (
            texto == "confirmar_servicio_si" or
            texto_lower in ("sí", "si", "yes", "ok", "okay", "dale", "vamos", "adelante", "continuar", "sí, quiero el servicio")
        )
        
        es_negativo = (
            texto == "confirmar_servicio_no" or
            texto_lower in ("no", "nope", "no gracias", "no, gracias", "cancelar")
        )
        
        if es_negativo:
            mensaje = (
                "Está bien de todas formas por cualquier consulta durante tu viaje no dudes en escribir."
            )
            set_estado_bot(numero, ESTADOS_BOT["INICIO"])
            usuario.estado_conversacion = ESTADOS_BOT["INICIO"]
            UsuarioService.actualizar_usuario(usuario)
            clear_waiting_for(numero)
            return enviar_mensaje_whatsapp(numero, mensaje)
        
        if es_afirmativo:
            # Continuar con selección de intereses
            # Actualizar estado a SELECCION_INTERESES
            set_estado_bot(numero, ESTADOS_BOT["SELECCION_INTERESES"])
            usuario.estado_conversacion = ESTADOS_BOT["SELECCION_INTERESES"]
            UsuarioService.actualizar_usuario(usuario)
            clear_waiting_for(numero)
            # Llamar con texto vacío para evitar que se detecte como interés
            return self.flujo_seleccion_intereses(numero, "")
        
        # Si no es claro, usar Gemini para interpretar y responder amigablemente
        respuesta_amigable = GeminiOrchestratorService.generar_respuesta_amigable(
            texto,
            usuario,
            contexto_estado="El bot está esperando confirmación del usuario para iniciar el servicio de planificación de viaje"
        )
        
        # Agregar recordatorio sobre los botones
        mensaje = f"{respuesta_amigable}\n\nSi querés continuar, podés usar los botones o responder 'Sí' para comenzar."
        return enviar_mensaje_whatsapp(numero, mensaje)
    
    def flujo_seleccion_intereses(self, numero, texto):
        """Flujo de selección de intereses con texto simple (1 2 3)"""
        usuario = UsuarioService.obtener_o_crear_usuario(numero)
        
        # Validar estado: si no estamos en SELECCION_INTERESES, verificar si es un botón obsoleto
        estado_actual = get_estado_bot(numero)
        if estado_actual != ESTADOS_BOT["SELECCION_INTERESES"]:
            # Si es un botón de intereses pero el estado cambió, redirigir apropiadamente
            if texto in ("confirmar_intereses", "agregar_mas_intereses"):
                # Si estamos en ARMANDO_PERFIL, rechazar el botón obsoleto
                if estado_actual == ESTADOS_BOT["ARMANDO_PERFIL"]:
                    # Ya estamos en otro flujo, ignorar el botón obsoleto
                    return self.flujo_armando_perfil(numero, texto)
                # Si estamos en otro estado, intentar redirigir al flujo correcto
                elif estado_actual == ESTADOS_BOT["INICIO"]:
                    return self.flujo_inicio(numero, texto)
                # Estado desconocido, redirigir al inicio
                else:
                    set_estado_bot(numero, ESTADOS_BOT["INICIO"])
                    return self.flujo_inicio(numero, texto)
            # Si el texto parece ser selección de intereses (números o nombres), corregir el estado y procesar
            elif texto and texto.strip():
                # Verificar si el texto parece ser intereses (contiene números o palabras clave)
                intereses_detectados = self._detectar_intereses_texto(texto)
                if intereses_detectados:
                    # Es texto de intereses, corregir el estado y continuar con el procesamiento normal
                    set_estado_bot(numero, ESTADOS_BOT["SELECCION_INTERESES"])
                    usuario.estado_conversacion = ESTADOS_BOT["SELECCION_INTERESES"]
                    UsuarioService.actualizar_usuario(usuario)
                    # Continuar con el procesamiento normal más abajo (no hacer return aquí)
                else:
                    # No es texto de intereses, redirigir según estado
                    if estado_actual == ESTADOS_BOT["INICIO"]:
                        return self.flujo_inicio(numero, texto)
                    else:
                        # Corregir el estado a SELECCION_INTERESES y mostrar mensaje inicial
                        set_estado_bot(numero, ESTADOS_BOT["SELECCION_INTERESES"])
                        usuario.estado_conversacion = ESTADOS_BOT["SELECCION_INTERESES"]
                        UsuarioService.actualizar_usuario(usuario)
                        return self._mostrar_mensaje_intereses(numero, usuario, False)
        
        # Verificar si el usuario presionó "Confirmar" (botón interactivo)
        if texto == "confirmar_intereses":
            # Marcar que el botón fue presionado (desactivar botones)
            self.set_waiting_for(numero, "flujo_seleccion_intereses_confirmado")
            
            # Verificar que tenga intereses
            if not usuario.intereses or len(usuario.intereses) == 0:
                # No tiene intereses, mostrar mensaje de intereses de nuevo
                return self._mostrar_mensaje_intereses(numero, usuario, False)
            
            # Tiene intereses, continuar al siguiente flujo
            set_estado_bot(numero, ESTADOS_BOT["ARMANDO_PERFIL"])
            usuario.estado_conversacion = ESTADOS_BOT["ARMANDO_PERFIL"]
            UsuarioService.actualizar_usuario(usuario)
            clear_waiting_for(numero)
            # Llamar a flujo_armando_perfil con texto vacío para que muestre la primera pregunta
            return self.flujo_armando_perfil(numero, "")
        
        # Verificar si el usuario presionó "Agregar más intereses" (botón interactivo)
        if texto == "agregar_mas_intereses":
            # Resetear waiting_for para permitir mostrar botones de nuevo después de agregar más intereses
            clear_waiting_for(numero)
            
            # Mostrar mensaje de intereses excluyendo los ya seleccionados
            return self._mostrar_mensaje_intereses(numero, usuario, True)
        
        # Detectar intereses del texto del usuario (formato: "1 2 3" o texto libre)
        # Solo procesar si el texto no está vacío y no es un botón
        if texto and texto.strip() and texto not in ("confirmar_intereses", "agregar_mas_intereses"):
            intereses_detectados = self._detectar_intereses_texto(texto)
            print(f"🔍 Texto recibido: '{texto}' -> Intereses detectados: {intereses_detectados}")
            
            if intereses_detectados:
                # Agregar intereses detectados (sin duplicar)
                intereses_nuevos = []
                for interes in intereses_detectados:
                    if interes not in usuario.intereses:
                        usuario.agregar_interes(interes)
                        intereses_nuevos.append(interes)
                UsuarioService.actualizar_usuario(usuario)
                
                # Actualizar estado local
                intereses_actuales = usuario.intereses.copy()
                set_intereses_seleccionados(numero, intereses_actuales)
                
                # Mostrar confirmación con botones
                print(f"✅ Intereses agregados: {intereses_actuales}")
                return self._mostrar_confirmacion_intereses(numero, usuario)
            else:
                print(f"⚠️ No se detectaron intereses en el texto: '{texto}'")
        
        # Si no se detectaron intereses o el texto está vacío, mostrar mensaje inicial
        return self._mostrar_mensaje_intereses(numero, usuario, False)
    
    def _mostrar_mensaje_intereses(self, numero, usuario, excluir_seleccionados=False):
        """Muestra el mensaje de selección de intereses con opciones numeradas"""
        intereses_actuales = usuario.intereses if usuario.intereses else []
        
        # Lista de todos los intereses disponibles
        intereses_opciones = [
            {"id": "restaurantes", "nombre": "Restaurantes", "emoji": "🍽️"},
            {"id": "comercios", "nombre": "Comercios", "emoji": "🛍️"},
            {"id": "recreacion", "nombre": "Recreación", "emoji": "🌳"},
            {"id": "cultura", "nombre": "Cultura", "emoji": "🏛️"},
            {"id": "compras", "nombre": "Compras", "emoji": "🛒"}
        ]
        
        # Si excluir_seleccionados es True, filtrar los ya seleccionados
        if excluir_seleccionados:
            intereses_disponibles = [op for op in intereses_opciones if op["id"] not in intereses_actuales]
        else:
            intereses_disponibles = intereses_opciones
        
        # Construir mensaje con opciones numeradas
        mensaje = "¿Qué te interesa? (Por favor elegí separando por , o espacios)\n\n"
        for idx, opcion in enumerate(intereses_disponibles, 1):
            mensaje += f"{idx}. {opcion['emoji']} {opcion['nombre']}\n"
        
        mensaje += "\nEjemplo: \"1 2 3\" o \"restaurantes compras recreacion\""
        
        set_estado_bot(numero, ESTADOS_BOT["SELECCION_INTERESES"])
        usuario.estado_conversacion = ESTADOS_BOT["SELECCION_INTERESES"]
        UsuarioService.actualizar_usuario(usuario)
        self.set_waiting_for(numero, "flujo_seleccion_intereses")
        
        return enviar_mensaje_whatsapp(numero, mensaje)
    
    def _mostrar_confirmacion_intereses(self, numero, usuario):
        """Muestra la confirmación de intereses seleccionados con botones"""
        intereses_actuales = usuario.intereses if usuario.intereses else []
        nombres_intereses = [self._obtener_nombre_interes(i) for i in intereses_actuales]
        
        # Limitar el mensaje a 1024 caracteres (límite de WhatsApp)
        mensaje = f"Tus intereses son: {', '.join(nombres_intereses)}\n\n¿Confirmar o agregar más intereses?"
        if len(mensaje) > 1024:
            mensaje = f"Tus intereses: {', '.join(nombres_intereses[:3])}{'...' if len(nombres_intereses) > 3 else ''}\n\n¿Confirmar o agregar más?"
        
        # Verificar si los botones ya fueron presionados (usando waiting_for como flag)
        waiting_for = get_waiting_for(numero)
        # Si waiting_for contiene "confirmado", significa que ya se presionó el botón de confirmar
        if waiting_for and "confirmado" in waiting_for:
            # Botón de confirmar ya fue presionado, no mostrar botones de nuevo, solo el mensaje
            set_estado_bot(numero, ESTADOS_BOT["SELECCION_INTERESES"])
            usuario.estado_conversacion = ESTADOS_BOT["SELECCION_INTERESES"]
            UsuarioService.actualizar_usuario(usuario)
            return enviar_mensaje_whatsapp(numero, mensaje)
        
        # Crear payload con botones interactivos
        # Limitar títulos de botones a 20 caracteres (límite de WhatsApp)
        payload = {
            "messaging_product": "whatsapp",
            "to": numero,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": mensaje
                },
                "action": {
                    "buttons": [
                        {
                            "type": "reply",
                            "reply": {
                                "id": "confirmar_intereses",
                                "title": "✅ Confirmar"
                            }
                        },
                        {
                            "type": "reply",
                            "reply": {
                                "id": "agregar_mas_intereses",
                                "title": "➕ Agregar más"
                            }
                        }
                    ]
                }
            }
        }
        
        set_estado_bot(numero, ESTADOS_BOT["SELECCION_INTERESES"])
        usuario.estado_conversacion = ESTADOS_BOT["SELECCION_INTERESES"]
        UsuarioService.actualizar_usuario(usuario)
        self.set_waiting_for(numero, "flujo_seleccion_intereses")
        
        try:
            resultado = enviar_mensaje_whatsapp(numero, payload)
            # Si hay error, intentar enviar solo texto
            if resultado and not resultado.get("success", True):
                print(f"⚠️ Error enviando botones interactivos, enviando solo texto")
                return enviar_mensaje_whatsapp(numero, mensaje)
            return resultado
        except Exception as e:
            print(f"⚠️ Error en _mostrar_confirmacion_intereses: {e}")
            # Fallback: enviar solo texto
            return enviar_mensaje_whatsapp(numero, mensaje)
    
    def _crear_pregunta_interactiva(self, numero: str, campo: str) -> dict:
        """Crea un mensaje interactivo según el campo del perfil.
        Usa botones si hay 3 o menos opciones, lista interactiva si hay más de 3."""
        preguntas_interactivas = {
            "tipo_viaje": {
                "body": "¿Qué tipo de viaje estás haciendo?",
                "options": [
                    {"id": "tipo_viaje_solo", "title": "Solo"},
                    {"id": "tipo_viaje_pareja", "title": "Con pareja"},
                    {"id": "tipo_viaje_familia", "title": "Con familia"},
                    {"id": "tipo_viaje_amigos", "title": "Con amigos"},
                    {"id": "tipo_viaje_negocios", "title": "Negocios"}
                ]
            },
            "duracion_estadia": {
                "body": "¿Cuántos días vas a estar?",
                "options": [
                    {"id": "duracion_1_2", "title": "1-2 días"},
                    {"id": "duracion_3_5", "title": "3-5 días"},
                    {"id": "duracion_mas_5", "title": "Más de 5 días"}
                ]
            },
            "preferencias_comida": {
                "body": "¿Qué tipo de comida preferís?",
                "options": [
                    {"id": "comida_local", "title": "Local"},
                    {"id": "comida_internacional", "title": "Internacional"},
                    {"id": "comida_vegetariano", "title": "Vegetariano"},
                    {"id": "comida_vegano", "title": "Vegano"},
                    {"id": "comida_sin_restricciones", "title": "Sin restricciones"}
                ]
            },
            "interes_regalos": {
                "body": "¿Buscás algo para vos o para regalar?",
                "options": [
                    {"id": "regalos_si", "title": "Sí, para regalar"},
                    {"id": "regalos_no", "title": "No, para mí"}
                ]
            },
            "interes_ropa": {
                "body": "¿Te interesa comprar ropa?",
                "options": [
                    {"id": "ropa_si", "title": "Sí"},
                    {"id": "ropa_no", "title": "No"}
                ]
            },
            "interes_tipo_recreacion": {
                "body": "¿Qué tipo de recreación preferís?",
                "options": [
                    {"id": "recreacion_activa", "title": "Activa"},
                    {"id": "recreacion_pasiva", "title": "Pasiva"},
                    {"id": "recreacion_familiar", "title": "Familiar"},
                    {"id": "recreacion_romantica", "title": "Romántica"}
                ]
            },
            "interes_tipo_cultura": {
                "body": "¿Qué tipo de cultura te interesa más?",
                "options": [
                    {"id": "cultura_museos", "title": "Museos"},
                    {"id": "cultura_arquitectura", "title": "Arquitectura"},
                    {"id": "cultura_arte", "title": "Arte"},
                    {"id": "cultura_historia", "title": "Historia"}
                ]
            },
            "interes_tipo_comercios": {
                "body": "¿Qué tipo de comercios te interesan?",
                "options": [
                    {"id": "comercios_artesanias", "title": "Artesanías"},
                    {"id": "comercios_souvenirs", "title": "Souvenirs"},
                    {"id": "comercios_productos_locales", "title": "Productos locales"},
                    {"id": "comercios_joyeria", "title": "Joyería"},
                    {"id": "comercios_tienda_ropa", "title": "Tienda de ropa"}
                ]
            },
            "viaja_con_ninos": {
                "body": "¿Viajás con niños o familiares chicos?",
                "options": [
                    {"id": "ninos_si", "title": "Sí"},
                    {"id": "ninos_no", "title": "No"}
                ]
            }
        }
        
        if campo not in preguntas_interactivas:
            return None
        
        pregunta_data = preguntas_interactivas[campo]
        opciones = pregunta_data["options"]
        
        # Si hay 3 o menos opciones, usar botones interactivos
        if len(opciones) <= 3:
            payload = {
                "messaging_product": "whatsapp",
                "to": numero,
                "type": "interactive",
                "interactive": {
                    "type": "button",
                    "body": {
                        "text": pregunta_data["body"]
                    },
                    "action": {
                        "buttons": [
                            {
                                "type": "reply",
                                "reply": {
                                    "id": opt["id"],
                                    "title": opt["title"]
                                }
                            }
                            for opt in opciones
                        ]
                    }
                }
            }
        else:
            # Si hay más de 3 opciones, usar lista interactiva
            # Limitar a 10 opciones (límite de WhatsApp)
            opciones_limitadas = opciones[:10]
            payload = {
                "messaging_product": "whatsapp",
                "to": numero,
                "type": "interactive",
                "interactive": {
                    "type": "list",
                    "body": {
                        "text": pregunta_data["body"]
                    },
                    "action": {
                        "button": "Seleccionar",
                        "sections": [
                            {
                                "title": "Opciones",
                                "rows": [
                                    {
                                        "id": opt["id"],
                                        "title": opt["title"][:24]  # Limitar título a 24 caracteres
                                    }
                                    for opt in opciones_limitadas
                                ]
                            }
                        ]
                    }
                }
            }
        
        return payload
    
    def _detectar_intereses_texto(self, texto: str) -> List[str]:
        """
        Detecta intereses del texto del usuario.
        Soporta:
        - Números: "1 2 3" → restaurantes, comercios, recreacion
        - Letras: "A B C" → restaurantes, comercios, recreacion
        - Nombres completos o parciales: "restaurantes compras recreacion"
        - "todo" → todos los intereses
        """
        if not texto or not texto.strip():
            return []
        
        texto_lower = texto.lower().strip()
        
        # Mapeo de intereses
        intereses_map = {
            "1": "restaurantes",
            "a": "restaurantes",
            "restaurante": "restaurantes",
            "restaurantes": "restaurantes",
            "comida": "restaurantes",
            "2": "comercios",
            "b": "comercios",
            "comercio": "comercios",
            "comercios": "comercios",
            "tienda": "comercios",
            "tiendas": "comercios",
            "3": "recreacion",
            "c": "recreacion",
            "recreacion": "recreacion",
            "recreación": "recreacion",
            "recreativo": "recreacion",
            "parque": "recreacion",
            "parques": "recreacion",
            "4": "cultura",
            "d": "cultura",
            "cultura": "cultura",
            "museo": "cultura",
            "museos": "cultura",
            "paseo": "cultura",
            "paseos": "cultura",
            "5": "compras",
            "e": "compras",
            "compra": "compras",
            "compras": "compras",
            "shopping": "compras",
            "regalo": "compras",
            "regalos": "compras"
        }
        
        intereses_validos = ["restaurantes", "comercios", "recreacion", "cultura", "compras"]
        intereses_detectados = []
        
        # Si dice "todo", seleccionar todos
        if texto_lower in ("todo", "todos", "all", "t"):
            return intereses_validos
        
        # Dividir el texto por espacios, comas, puntos o punto y coma
        # Manejar tanto "1 2 3" como "1,2,3" o "1.2.3" o "1;2;3"
        texto_limpio = texto_lower.replace(",", " ").replace(".", " ").replace(";", " ")
        
        # Separar números mayores a 9 en dígitos individuales (ej: "15" → "1 5", "123" → "1 2 3")
        # Solo hay 5 intereses, así que cualquier número con más de 1 dígito debe separarse
        # Encontrar números de 2 o más dígitos y separarlos en dígitos individuales
        def separar_digitos(match):
            numero = match.group(0)
            return " ".join(list(numero))
        
        texto_limpio = re.sub(r'\d{2,}', separar_digitos, texto_limpio)
        
        palabras = texto_limpio.split()
        
        for palabra in palabras:
            palabra_limpia = palabra.strip()
            # Verificar coincidencia exacta primero (más rápido y preciso)
            if palabra_limpia in intereses_map:
                interes = intereses_map[palabra_limpia]
                if interes not in intereses_detectados:
                    intereses_detectados.append(interes)
            else:
                # Buscar coincidencias parciales solo si la palabra tiene más de 2 caracteres
                # (evita falsos positivos con números de un solo dígito)
                if len(palabra_limpia) > 2:
                    for key, interes in intereses_map.items():
                        if key in palabra_limpia or palabra_limpia in key:
                            if interes not in intereses_detectados:
                                intereses_detectados.append(interes)
                            break
        
        return intereses_detectados
    
    def _obtener_nombre_interes(self, interes: str) -> str:
        """Obtiene el nombre amigable de un interés"""
        nombres = {
            "restaurantes": "Restaurantes",
            "comercios": "Comercios",
            "recreacion": "Recreación",
            "cultura": "Cultura",
            "compras": "Compras"
        }
        return nombres.get(interes, interes.capitalize())
    
    def _procesar_respuesta_interactiva(self, texto: str) -> Optional[Dict[str, Any]]:
        """Procesa una respuesta de botón interactivo y retorna campo y valor"""
        mapeo_respuestas = {
            # Tipo de viaje
            "tipo_viaje_solo": ("tipo_viaje", "solo"),
            "tipo_viaje_pareja": ("tipo_viaje", "pareja"),
            "tipo_viaje_familia": ("tipo_viaje", "familia"),
            "tipo_viaje_amigos": ("tipo_viaje", "amigos"),
            "tipo_viaje_negocios": ("tipo_viaje", "negocios"),
            # Duración
            "duracion_1_2": ("duracion_estadia", 2),
            "duracion_3_5": ("duracion_estadia", 4),
            "duracion_mas_5": ("duracion_estadia", 7),
            # Preferencias comida
            "comida_local": ("preferencias_comida", "local"),
            "comida_internacional": ("preferencias_comida", "internacional"),
            "comida_vegetariano": ("preferencias_comida", "vegetariano"),
            "comida_vegano": ("preferencias_comida", "vegano"),
            "comida_sin_restricciones": ("preferencias_comida", "sin_restricciones"),
            # Interés regalos
            "regalos_si": ("interes_regalos", True),
            "regalos_no": ("interes_regalos", False),
            # Interés ropa
            "ropa_si": ("interes_ropa", True),
            "ropa_no": ("interes_ropa", False),
            # Tipo recreación
            "recreacion_activa": ("interes_tipo_recreacion", "activa"),
            "recreacion_pasiva": ("interes_tipo_recreacion", "pasiva"),
            "recreacion_familiar": ("interes_tipo_recreacion", "familiar"),
            "recreacion_romantica": ("interes_tipo_recreacion", "romantica"),
            # Tipo cultura
            "cultura_museos": ("interes_tipo_cultura", "museos"),
            "cultura_arquitectura": ("interes_tipo_cultura", "arquitectura"),
            "cultura_arte": ("interes_tipo_cultura", "arte"),
            "cultura_historia": ("interes_tipo_cultura", "historia"),
            # Tipo comercios
            "comercios_artesanias": ("interes_tipo_comercios", "artesanias"),
            "comercios_souvenirs": ("interes_tipo_comercios", "souvenirs"),
            "comercios_productos_locales": ("interes_tipo_comercios", "productos_locales"),
            "comercios_joyeria": ("interes_tipo_comercios", "joyeria"),
            "comercios_tienda_ropa": ("interes_tipo_comercios", "tienda_ropa"),
            # Viaja con niños
            "ninos_si": ("viaja_con_ninos", True),
            "ninos_no": ("viaja_con_ninos", False)
        }
        
        if texto in mapeo_respuestas:
            campo, valor = mapeo_respuestas[texto]
            return {"campo": campo, "valor": valor}
        
        return None
    
    def flujo_armando_perfil(self, numero, texto):
        """Flujo para armar el perfil del usuario con preguntas progresivas"""
        usuario = UsuarioService.obtener_o_crear_usuario(numero)
        
        # Rechazar botones obsoletos de intereses si estamos en este flujo
        if texto in ("agregar_mas_intereses", "continuar_intereses"):
            # Botón obsoleto, ignorar y continuar con el flujo normal
            texto = ""  # Tratar como entrada inicial
        
        # IMPORTANTE: Si el perfil ya está completo y no es un ajuste explícito, NO volver a preguntar
        if usuario.tiene_perfil_completo() and texto.lower() not in ("ajustar plan", "ajustar", "modificar", "cambiar"):
            # Perfil completo, pasar a seguimiento o generación según contexto
            if usuario.estado_conversacion == ESTADOS_BOT["SEGUIMIENTO"]:
                return self.flujo_seguimiento(numero, texto)
            else:
                # Si no hay plan generado, generarlo
                set_estado_bot(numero, ESTADOS_BOT["GENERANDO_PLAN"])
                usuario.estado_conversacion = ESTADOS_BOT["GENERANDO_PLAN"]
                UsuarioService.actualizar_usuario(usuario)
                return self.flujo_generando_plan(numero, texto)
        
        # Inicializar perfil si no existe
        if not usuario.perfil:
            UsuarioService.inicializar_perfil(numero)
            usuario = UsuarioService.obtener_usuario_por_telefono(numero)
        
        # Si el texto está vacío o es "continuar_intereses", significa que entramos desde selección de intereses
        # No procesar como respuesta, solo mostrar la primera pregunta
        procesar_respuesta = texto and texto.strip() and texto != "continuar_intereses"
        
        if procesar_respuesta:
            # Procesar respuesta (puede ser botón interactivo o texto)
            respuesta_procesada = self._procesar_respuesta_interactiva(texto)
            
            if respuesta_procesada:
                # Es una respuesta de botón interactivo
                campo = respuesta_procesada["campo"]
                valor = respuesta_procesada["valor"]
                UsuarioService.actualizar_perfil(numero, campo, valor)
                usuario = UsuarioService.obtener_usuario_por_telefono(numero)
            elif texto.lower() not in ("ajustar plan", "ajustar", "modificar", "cambiar"):
                # Interpretar respuesta del usuario usando Gemini (texto libre)
                interpretacion = GeminiOrchestratorService.interpretar_mensaje_usuario(
                    texto,
                    usuario
                )
                
                # Si detectó una respuesta a un campo del perfil
                if interpretacion and interpretacion.get("respuesta_detectada") and interpretacion.get("campo_perfil"):
                    campo = interpretacion.get("campo_perfil")
                    valor = interpretacion.get("valor_detectado")
                    
                    # Actualizar perfil
                    UsuarioService.actualizar_perfil(numero, campo, valor)
                    usuario = UsuarioService.obtener_usuario_por_telefono(numero)
        
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
            # Detectar qué campo se está preguntando
            campo_pregunta = None
            if "tipo de viaje" in siguiente_pregunta.lower():
                campo_pregunta = "tipo_viaje"
            elif "comida" in siguiente_pregunta.lower():
                campo_pregunta = "preferencias_comida"
            elif "regalar" in siguiente_pregunta.lower():
                campo_pregunta = "interes_regalos"
            elif "ropa" in siguiente_pregunta.lower():
                campo_pregunta = "interes_ropa"
            elif "recreación" in siguiente_pregunta.lower() or "recreacion" in siguiente_pregunta.lower():
                campo_pregunta = "interes_tipo_recreacion"
            elif "cultura" in siguiente_pregunta.lower():
                campo_pregunta = "interes_tipo_cultura"
            elif "comercios" in siguiente_pregunta.lower() or "comercio" in siguiente_pregunta.lower():
                campo_pregunta = "interes_tipo_comercios"
            elif "niños" in siguiente_pregunta.lower() or "ninos" in siguiente_pregunta.lower() or "chicos" in siguiente_pregunta.lower():
                campo_pregunta = "viaja_con_ninos"
            elif "días" in siguiente_pregunta.lower() or "dias" in siguiente_pregunta.lower():
                campo_pregunta = "duracion_estadia"
            
            set_pregunta_actual(numero, campo_pregunta)
            set_estado_bot(numero, ESTADOS_BOT["ARMANDO_PERFIL"])
            usuario.estado_conversacion = ESTADOS_BOT["ARMANDO_PERFIL"]
            UsuarioService.actualizar_usuario(usuario)
            self.set_waiting_for(numero, "flujo_armando_perfil")
            
            # Enviar pregunta interactiva si está disponible, sino texto simple
            if campo_pregunta:
                payload_interactivo = self._crear_pregunta_interactiva(numero, campo_pregunta)
                if payload_interactivo:
                    return enviar_mensaje_whatsapp(numero, payload_interactivo)
            
            # Fallback a texto simple si no hay versión interactiva
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
        
        # NO enviar mensaje de seguimiento automáticamente
        # Solo esperar a que el usuario escriba algo
        return None
    
    def flujo_seguimiento(self, numero, texto):
        """Ofrece ayuda adicional después de presentar el plan"""
        usuario = UsuarioService.obtener_o_crear_usuario(numero)
        
        texto_lower = texto.lower()
        
        # Procesar respuestas de botones interactivos
        if texto in ("seguimiento_ajustar", "seguimiento_nuevo", "seguimiento_consulta"):
            if texto == "seguimiento_ajustar":
                set_estado_bot(numero, ESTADOS_BOT["ARMANDO_PERFIL"])
                usuario.estado_conversacion = ESTADOS_BOT["ARMANDO_PERFIL"]
                UsuarioService.actualizar_usuario(usuario)
                return self.flujo_armando_perfil(numero, "ajustar plan")
            elif texto == "seguimiento_nuevo":
                set_estado_bot(numero, ESTADOS_BOT["GENERANDO_PLAN"])
                usuario.estado_conversacion = ESTADOS_BOT["GENERANDO_PLAN"]
                UsuarioService.actualizar_usuario(usuario)
                return self.flujo_generando_plan(numero, texto)
            elif texto == "seguimiento_consulta":
                mensaje = (
                    "Escribime tu consulta y te ayudo a resolverla. "
                    "Puedo ayudarte con información sobre lugares, restaurantes, actividades, etc."
                )
                set_estado_bot(numero, ESTADOS_BOT["SEGUIMIENTO"])
                usuario.estado_conversacion = ESTADOS_BOT["SEGUIMIENTO"]
                UsuarioService.actualizar_usuario(usuario)
                return enviar_mensaje_whatsapp(numero, mensaje)
        
        # IMPORTANTE: Si el perfil está completo, NO volver a preguntar
        # Solo procesar comandos específicos o consultas generales
        if usuario.tiene_perfil_completo():
            # Procesar comandos directos
            if texto_lower in ("ajustar", "modificar", "cambiar", "reorganizar", "reorganizar plan"):
                # Volver a armando perfil (pero mantener datos existentes)
                set_estado_bot(numero, ESTADOS_BOT["ARMANDO_PERFIL"])
                usuario.estado_conversacion = ESTADOS_BOT["ARMANDO_PERFIL"]
                UsuarioService.actualizar_usuario(usuario)
                return self.flujo_armando_perfil(numero, "ajustar plan")
            
            if texto_lower in ("nuevo plan", "otro", "generar otro", "otro plan"):
                # Generar nuevo plan con el mismo perfil
                set_estado_bot(numero, ESTADOS_BOT["GENERANDO_PLAN"])
                usuario.estado_conversacion = ESTADOS_BOT["GENERANDO_PLAN"]
                UsuarioService.actualizar_usuario(usuario)
                return self.flujo_generando_plan(numero, texto)
            
            # Detectar keywords para "más opciones" sin usar Gemini
            keywords_mas_opciones = [
                "mas opciones", "más opciones", "otras opciones", "otra opcion", "otra opción",
                "mas lugares", "más lugares", "otros lugares", "otro lugar",
                "mas recomendaciones", "más recomendaciones", "otras recomendaciones",
                "ver mas", "ver más", "mostrar mas", "mostrar más"
            ]
            
            if any(keyword in texto_lower for keyword in keywords_mas_opciones):
                # Opción 1: Mostrar lista de intereses de nuevo
                # Opción 2: Enviar un lugar random de los intereses del usuario
                import random
                plan = self.conversation_data.get('plan_viaje')
                
                if plan and plan.excursiones:
                    # Enviar un lugar random del plan
                    lugar_random = random.choice(plan.excursiones)
                    
                    if lugar_random.imagen_url:
                        caption = f"*{lugar_random.nombre}*\n\n{lugar_random.descripcion}"
                        if lugar_random.ubicacion:
                            caption += f"\n\n📍 {lugar_random.ubicacion}"
                        
                        if len(caption) > 1024:
                            caption = caption[:1021] + "..."
                        
                        from whatsapp_api import enviar_imagen_whatsapp
                        resultado = enviar_imagen_whatsapp(numero, lugar_random.imagen_url, caption)
                        if not resultado.get("success"):
                            # Si falla, enviar solo texto
                            mensaje = f"*{lugar_random.nombre}*\n\n{lugar_random.descripcion}"
                            if lugar_random.ubicacion:
                                mensaje += f"\n\n📍 {lugar_random.ubicacion}"
                            return enviar_mensaje_whatsapp(numero, mensaje)
                        return resultado
                    else:
                        # Enviar solo texto
                        mensaje = f"*{lugar_random.nombre}*\n\n{lugar_random.descripcion}"
                        if lugar_random.ubicacion:
                            mensaje += f"\n\n📍 {lugar_random.ubicacion}"
                        return enviar_mensaje_whatsapp(numero, mensaje)
                else:
                    # Si no hay plan, mostrar lista de intereses
                    return self._mostrar_mensaje_intereses(numero, usuario, False)
            
            # Verificar que el mensaje NO sea del bot antes de llamar a Gemini
            texto_lower = texto.lower()
            texto_stripped = texto.strip()
            texto_len = len(texto_stripped)
            
            # Patrones específicos de mensajes del bot
            patrones_bot_exactos = [
                "código qr -",
                "📱 código qr -",
                "📱 *código qr -",
                "escanea este código",
                "escanea el código qr",
            ]
            
            # Verificar si empieza con un patrón del bot
            empieza_con_bot = any(texto_lower.startswith(patron) for patron in patrones_bot_exactos)
            
            # Verificar si contiene patrones de QR
            contiene_qr = any(patron in texto_lower for patron in ["código qr", "codigo qr", "qr -", "código qr -", "📱 código", "📱 *código"])
            
            # Verificar si contiene el patrón completo de QR con "escanea"
            es_mensaje_qr_completo = ("código qr -" in texto_lower or "codigo qr -" in texto_lower) and "escanea" in texto_lower
            
            # Si el mensaje es muy corto y contiene QR, probablemente es del bot
            es_mensaje_corto_qr = texto_len < 50 and contiene_qr
            
            # DETECCIÓN AGRESIVA: Si contiene "QR" y "escanea" en cualquier parte, es del bot
            es_mensaje_qr_agresivo = ("qr" in texto_lower or "codigo" in texto_lower) and "escanea" in texto_lower and texto_len < 150
            
            # Si parece ser un mensaje del bot, NO llamar a Gemini
            if empieza_con_bot or es_mensaje_corto_qr or es_mensaje_qr_completo or es_mensaje_qr_agresivo:
                print(f"⚠️ [flujo_seguimiento] Ignorando mensaje que parece ser del bot:")
                print(f"   - Empieza con patrón bot: {empieza_con_bot}")
                print(f"   - Mensaje corto con QR: {es_mensaje_corto_qr}")
                print(f"   - Mensaje QR completo: {es_mensaje_qr_completo}")
                print(f"   - Mensaje QR agresivo: {es_mensaje_qr_agresivo}")
                print(f"   - Mensaje: {texto[:100]}...")
                return None  # No procesar, no responder
            
            # Si no es un comando específico, usar Gemini para generar respuesta amigable
            respuesta_amigable = GeminiOrchestratorService.generar_respuesta_amigable(
                texto,
                usuario,
                contexto_estado=f"El usuario tiene un plan completo y está en seguimiento. Ciudad: {usuario.ciudad}"
            )
            
            set_estado_bot(numero, ESTADOS_BOT["SEGUIMIENTO"])
            usuario.estado_conversacion = ESTADOS_BOT["SEGUIMIENTO"]
            UsuarioService.actualizar_usuario(usuario)
            
            return enviar_mensaje_whatsapp(numero, respuesta_amigable)
        else:
            # Si el perfil NO está completo y el usuario escribe algo, NO continuar automáticamente
            # Solo procesar si el usuario escribe un comando específico o consulta
            # Si el texto está vacío o es muy corto, no hacer nada
            if not texto or len(texto.strip()) < 2:
                return None
            
            # Verificar que el mensaje NO sea del bot antes de llamar a Gemini
            texto_lower_check = texto.lower()
            texto_stripped_check = texto.strip()
            texto_len_check = len(texto_stripped_check)
            
            # Patrones específicos de mensajes del bot
            patrones_bot_exactos_check = [
                "código qr -",
                "📱 código qr -",
                "📱 *código qr -",
                "escanea este código",
                "escanea el código qr",
            ]
            
            # Verificar si empieza con un patrón del bot
            empieza_con_bot_check = any(texto_lower_check.startswith(patron) for patron in patrones_bot_exactos_check)
            
            # Verificar si contiene patrones de QR
            contiene_qr_check = any(patron in texto_lower_check for patron in ["código qr", "codigo qr", "qr -", "código qr -", "📱 código", "📱 *código"])
            
            # Verificar si contiene el patrón completo de QR con "escanea"
            es_mensaje_qr_completo_check = ("código qr -" in texto_lower_check or "codigo qr -" in texto_lower_check) and "escanea" in texto_lower_check
            
            # Si el mensaje es muy corto y contiene QR, probablemente es del bot
            es_mensaje_corto_qr_check = texto_len_check < 50 and contiene_qr_check
            
            # DETECCIÓN AGRESIVA: Si contiene "QR" y "escanea" en cualquier parte, es del bot
            es_mensaje_qr_agresivo_check = ("qr" in texto_lower_check or "codigo" in texto_lower_check) and "escanea" in texto_lower_check and texto_len_check < 150
            
            # Si parece ser un mensaje del bot, NO llamar a Gemini
            if empieza_con_bot_check or es_mensaje_corto_qr_check or es_mensaje_qr_completo_check or es_mensaje_qr_agresivo_check:
                print(f"⚠️ [flujo_seguimiento] Ignorando mensaje que parece ser del bot (perfil incompleto):")
                print(f"   - Empieza con patrón bot: {empieza_con_bot_check}")
                print(f"   - Mensaje corto con QR: {es_mensaje_corto_qr_check}")
                print(f"   - Mensaje QR completo: {es_mensaje_qr_completo_check}")
                print(f"   - Mensaje QR agresivo: {es_mensaje_qr_agresivo_check}")
                print(f"   - Mensaje: {texto[:100]}...")
                return None  # No procesar, no responder
            
            # Si el usuario escribe algo específico, procesarlo
            # Pero NO continuar automáticamente con armar perfil después de enviar el plan
            # Solo usar Gemini para responder amigablemente
            respuesta_amigable = GeminiOrchestratorService.generar_respuesta_amigable(
                texto,
                usuario,
                contexto_estado=f"El usuario tiene un plan pero el perfil no está completo. Ciudad: {usuario.ciudad}"
            )
            
            set_estado_bot(numero, ESTADOS_BOT["SEGUIMIENTO"])
            usuario.estado_conversacion = ESTADOS_BOT["SEGUIMIENTO"]
            UsuarioService.actualizar_usuario(usuario)
            
            return enviar_mensaje_whatsapp(numero, respuesta_amigable)
