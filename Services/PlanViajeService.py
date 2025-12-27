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
    def generar_plan_personalizado(usuario: Usuario) -> PlanViaje:
        """
        Genera un plan de viaje personalizado para un usuario basado en su perfil e intereses.
        """
        if not usuario.ciudad:
            raise ValueError("El usuario debe tener una ciudad asignada")
        
        if not usuario.intereses:
            raise ValueError("El usuario debe tener al menos un interés seleccionado")
        
        # Obtener excursiones filtradas por intereses y perfil
        excursiones = ExcursionService.obtener_excursiones_por_intereses(
            ciudad=usuario.ciudad,
            intereses=usuario.intereses,
            perfil=usuario.perfil
        )
        
        # Verificar que cada interés tenga al menos una excursión
        ids_existentes = {exc.id for exc in excursiones}
        excursiones_por_interes = {}
        for interes in usuario.intereses:
            excursiones_por_interes[interes] = [e for e in excursiones if e.categoria.lower() == interes.lower()]
        
        # Completar intereses faltantes
        for interes in usuario.intereses:
            if not excursiones_por_interes.get(interes):
                # Buscar al menos una excursión de este interés
                excursiones_interes = ExcursionService.obtener_excursiones_por_categoria(usuario.ciudad, interes)
                if excursiones_interes:
                    # Agregar la primera que no esté ya en la lista
                    for exc in excursiones_interes:
                        if exc.id not in ids_existentes:
                            excursiones.append(exc)
                            ids_existentes.add(exc.id)
                            break
        
        # Limitar a máximo 15 excursiones para no sobrecargar
        excursiones = excursiones[:15]
        
        # Si no hay suficientes, agregar más sin filtrar por perfil
        if len(excursiones) < 5:
            todas_las_excursiones = ExcursionService.obtener_excursiones_por_ciudad(usuario.ciudad)
            categorias_interes = [interes.lower() for interes in usuario.intereses]
            excursiones_adicionales = [
                exc for exc in todas_las_excursiones
                if exc.categoria.lower() in categorias_interes or any(
                    cat in exc.categoria.lower() for cat in categorias_interes
                )
            ]
            # Agregar sin duplicar
            for exc in excursiones_adicionales:
                if exc.id not in ids_existentes and len(excursiones) < 15:
                    excursiones.append(exc)
                    ids_existentes.add(exc.id)
        
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
            "recreacion": "🌳",
            "cultura": "🏛️",
            "compras": "🛒"
        }
        
        # Nombres de categoría en español
        nombres_categoria = {
            "restaurantes": "Restaurantes",
            "comercios": "Comercios",
            "recreacion": "Zonas de Recreación",
            "cultura": "Cultura y Paseos",
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
                "recreacion": "🌳",
                "cultura": "🏛️",
                "compras": "🛒"
            }
            
            nombres_categoria = {
                "restaurantes": "Restaurantes",
                "comercios": "Comercios",
                "recreacion": "Recreación",
                "cultura": "Cultura",
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
        # Agrupar excursiones por categoría (interés)
        excursiones_por_categoria = plan.obtener_excursiones_por_categoria()
        
        print(f"📋 Iniciando envío de mensajes individuales. Total de categorías: {len(excursiones_por_categoria)}")
        print(f"📋 Excursiones en el plan: {len(plan.excursiones)}")
        
        # Emojis por categoría
        emojis_categoria = {
            "restaurantes": "🍽️",
            "comercios": "🛍️",
            "recreacion": "🌳",
            "cultura": "🏛️",
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
                    
                    if excursion.imagen_url:
                        # Enviar imagen del lugar con caption
                        caption = f"*{excursion.nombre}*\n\n{descripcion}"
                        if ubicacion:
                            caption += f"\n\n📍 {ubicacion}"
                        
                        # Si hay QR, agregarlo al caption
                        if ruta_qr:
                            caption += f"\n\n📱 Escanea el código QR para obtener un descuento del 5%"
                        
                        # Limitar caption a 1024 caracteres (límite de WhatsApp)
                        if len(caption) > 1024:
                            caption = caption[:1021] + "..."
                        
                        try:
                            print(f"     📷 Enviando imagen del lugar: {excursion.imagen_url[:50]}...")
                            resultado = enviar_imagen_whatsapp(numero, excursion.imagen_url, caption)
                            if resultado.get("success"):
                                print(f"     ✅ Imagen enviada exitosamente")
                                
                                # Si hay QR, enviarlo en un mensaje separado después de una pausa
                                if ruta_qr:
                                    try:
                                        # Pausa para evitar problemas con WhatsApp
                                        time.sleep(2)
                                        caption_qr = f"📱 *Código QR - {excursion.nombre}*\n\nEscanea este código para obtener un descuento del 5%"
                                        print(f"     📱 Enviando QR en mensaje separado: {ruta_qr}")
                                        print(f"     📱 Verificando que el archivo existe: {os.path.exists(ruta_qr)}")
                                        resultado_qr = enviar_imagen_whatsapp(numero, ruta_qr, caption_qr)
                                        if resultado_qr.get("success"):
                                            print(f"     ✅ QR enviado exitosamente en mensaje separado")
                                        else:
                                            error_qr = resultado_qr.get('error', 'Error desconocido')
                                            print(f"     ❌ Error al enviar QR: {error_qr}")
                                            logger.error(f"Error al enviar QR para {excursion.nombre}: {error_qr}")
                                    except Exception as e:
                                        print(f"     ❌ Excepción al enviar QR: {e}")
                                        import traceback
                                        print(f"     Traceback: {traceback.format_exc()}")
                                        logger.error(f"Excepción al enviar QR para {excursion.nombre}: {e}")
                            else:
                                # Si falla la imagen, enviar solo texto
                                error_msg = resultado.get('error', 'Error desconocido')
                                print(f"     ❌ Error al enviar imagen: {error_msg}")
                                logger.warning(f"No se pudo enviar imagen de {excursion.nombre}: {error_msg}")
                                mensaje = f"*{excursion.nombre}*\n\n{descripcion}"
                                if ubicacion:
                                    mensaje += f"\n\n📍 {ubicacion}"
                                if ruta_qr:
                                    mensaje += f"\n\n📱 Escanea el código QR para obtener un descuento del 5%"
                                enviar_mensaje_whatsapp(numero, mensaje)
                                
                                # Enviar QR después del texto en mensaje separado
                                if ruta_qr:
                                    try:
                                        time.sleep(2)
                                        caption_qr = f"📱 *Código QR - {excursion.nombre}*\n\nEscanea este código para obtener un descuento del 5%"
                                        print(f"     📱 Enviando QR después del texto: {ruta_qr}")
                                        resultado_qr = enviar_imagen_whatsapp(numero, ruta_qr, caption_qr)
                                        if resultado_qr.get("success"):
                                            print(f"     ✅ QR enviado exitosamente")
                                        else:
                                            print(f"     ❌ Error al enviar QR: {resultado_qr.get('error')}")
                                    except Exception as e:
                                        print(f"     ❌ Error al enviar QR: {e}")
                                        import traceback
                                        traceback.print_exc()
                                print(f"     📝 Mensaje de texto enviado como fallback")
                        except Exception as e:
                            # Error al enviar imagen
                            print(f"     ❌ Excepción al enviar imagen: {e}")
                            logger.warning(f"No se pudo enviar imagen de {excursion.nombre}: {e}")
                            mensaje = f"*{excursion.nombre}*\n\n{descripcion}"
                            if ubicacion:
                                mensaje += f"\n\n📍 {ubicacion}"
                            if ruta_qr:
                                mensaje += f"\n\n📱 Escanea el código QR para obtener un descuento del 5%"
                            enviar_mensaje_whatsapp(numero, mensaje)
                            
                            # Enviar QR después del texto
                            if ruta_qr:
                                try:
                                    caption_qr = f"📱 Código QR - Descuento 5%"
                                    enviar_imagen_whatsapp(numero, ruta_qr, caption_qr)
                                except:
                                    pass
                            print(f"     📝 Mensaje de texto enviado como fallback")
                    else:
                        # Enviar solo texto (sin imagen del lugar)
                        print(f"     📝 Enviando mensaje de texto (sin imagen)")
                        mensaje = f"*{excursion.nombre}*\n\n{descripcion}"
                        if ubicacion:
                            mensaje += f"\n\n📍 {ubicacion}"
                        if ruta_qr:
                            mensaje += f"\n\n📱 Escanea el código QR para obtener un descuento del 5%"
                        enviar_mensaje_whatsapp(numero, mensaje)
                        
                        # Enviar QR después del texto en mensaje separado
                        if ruta_qr:
                            try:
                                time.sleep(2)
                                caption_qr = f"📱 *Código QR - {excursion.nombre}*\n\nEscanea este código para obtener un descuento del 5%"
                                print(f"     📱 Enviando QR después del texto: {ruta_qr}")
                                print(f"     📱 Verificando que el archivo existe: {os.path.exists(ruta_qr)}")
                                resultado_qr = enviar_imagen_whatsapp(numero, ruta_qr, caption_qr)
                                if resultado_qr.get("success"):
                                    print(f"     ✅ QR enviado exitosamente en mensaje separado")
                                else:
                                    error_qr = resultado_qr.get('error', 'Error desconocido')
                                    print(f"     ❌ Error al enviar QR: {error_qr}")
                                    logger.error(f"Error al enviar QR para {excursion.nombre}: {error_qr}")
                            except Exception as e:
                                print(f"     ❌ Excepción al enviar QR: {e}")
                                import traceback
                                print(f"     Traceback: {traceback.format_exc()}")
                                logger.error(f"Excepción al enviar QR para {excursion.nombre}: {e}")
                        print(f"     ✅ Mensaje de texto enviado")
                    
                    # Pausa entre mensajes para mejor UX
                    time.sleep(1.5)
                    
                except Exception as e:
                    # Error general al procesar la excursión
                    print(f"     ❌ Error general al procesar {excursion.nombre}: {e}")
                    logger.error(f"Error al enviar mensaje de {excursion.nombre}: {e}")
                    import traceback
                    print(f"     Traceback: {traceback.format_exc()}")
                    # Continuar con el siguiente lugar aunque haya error
                    continue
        
        print(f"✅ Finalizado envío de mensajes individuales")

