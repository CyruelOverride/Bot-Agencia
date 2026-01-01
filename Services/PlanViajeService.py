from typing import List, Optional
import os
import logging
from Models.plan_viaje import PlanViaje
from Models.usuario import Usuario
from Models.excursion import Excursion
from Services.ExcursionService import ExcursionService
from Services.GeminiOrchestratorService import GeminiOrchestratorService
from Util.qr_helper import obtener_ruta_qr, debe_enviar_qr

logger = logging.getLogger(__name__)


class PlanViajeService:
    @staticmethod
    def generar_plan_personalizado(usuario: Usuario, lugares_excluidos: Optional[List[str]] = None) -> PlanViaje:
        """
        Genera un plan de viaje personalizado para un usuario basado en su perfil e intereses.
        
        Args:
            usuario: Usuario para el cual generar el plan
            lugares_excluidos: Lista opcional de IDs de lugares a excluir (para evitar duplicados)
        """
        if not usuario.ciudad:
            raise ValueError("El usuario debe tener una ciudad asignada")
        
        if not usuario.intereses:
            raise ValueError("El usuario debe tener al menos un interés seleccionado")
        
        # Inicializar lista de lugares excluidos si no se proporciona
        if lugares_excluidos is None:
            lugares_excluidos = []
        
        # LOGGING: Intereses del usuario antes de generar plan
        print(f"🔍 [GENERAR_PLAN] Intereses del usuario: {usuario.intereses}")
        print(f"🔍 [GENERAR_PLAN] Ciudad: {usuario.ciudad}")
        print(f"🔍 [GENERAR_PLAN] Lugares excluidos: {len(lugares_excluidos)} lugares")
        
        # Obtener excursiones filtradas por intereses y perfil
        excursiones = ExcursionService.obtener_excursiones_por_intereses(
            ciudad=usuario.ciudad,
            intereses=usuario.intereses,
            perfil=usuario.perfil
        )
        
        # Excluir lugares ya enviados
        if lugares_excluidos:
            excursiones = [exc for exc in excursiones if exc.id not in lugares_excluidos]
            print(f"🔍 [GENERAR_PLAN] Después de excluir lugares ya enviados: {len(excursiones)} excursiones")
        
        print(f"🔍 [GENERAR_PLAN] Excursiones después de filtrar por intereses: {len(excursiones)}")
        for exc in excursiones:
            print(f"   - {exc.nombre} (ID: {exc.id}, Categoría: {exc.categoria})")
        
        # Verificar que cada interés tenga al menos una excursión
        ids_existentes = {exc.id for exc in excursiones}
        excursiones_por_interes = {}
        for interes in usuario.intereses:
            excursiones_por_interes[interes] = [e for e in excursiones if e.categoria.lower() == interes.lower()]
            print(f"🔍 [GENERAR_PLAN] Interés '{interes}': {len(excursiones_por_interes[interes])} excursiones")
        
        # Completar intereses faltantes SOLO si el interés está en la lista del usuario
        for interes in usuario.intereses:
            if not excursiones_por_interes.get(interes):
                print(f"🔍 [GENERAR_PLAN] Interés '{interes}' no tiene excursiones, buscando una...")
                # Buscar al menos una excursión de este interés
                excursiones_interes = ExcursionService.obtener_excursiones_por_categoria(usuario.ciudad, interes)
                if excursiones_interes:
                    # Agregar la primera que no esté ya en la lista y no esté excluida
                    for exc in excursiones_interes:
                        if exc.id not in ids_existentes and exc.id not in lugares_excluidos:
                            excursiones.append(exc)
                            ids_existentes.add(exc.id)
                            print(f"🔍 [GENERAR_PLAN] Agregada excursión para completar interés '{interes}': {exc.nombre} (ID: {exc.id})")
                            break
        
        # Limitar a máximo 15 excursiones para no sobrecargar
        excursiones = excursiones[:15]
        
        # Si no hay suficientes, agregar más SOLO de los intereses del usuario
        if len(excursiones) < 5:
            print(f"🔍 [GENERAR_PLAN] Solo hay {len(excursiones)} excursiones, agregando más de los intereses del usuario...")
            todas_las_excursiones = ExcursionService.obtener_excursiones_por_ciudad(usuario.ciudad)
            categorias_interes = [interes.lower() for interes in usuario.intereses]
            print(f"🔍 [GENERAR_PLAN] Categorías de interés del usuario: {categorias_interes}")
            
            excursiones_adicionales = [
                exc for exc in todas_las_excursiones
                if exc.categoria.lower() in categorias_interes or any(
                    cat in exc.categoria.lower() for cat in categorias_interes
                )
            ]
            print(f"🔍 [GENERAR_PLAN] Excursiones adicionales encontradas: {len(excursiones_adicionales)}")
            
            # Agregar sin duplicar SOLO de los intereses del usuario y excluyendo lugares ya enviados
            for exc in excursiones_adicionales:
                if exc.id not in ids_existentes and exc.id not in lugares_excluidos and len(excursiones) < 15:
                    # VERIFICAR que la categoría coincida con algún interés del usuario
                    if exc.categoria.lower() in categorias_interes:
                        excursiones.append(exc)
                        ids_existentes.add(exc.id)
                        print(f"🔍 [GENERAR_PLAN] Agregada excursión adicional: {exc.nombre} (ID: {exc.id}, Categoría: {exc.categoria})")
        
        # Filtrar excursiones: solo incluir las que tienen imagen
        excursiones = [exc for exc in excursiones if exc.imagen_url]
        
        # Limitar total a 15
        excursiones = excursiones[:15]
        
        # Generar resumen con Gemini
        resumen_ia = GeminiOrchestratorService.generar_resumen_plan(usuario, excursiones)
        
        # Crear plan de viaje
        plan = PlanViaje(
            usuario_id=usuario.telefono,
            ciudad=usuario.ciudad,
            resumen_ia=resumen_ia,
            excursiones=excursiones
        )
        
        return plan
    
    @staticmethod
    def formatear_plan_para_whatsapp(plan: PlanViaje) -> str:
        """
        Formatea un plan de viaje para enviarlo por WhatsApp.
        Retorna un string formateado con emojis y estructura clara.
        """
        mensaje = f"{plan.resumen_ia}\n\n"
        
        # Agrupar excursiones por categoría
        excursiones_por_categoria = plan.obtener_excursiones_por_categoria()
        
        # Emojis por categoría
        emojis_categoria = {
            "restaurantes": "🍽️",
            "comercios": "🛍️",
            "compras": "🛒"
        }
        
        # Nombres de categoría en español
        nombres_categoria = {
            "restaurantes": "Restaurantes",
            "comercios": "Comercios",
            "compras": "Compras"
        }
        
        for categoria, excursiones in excursiones_por_categoria.items():
            emoji = emojis_categoria.get(categoria, "📍")
            nombre = nombres_categoria.get(categoria, categoria.capitalize())
            
            mensaje += f"{emoji} *{nombre}*\n"
            
            for exc in excursiones:
                mensaje += f"• *{exc.nombre}*"
                if exc.ubicacion:
                    mensaje += f" - {exc.ubicacion}"
                mensaje += f"\n  {exc.descripcion}\n"
            
            mensaje += "\n"
        
        return mensaje.strip()
    
    @staticmethod
    def formatear_plan_para_whatsapp_interactivo(plan: PlanViaje) -> dict:
        """
        Formatea un plan de viaje como mensaje interactivo de WhatsApp.
        Retorna un dict con la estructura de mensaje interactivo.
        """
        # Agrupar excursiones por categoría
        excursiones_por_categoria = plan.obtener_excursiones_por_categoria()
        
        # Crear secciones para el mensaje interactivo
        secciones = []
        rows = []
        
        for categoria, excursiones in excursiones_por_categoria.items():
            emojis_categoria = {
                "restaurantes": "🍽️",
                "comercios": "🛍️",
                "compras": "🛒"
            }
            
            nombres_categoria = {
                "restaurantes": "Restaurantes",
                "comercios": "Comercios",
                "compras": "Compras"
            }
            
            emoji = emojis_categoria.get(categoria, "📍")
            nombre = nombres_categoria.get(categoria, categoria.capitalize())
            
            for exc in excursiones:
                descripcion_corta = exc.descripcion[:60] + "..." if len(exc.descripcion) > 60 else exc.descripcion
                # Limitar título a 24 caracteres (límite de WhatsApp para listas interactivas)
                titulo_completo = f"{emoji} {exc.nombre}"
                titulo_limitado = titulo_completo[:24] if len(titulo_completo) > 24 else titulo_completo
                rows.append({
                    "id": f"exc_{exc.id}",
                    "title": titulo_limitado,
                    "description": descripcion_corta
                })
        
        if rows:
            secciones.append({
                "title": "Lugares Recomendados",
                "rows": rows[:10]  # WhatsApp limita a 10 opciones por sección
            })
        
        return {
            "messaging_product": "whatsapp",
            "to": plan.usuario_id,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "header": {
                    "type": "text",
                    "text": "📋 Tu Plan de Viaje Personalizado"
                },
                "body": {
                    "text": plan.resumen_ia[:200] + "..." if len(plan.resumen_ia) > 200 else plan.resumen_ia
                },
                "footer": {
                    "text": (f"{plan.ciudad} - {len(plan.excursiones)} recomendaciones")[:60]
                },
                "action": {
                    "button": "Ver lugares",
                    "sections": secciones
                }
            }
        }
    
    @staticmethod
    def enviar_plan_con_imagen(numero: str, plan: PlanViaje, ruta_imagen: Optional[str] = None):
        """
        Envía el plan con un mensaje individual por cada lugar.
        Primero envía imagen con resumen, luego cada excursión en mensajes separados con su imagen.
        
        Args:
            numero: Número de teléfono del usuario
            plan: Plan de viaje a enviar
            ruta_imagen: Ruta opcional a la imagen del resumen. Si no se proporciona, busca automáticamente
        """
        from whatsapp_api import enviar_imagen_whatsapp, enviar_mensaje_whatsapp
        import time
        
        # Determinar imagen a usar para el primer mensaje (resumen del plan)
        # Usar imagen hardcodeada específica para el mensaje de introducción
        imagen_a_enviar = "https://www.clarin.com/img/2019/07/03/k2EHmOpGl_1256x620__1.jpg"
        
        # Si se proporciona una imagen explícitamente, usar esa en su lugar
        if ruta_imagen:
            imagen_a_enviar = ruta_imagen
        
        # Mensaje 1: Enviar imagen con resumen (si existe)
        if imagen_a_enviar:
            try:
                # Caption con resumen corto (500-700 chars recomendado, usamos 700 como máximo seguro)
                caption = f"🎯 Tu Plan Personalizado para {plan.ciudad}\n\n{plan.resumen_ia[:700]}"
                
                resultado = enviar_imagen_whatsapp(numero, imagen_a_enviar, caption)
                
                if resultado.get("success"):
                    # Pausa para mejor UX
                    time.sleep(2)
                else:
                    logger.warning(f"No se pudo enviar imagen del plan: {resultado.get('error', 'Error desconocido')}")
                    # Si falla la imagen, enviar resumen como texto
                    mensaje_resumen = f"🎯 *Tu Plan Personalizado para {plan.ciudad}*\n\n{plan.resumen_ia[:700]}"
                    enviar_mensaje_whatsapp(numero, mensaje_resumen)
                    time.sleep(1)
                    
            except Exception as e:
                # Error silencioso: enviar resumen como texto
                logger.warning(f"No se pudo enviar imagen del plan: {e}")
                mensaje_resumen = f"🎯 *Tu Plan Personalizado para {plan.ciudad}*\n\n{plan.resumen_ia[:700]}"
                enviar_mensaje_whatsapp(numero, mensaje_resumen)
                time.sleep(1)
        else:
            # Si no hay imagen, enviar resumen como texto
            mensaje_resumen = f"🎯 *Tu Plan Personalizado para {plan.ciudad}*\n\n{plan.resumen_ia[:700]}"
            enviar_mensaje_whatsapp(numero, mensaje_resumen)
            time.sleep(1)
        
        # Mensajes 2-N: Enviar un mensaje individual por cada lugar de cada interés
        # Obtener usuario para loggear intereses
        from Services.UsuarioService import UsuarioService
        usuario = UsuarioService.obtener_usuario_por_telefono(numero)
        
        # LOGGING CRÍTICO: Intereses del cliente
        if usuario:
            print(f"🔍 [LOGGING] Intereses del cliente: {usuario.intereses}")
            print(f"🔍 [LOGGING] Ciudad: {usuario.ciudad}")
            if usuario.perfil:
                print(f"🔍 [LOGGING] Perfil - Tipo viaje: {usuario.perfil.tipo_viaje}, Duración: {usuario.perfil.duracion_estadia}")
        else:
            print(f"⚠️ [LOGGING] No se pudo obtener usuario para {numero}")
        
        # Agrupar excursiones por categoría (interés)
        excursiones_por_categoria = plan.obtener_excursiones_por_categoria()
        
        print(f"📋 Iniciando envío de mensajes individuales. Total de categorías: {len(excursiones_por_categoria)}")
        print(f"📋 Excursiones en el plan: {len(plan.excursiones)}")
        
        # LOGGING CRÍTICO: Qué excursiones se van a enviar
        print(f"🔍 [LOGGING] Excursiones que se enviarán:")
        for exc in plan.excursiones:
            print(f"   - {exc.nombre} (ID: {exc.id}, Categoría: {exc.categoria})")
        
        # Emojis por categoría
        emojis_categoria = {
            "restaurantes": "🍽️",
            "comercios": "🛍️",
            "compras": "🛒"
        }
        
        # Recorrer cada categoría (interés)
        for categoria, excursiones in excursiones_por_categoria.items():
            emoji = emojis_categoria.get(categoria, "📍")
            print(f"📤 Procesando categoría: {categoria} ({emoji}) - {len(excursiones)} lugares")
            
            # Para cada lugar (excursión) de este interés, enviar un mensaje individual
            for excursion in excursiones:
                print(f"  → Enviando lugar: {excursion.nombre}")
                print(f"     - Tiene imagen: {excursion.imagen_url is not None}")
                print(f"     - Tiene descripción: {len(excursion.descripcion) > 0 if excursion.descripcion else False}")
                print(f"     - Tiene ubicación: {excursion.ubicacion is not None}")
                try:
                    # Construir mensaje con descripción y ubicación
                    descripcion = excursion.descripcion if excursion.descripcion else "Sin descripción disponible"
                    ubicacion = excursion.ubicacion if excursion.ubicacion else None
                    
                    # Verificar si es restaurante/comercio y obtener QR primero
                    ruta_qr = None
                    if debe_enviar_qr(excursion.categoria):
                        try:
                            print(f"     📱 Generando QR para {excursion.nombre} (ID: {excursion.id})")
                            ruta_qr = obtener_ruta_qr(excursion.id)
                            if ruta_qr and os.path.exists(ruta_qr):
                                print(f"     ✅ QR generado: {ruta_qr}")
                            else:
                                print(f"     ⚠️ QR no disponible para {excursion.nombre}")
                                logger.warning(f"QR no disponible para {excursion.nombre} (ID: {excursion.id})")
                        except Exception as e:
                            print(f"     ⚠️ Error al generar QR: {e}")
                            logger.warning(f"No se pudo generar QR para {excursion.nombre}: {e}")
                            # Para lugares con caracteres especiales como "Charco Bistró", intentar manejo especial
                            if "bistró" in excursion.nombre.lower() or "bistro" in excursion.nombre.lower():
                                try:
                                    print(f"     🔄 Intentando manejo especial para caracteres especiales en: {excursion.nombre}")
                                    # Limpiar caracteres especiales del nombre para el QR
                                    nombre_limpio = excursion.nombre.replace("ó", "o").replace("í", "i").replace("ú", "u")
                                    print(f"     🔄 Nombre limpiado: {nombre_limpio}")
                                    ruta_qr = obtener_ruta_qr(excursion.id)
                                except Exception as e2:
                                    print(f"     ❌ Error persistente con caracteres especiales: {e2}")
                    
                    # VERIFICACIÓN DE 2 PARTES: Primero enviar información, solo entonces QR
                    descripcion = excursion.descripcion if excursion.descripcion else "Sin descripción disponible"
                    ubicacion = excursion.ubicacion if excursion.ubicacion else None
                    info_enviada_exitosamente = False

                    # PARTE 1: Enviar información del lugar
                    if excursion.imagen_url:
                        # Intentar enviar imagen primero
                        caption = f"*{excursion.nombre}*\n\n{descripcion}"
                        if ubicacion:
                            caption += f"\n\n📍 {ubicacion}"
                        if ruta_qr:
                            caption += f"\n\n*A continuación te enviaremos un código QR el cual puedes enseñar al momento de pagar para acceder a un descuento.*"

                        if len(caption) > 1024:
                            caption = caption[:1021] + "..."

                        try:
                            resultado = enviar_imagen_whatsapp(numero, excursion.imagen_url, caption)
                            if resultado.get("success"):
                                print(f"     ✅ Información del lugar enviada exitosamente (imagen)")
                                info_enviada_exitosamente = True
                            else:
                                # Fallback a texto si falla la imagen
                                print(f"     ⚠️ Error al enviar imagen, intentando con texto...")
                                mensaje = f"*{excursion.nombre}*\n\n{descripcion}"
                                if ubicacion:
                                    mensaje += f"\n\n📍 {ubicacion}"
                                if ruta_qr:
                                    mensaje += f"\n\n*A continuación te enviaremos un código QR el cual puedes enseñar al momento de pagar para acceder a un descuento.*"

                                resultado_texto = enviar_mensaje_whatsapp(numero, mensaje)
                                if resultado_texto.get("success"):
                                    print(f"     ✅ Información del lugar enviada exitosamente (texto fallback)")
                                    info_enviada_exitosamente = True
                                else:
                                    print(f"     ❌ Error al enviar información del lugar (imagen y texto fallaron)")
                                    logger.error(f"No se pudo enviar información de {excursion.nombre}")
                        except Exception as e:
                            # Excepción al enviar imagen, intentar texto
                            print(f"     ⚠️ Excepción al enviar imagen: {e}, intentando con texto...")
                            mensaje = f"*{excursion.nombre}*\n\n{descripcion}"
                            if ubicacion:
                                mensaje += f"\n\n📍 {ubicacion}"
                            if ruta_qr:
                                mensaje += f"\n\n*A continuación te enviaremos un código QR el cual puedes enseñar al momento de pagar para acceder a un descuento.*"

                            try:
                                resultado_texto = enviar_mensaje_whatsapp(numero, mensaje)
                                if resultado_texto.get("success"):
                                    print(f"     ✅ Información del lugar enviada exitosamente (texto fallback excepción)")
                                    info_enviada_exitosamente = True
                                else:
                                    print(f"     ❌ Error al enviar información del lugar (texto fallback falló)")
                                    logger.error(f"No se pudo enviar información de {excursion.nombre}: {e}")
                            except Exception as e2:
                                print(f"     ❌ Error crítico al enviar información del lugar: {e2}")
                                logger.error(f"Error crítico al enviar información de {excursion.nombre}: {e2}")
                    else:
                        # Solo texto (sin imagen)
                        mensaje = f"*{excursion.nombre}*\n\n{descripcion}"
                        if ubicacion:
                            mensaje += f"\n\n📍 {ubicacion}"
                        if ruta_qr:
                            mensaje += f"\n\n*A continuación te enviaremos un código QR el cual puedes enseñar al momento de pagar para acceder a un descuento.*"

                        try:
                            resultado_texto = enviar_mensaje_whatsapp(numero, mensaje)
                            if resultado_texto.get("success"):
                                print(f"     ✅ Información del lugar enviada exitosamente (texto)")
                                info_enviada_exitosamente = True
                            else:
                                # Reintentar una vez
                                time.sleep(1)
                                resultado_texto_retry = enviar_mensaje_whatsapp(numero, mensaje)
                                if resultado_texto_retry.get("success"):
                                    print(f"     ✅ Información del lugar enviada exitosamente (texto reintento)")
                                    info_enviada_exitosamente = True
                                else:
                                    print(f"     ❌ Error al enviar información del lugar (texto falló)")
                                    logger.error(f"No se pudo enviar información de {excursion.nombre}")
                        except Exception as e:
                            print(f"     ❌ Excepción al enviar información del lugar: {e}")
                            logger.error(f"Excepción al enviar información de {excursion.nombre}: {e}")

                    # PARTE 2: Solo si la información se envió exitosamente, enviar QR
                    if info_enviada_exitosamente and ruta_qr and os.path.exists(ruta_qr):
                        try:
                            time.sleep(2)  # Pausa para asegurar que la información se procesó
                            caption_qr = f"📱 *Código QR - {excursion.nombre}*\n\nMuestra este QR a la hora de pagar para poder acceder al descuento."
                            print(f"     📱 Enviando QR (información enviada exitosamente): {ruta_qr}")
                            resultado_qr = enviar_imagen_whatsapp(numero, ruta_qr, caption_qr)
                            if resultado_qr.get("success"):
                                print(f"     ✅ QR enviado exitosamente")
                                time.sleep(2)
                            else:
                                error_qr = resultado_qr.get('error', 'Error desconocido')
                                print(f"     ❌ Error al enviar QR: {error_qr}")
                                logger.error(f"Error al enviar QR para {excursion.nombre}: {error_qr}")
                        except Exception as e:
                            print(f"     ❌ Excepción al enviar QR: {e}")
                            logger.error(f"Excepción al enviar QR para {excursion.nombre}: {e}")
                    elif ruta_qr and not info_enviada_exitosamente:
                        print(f"     ⚠️ NO se enviará QR porque la información del lugar no se envió exitosamente")
                    elif ruta_qr and not os.path.exists(ruta_qr):
                        print(f"     ⚠️ QR no existe en ruta: {ruta_qr}")

                    print(f"     ✅ Proceso completado para {excursion.nombre}")
                    
                    # Pausa más larga entre restaurantes para asegurar que todo se procesó completamente
                    # Esto evita que WhatsApp procese mensajes fuera de orden
                    print(f"     ⏳ Esperando antes de enviar el siguiente restaurante...")
                    time.sleep(3)
                    
                except Exception as e:
                    # Error general al procesar la excursión
                    print(f"     ❌ Error general al procesar {excursion.nombre}: {e}")
                    logger.error(f"Error al enviar mensaje de {excursion.nombre}: {e}")
                    import traceback
                    print(f"     Traceback: {traceback.format_exc()}")
                    # Continuar con el siguiente lugar aunque haya error
                    continue
        
        print(f"✅ Finalizado envío de mensajes individuales")
    
    @staticmethod
    def enviar_lugares_seguimiento(chat, numero: str, usuario: Usuario, nuevos_intereses: List[str]):
        """
        Envía lugares directamente sin usar Gemini para el resumen.
        Solo envía lugares de los nuevos intereses que no se hayan enviado antes.
        
        Args:
            numero: Número de teléfono del usuario
            usuario: Usuario para el cual enviar los lugares
            nuevos_intereses: Lista de nuevos intereses agregados en seguimiento
        """
        from whatsapp_api import enviar_imagen_whatsapp, enviar_mensaje_whatsapp
        from Services.UsuarioService import UsuarioService
        import time
        
        if not nuevos_intereses:
            print(f"⚠️ [SEGUIMIENTO] No hay nuevos intereses para enviar")
            return
        
        print(f"📋 [SEGUIMIENTO] Enviando lugares para nuevos intereses: {nuevos_intereses}")
        
        # SOLUCIÓN 3: Usar arreglo simple de lugares enviados en conversation_data
        lugares_ya_enviados = chat.conversation_data.get('lugares_enviados_seguimiento', [])
        print(f"🔍 [SEGUIMIENTO] Lugares ya enviados en seguimiento: {len(lugares_ya_enviados)} lugares")

        # Obtener excursiones para los nuevos intereses
        excursiones = ExcursionService.obtener_excursiones_por_intereses(
            ciudad=usuario.ciudad,
            intereses=nuevos_intereses,
            perfil=usuario.perfil
        )

        # SOLUCIÓN 3: Filtrar lugares ya enviados usando el arreglo simple
        excursiones_filtradas = []
        for exc in excursiones:
            if exc.id not in lugares_ya_enviados:
                excursiones_filtradas.append(exc)
        
        print(f"🔍 [SEGUIMIENTO] Lugares a enviar después de filtrar: {len(excursiones_filtradas)}")
        
        if not excursiones_filtradas:
            mensaje = "Ya te he enviado todos los lugares disponibles para estos intereses. Si querés ver más opciones, podés agregar otros intereses."
            enviar_mensaje_whatsapp(numero, mensaje)
            return
        
        # Limitar a máximo 10 lugares para no sobrecargar
        excursiones_filtradas = excursiones_filtradas[:10]
        
        # Agrupar por categoría (interés)
        excursiones_por_categoria = {}
        for exc in excursiones_filtradas:
            categoria = exc.categoria.lower()
            if categoria not in excursiones_por_categoria:
                excursiones_por_categoria[categoria] = []
            excursiones_por_categoria[categoria].append(exc)
        
        # Emojis por categoría
        emojis_categoria = {
            "restaurantes": "🍽️",
            "comercios": "🛍️",
            "compras": "🛒",
            "cultura": "🎭"
        }
        
        # Enviar lugares directamente sin resumen inicial
        lugares_enviados_ids = []
        for categoria, excursiones_cat in excursiones_por_categoria.items():
            emoji = emojis_categoria.get(categoria, "📍")
            print(f"📤 [SEGUIMIENTO] Procesando categoría: {categoria} ({emoji}) - {len(excursiones_cat)} lugares")
            
            for excursion in excursiones_cat:
                print(f"  → Enviando lugar: {excursion.nombre}")
                try:
                    descripcion = excursion.descripcion if excursion.descripcion else "Sin descripción disponible"
                    ubicacion = excursion.ubicacion if excursion.ubicacion else None
                    
                    # Verificar si es restaurante/comercio y obtener QR
                    ruta_qr = None
                    if debe_enviar_qr(excursion.categoria):
                        try:
                            ruta_qr = obtener_ruta_qr(excursion.id)
                            if ruta_qr and os.path.exists(ruta_qr):
                                print(f"     ✅ QR disponible para {excursion.nombre}")
                        except Exception as e:
                            print(f"     ⚠️ Error al generar QR: {e}")
                            logger.warning(f"No se pudo generar QR para {excursion.nombre}: {e}")
                    
                    # VERIFICACIÓN DE 2 PARTES: Primero enviar información, solo entonces QR
                    descripcion = excursion.descripcion if excursion.descripcion else "Sin descripción disponible"
                    ubicacion = excursion.ubicacion if excursion.ubicacion else None
                    info_enviada_exitosamente = False

                    # PARTE 1: Enviar información del lugar
                    if excursion.imagen_url:
                        # Intentar enviar imagen primero
                        caption = f"*{excursion.nombre}*\n\n{descripcion}"
                        if ubicacion:
                            caption += f"\n\n📍 {ubicacion}"
                        if ruta_qr:
                            caption += f"\n\n*A continuación te enviaremos un código QR el cual puedes enseñar al momento de pagar para acceder a un descuento.*"

                        if len(caption) > 1024:
                            caption = caption[:1021] + "..."

                        try:
                            resultado = enviar_imagen_whatsapp(numero, excursion.imagen_url, caption)
                            if resultado.get("success"):
                                print(f"     ✅ Información del lugar enviada exitosamente (imagen)")
                                info_enviada_exitosamente = True
                            else:
                                # Fallback a texto si falla la imagen
                                print(f"     ⚠️ Error al enviar imagen, intentando con texto...")
                                mensaje = f"*{excursion.nombre}*\n\n{descripcion}"
                                if ubicacion:
                                    mensaje += f"\n\n📍 {ubicacion}"
                                if ruta_qr:
                                    mensaje += f"\n\n*A continuación te enviaremos un código QR el cual puedes enseñar al momento de pagar para acceder a un descuento.*"

                                resultado_texto = enviar_mensaje_whatsapp(numero, mensaje)
                                if resultado_texto.get("success"):
                                    print(f"     ✅ Información del lugar enviada exitosamente (texto fallback)")
                                    info_enviada_exitosamente = True
                                else:
                                    print(f"     ❌ Error al enviar información del lugar (imagen y texto fallaron)")
                                    logger.error(f"No se pudo enviar información de {excursion.nombre}")
                        except Exception as e:
                            # Excepción al enviar imagen, intentar texto
                            print(f"     ⚠️ Excepción al enviar imagen: {e}, intentando con texto...")
                            mensaje = f"*{excursion.nombre}*\n\n{descripcion}"
                            if ubicacion:
                                mensaje += f"\n\n📍 {ubicacion}"
                            if ruta_qr:
                                mensaje += f"\n\n*A continuación te enviaremos un código QR el cual puedes enseñar al momento de pagar para acceder a un descuento.*"

                            try:
                                resultado_texto = enviar_mensaje_whatsapp(numero, mensaje)
                                if resultado_texto.get("success"):
                                    print(f"     ✅ Información del lugar enviada exitosamente (texto fallback excepción)")
                                    info_enviada_exitosamente = True
                                else:
                                    print(f"     ❌ Error al enviar información del lugar (texto fallback falló)")
                                    logger.error(f"No se pudo enviar información de {excursion.nombre}: {e}")
                            except Exception as e2:
                                print(f"     ❌ Error crítico al enviar información del lugar: {e2}")
                                logger.error(f"Error crítico al enviar información de {excursion.nombre}: {e2}")
                    else:
                        # Solo texto (sin imagen)
                        mensaje = f"*{excursion.nombre}*\n\n{descripcion}"
                        if ubicacion:
                            mensaje += f"\n\n📍 {ubicacion}"
                        if ruta_qr:
                            mensaje += f"\n\n*A continuación te enviaremos un código QR el cual puedes enseñar al momento de pagar para acceder a un descuento.*"

                        try:
                            resultado_texto = enviar_mensaje_whatsapp(numero, mensaje)
                            if resultado_texto.get("success"):
                                print(f"     ✅ Información del lugar enviada exitosamente (texto)")
                                info_enviada_exitosamente = True
                            else:
                                # Reintentar una vez
                                time.sleep(1)
                                resultado_texto_retry = enviar_mensaje_whatsapp(numero, mensaje)
                                if resultado_texto_retry.get("success"):
                                    print(f"     ✅ Información del lugar enviada exitosamente (texto reintento)")
                                    info_enviada_exitosamente = True
                                else:
                                    print(f"     ❌ Error al enviar información del lugar (texto falló)")
                                    logger.error(f"No se pudo enviar información de {excursion.nombre}")
                        except Exception as e:
                            print(f"     ❌ Excepción al enviar información del lugar: {e}")
                            logger.error(f"Excepción al enviar información de {excursion.nombre}: {e}")

                    # PARTE 2: Solo si la información se envió exitosamente, enviar QR
                    if info_enviada_exitosamente and ruta_qr and os.path.exists(ruta_qr):
                        try:
                            time.sleep(2)  # Pausa para asegurar que la información se procesó
                            caption_qr = f"📱 *Código QR - {excursion.nombre}*\n\nMuestra este QR a la hora de pagar para poder acceder al descuento."
                            print(f"     📱 Enviando QR (información enviada exitosamente): {ruta_qr}")
                            resultado_qr = enviar_imagen_whatsapp(numero, ruta_qr, caption_qr)
                            if resultado_qr.get("success"):
                                print(f"     ✅ QR enviado exitosamente")
                                time.sleep(2)
                            else:
                                error_qr = resultado_qr.get('error', 'Error desconocido')
                                print(f"     ❌ Error al enviar QR: {error_qr}")
                                logger.error(f"Error al enviar QR para {excursion.nombre}: {error_qr}")
                        except Exception as e:
                            print(f"     ❌ Excepción al enviar QR: {e}")
                            logger.error(f"Excepción al enviar QR para {excursion.nombre}: {e}")
                    elif ruta_qr and not info_enviada_exitosamente:
                        print(f"     ⚠️ NO se enviará QR porque la información del lugar no se envió exitosamente")
                    elif ruta_qr and not os.path.exists(ruta_qr):
                        print(f"     ⚠️ QR no existe en ruta: {ruta_qr}")

                    # SOLUCIÓN 3: Marcar lugar como enviado en el arreglo simple
                    if info_enviada_exitosamente:
                        lugares_enviados_ids.append(excursion.id)
                        # Agregar al arreglo de seguimiento en conversation_data
                        if 'lugares_enviados_seguimiento' not in chat.conversation_data:
                            chat.conversation_data['lugares_enviados_seguimiento'] = []
                        if excursion.id not in chat.conversation_data['lugares_enviados_seguimiento']:
                            chat.conversation_data['lugares_enviados_seguimiento'].append(excursion.id)
                            print(f"✅ [SEGUIMIENTO] Agregado lugar {excursion.id} a seguimiento")

                        # También mantener en el usuario por interés (para compatibilidad)
                        UsuarioService.agregar_lugar_enviado(numero, excursion.id, excursion.categoria.lower())

                    time.sleep(3)
                    
                except Exception as e:
                    print(f"     ❌ Error al procesar {excursion.nombre}: {e}")
                    logger.error(f"Error al enviar lugar {excursion.nombre}: {e}")
                    continue
        
        print(f"✅ [SEGUIMIENTO] Finalizado envío de lugares. Total enviados: {len(lugares_enviados_ids)}")

