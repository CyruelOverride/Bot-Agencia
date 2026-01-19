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
    def _sanitizar_ruta_qr(ruta_qr: str, excursion: Excursion) -> Optional[str]:
        """
        Sanitiza la ruta del QR para manejar acentos y caracteres especiales.
        Busca el archivo tanto con acento como sin él.
        
        Args:
            ruta_qr: Ruta original del archivo QR
            excursion: Excursión para obtener información adicional si es necesario
        
        Returns:
            Ruta sanitizada que existe en el sistema, o None si no se encuentra
        """
        if not ruta_qr:
            return None
        
        # Si la ruta existe tal cual, retornarla
        if os.path.exists(ruta_qr):
            return ruta_qr
        
        # Si no existe, intentar variaciones sin acentos
        # Obtener directorio y nombre del archivo
        directorio = os.path.dirname(ruta_qr)
        nombre_archivo = os.path.basename(ruta_qr)
        
        # Crear variaciones del nombre sin acentos
        nombre_sin_acentos = nombre_archivo
        # Reemplazar acentos comunes
        reemplazos = {
            'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
            'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U',
            'ñ': 'n', 'Ñ': 'N'
        }
        for acento, sin_acento in reemplazos.items():
            nombre_sin_acentos = nombre_sin_acentos.replace(acento, sin_acento)
        
        # Intentar con nombre sin acentos
        if nombre_sin_acentos != nombre_archivo:
            ruta_sin_acentos = os.path.join(directorio, nombre_sin_acentos)
            if os.path.exists(ruta_sin_acentos):
                print(f"     🔄 QR encontrado con nombre sin acentos: {ruta_sin_acentos}")
                return ruta_sin_acentos
        
        # Si aún no existe, intentar buscar por ID de excursión (más robusto)
        # El QR generalmente se genera con el ID, no con el nombre
        if excursion and excursion.id:
            # Buscar archivo con patrón: {excursion_id}.png
            posibles_nombres = [
                f"{excursion.id}.png",
                f"{excursion.id}.jpg",
                f"{excursion.id}.jpeg"
            ]
            for nombre_posible in posibles_nombres:
                ruta_posible = os.path.join(directorio, nombre_posible)
                if os.path.exists(ruta_posible):
                    print(f"     🔄 QR encontrado por ID: {ruta_posible}")
                    return ruta_posible
        
        # Si no se encuentra ninguna variación, retornar None
        print(f"     ⚠️ No se encontró QR en ninguna variación para: {ruta_qr}")
        return None
    
    @staticmethod
    def _enviar_con_reintento(numero: str, excursion: Excursion) -> dict:
        """
        Envía la información del lugar con reintentos.
        Retorna un diccionario con 'success' y 'error' si aplica.
        """
        from whatsapp_api import enviar_imagen_whatsapp, enviar_mensaje_whatsapp
        from datetime import datetime
        import time
        
        descripcion = excursion.descripcion if excursion.descripcion else "Sin descripción disponible"
        ubicacion = excursion.ubicacion if excursion.ubicacion else None
        pagina_web = excursion.pagina_web if hasattr(excursion, 'pagina_web') and excursion.pagina_web else None
        
        # Intentar enviar imágenes primero
        imagenes_disponibles = excursion.imagenes_url if hasattr(excursion, 'imagenes_url') and excursion.imagenes_url else []
        if not imagenes_disponibles and excursion.imagen_url:
            # Compatibilidad hacia atrás: usar imagen_url si imagenes_url no está disponible
            imagenes_disponibles = [excursion.imagen_url]
        
        if imagenes_disponibles:
            import time
            # Construir caption completo para la primera imagen
            caption = f"*{excursion.nombre}*\n\n{descripcion}"
            if ubicacion:
                caption += f"\n\n📍 {ubicacion}"
            if pagina_web:
                caption += f"\n\n🌐 {pagina_web}"
            
            if len(caption) > 1024:
                caption = caption[:1021] + "..."
            
            try:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"🚀 [PASO 1] Enviando INFO ({len(imagenes_disponibles)} imagen/es) para: {excursion.nombre} - {timestamp}")
                
                # Enviar todas las imágenes
                resultado = None
                for idx, imagen_url in enumerate(imagenes_disponibles):
                    # Primera imagen lleva el caption completo, las demás solo el nombre
                    caption_imagen = caption if idx == 0 else f"*{excursion.nombre}*"
                    
                    resultado_imagen = enviar_imagen_whatsapp(numero, imagen_url, caption_imagen)
                    
                    # El resultado de la primera imagen es el que cuenta para validación
                    if idx == 0:
                        resultado = resultado_imagen
                    
                    # Delay eliminado - enviar imágenes sin delay
                
                if resultado and resultado.get("success"):
                    timestamp_result = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f"✅ [PASO 1] ÉXITO - {timestamp_result} - Lugar: {excursion.nombre} (ID: {excursion.id})")
                    return {"success": True}
                else:
                    # Fallback a texto
                    print(f"⚠️ [PASO 1] Imagen falló, intentando texto...")
            except Exception as e:
                print(f"⚠️ [PASO 1] Excepción con imagen: {e}, intentando texto...")
        
        # Fallback a texto
        mensaje = f"*{excursion.nombre}*\n\n{descripcion}"
        if ubicacion:
            mensaje += f"\n\n📍 {ubicacion}"
        if pagina_web:
            mensaje += f"\n\n🌐 {pagina_web}"
        
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"🚀 [PASO 1] Enviando INFO (texto) para: {excursion.nombre} - {timestamp}")
            resultado_texto = enviar_mensaje_whatsapp(numero, mensaje)
            if resultado_texto.get("success"):
                timestamp_result = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"✅ [PASO 1] ÉXITO - {timestamp_result} - Lugar: {excursion.nombre} (ID: {excursion.id})")
                return {"success": True}
            else:
                # Reintentar una vez
                time.sleep(1)
                print(f"🔄 [PASO 1] Reintentando envío de texto...")
                resultado_retry = enviar_mensaje_whatsapp(numero, mensaje)
                if resultado_retry.get("success"):
                    timestamp_retry = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f"✅ [PASO 1] ÉXITO REINTENTO - {timestamp_retry} - Lugar: {excursion.nombre} (ID: {excursion.id})")
                    return {"success": True}
                else:
                    timestamp_retry = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    error_msg = resultado_retry.get('error', 'Error desconocido')
                    print(f"❌ [PASO 1] FALLO REINTENTO - {timestamp_retry} - Lugar: {excursion.nombre} - Error: {error_msg}")
                    return {"success": False, "error": error_msg}
        except Exception as e:
            timestamp_exception = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"❌ [PASO 1] EXCEPCIÓN - {timestamp_exception} - Lugar: {excursion.nombre} - Error: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def _enviar_informacion_y_qr(numero: str, excursion: Excursion, ruta_qr: Optional[str] = None) -> bool:
        """
        ENVÍO ATÓMICO: El QR depende 100% del éxito del mensaje anterior.
        CANDADO DE SEGURIDAD: Si la información no se envía exitosamente, el QR se cancela automáticamente.
        
        Args:
            numero: Número de teléfono del usuario
            excursion: Excursión a enviar
            ruta_qr: Ruta opcional al archivo QR (si no se proporciona, se intenta generar)
        
        Returns:
            bool: True si la información se envió exitosamente, False en caso contrario
        """
        from whatsapp_api import enviar_imagen_whatsapp, enviar_mensaje_whatsapp
        from datetime import datetime
        import os
        
        # LOG DETALLADO: Inicio de envío
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n{'='*80}")
        print(f"📤 [LOG ENVÍO] INICIO - {timestamp}")
        print(f"📤 [LOG ENVÍO] Lugar ID: {excursion.id}")
        print(f"📤 [LOG ENVÍO] Lugar Nombre: {excursion.nombre}")
        print(f"📤 [LOG ENVÍO] Categoría: {excursion.categoria}")
        print(f"📤 [LOG ENVÍO] Tiene QR: {ruta_qr is not None}")
        print(f"{'='*80}\n")
        
        # 1. Intentar enviar la información (Imagen con caption o Texto)
        # NUEVA ESTRATEGIA: Las imágenes ahora se descargan y suben a WhatsApp Media API
        # Esto las hace más confiables que usar URLs externas directamente
        descripcion = excursion.descripcion if excursion.descripcion else "Sin descripción disponible"
        ubicacion = excursion.ubicacion if excursion.ubicacion else None
        pagina_web = excursion.pagina_web if hasattr(excursion, 'pagina_web') and excursion.pagina_web else None
        
        # Construir caption/mensaje
        imagenes_disponibles = excursion.imagenes_url if hasattr(excursion, 'imagenes_url') and excursion.imagenes_url else []
        if not imagenes_disponibles and excursion.imagen_url:
            # Compatibilidad hacia atrás: usar imagen_url si imagenes_url no está disponible
            imagenes_disponibles = [excursion.imagen_url]
        
        if imagenes_disponibles:
            import time
            # Construir caption completo para la primera imagen
            caption = f"*{excursion.nombre}*\n\n{descripcion}"
            if ubicacion:
                caption += f"\n\n📍 {ubicacion}"
            if pagina_web:
                caption += f"\n\n🌐 {pagina_web}"
            
            if len(caption) > 1024:
                caption = caption[:1021] + "..."
            
            print(f"🚀 [PASO 1] Enviando Info de {excursion.nombre} ({len(imagenes_disponibles)} imagen/es - descargada y subida a WhatsApp)...")
            print(f"📝 [PASO 1] CONTENIDO A ENVIAR:")
            print(f"   Nombre: {excursion.nombre}")
            print(f"   Descripción: {descripcion[:100]}..." if len(descripcion) > 100 else f"   Descripción: {descripcion}")
            print(f"   Ubicación: {ubicacion}" if ubicacion else "   Ubicación: No disponible")
            print(f"   Total de imágenes: {len(imagenes_disponibles)}")
            
            # Enviar todas las imágenes
            resultado_info = None
            for idx, imagen_url in enumerate(imagenes_disponibles):
                # Primera imagen lleva el caption completo, las demás solo el nombre
                caption_imagen = caption if idx == 0 else f"*{excursion.nombre}*"
                
                print(f"   📷 Enviando imagen {idx + 1}/{len(imagenes_disponibles)}: {imagen_url[:80]}..." if len(imagen_url) > 80 else f"   📷 Enviando imagen {idx + 1}/{len(imagenes_disponibles)}: {imagen_url}")
                
                resultado_imagen = enviar_imagen_whatsapp(numero, imagen_url, caption_imagen)
                
                # El resultado de la primera imagen es el que cuenta para validación
                if idx == 0:
                    resultado_info = resultado_imagen
                    print(f"📊 [PASO 1] RESULTADO (primera imagen): success={resultado_info.get('success', False)}, message_id={resultado_info.get('message_id', 'N/A')}, error={resultado_info.get('error', 'N/A')}")
                else:
                    # Para imágenes adicionales, solo loguear el resultado
                    if resultado_imagen.get('success'):
                        print(f"✅ [PASO 1] Imagen {idx + 1} enviada exitosamente")
                    else:
                        print(f"⚠️ [PASO 1] Imagen {idx + 1} falló: {resultado_imagen.get('error', 'N/A')}")
                
                # Delay mínimo eliminado - enviar imágenes sin delay para mayor velocidad
        else:
            # Sin imagen, enviar texto directamente
            mensaje = f"*{excursion.nombre}*\n\n{descripcion}"
            if ubicacion:
                mensaje += f"\n\n📍 {ubicacion}"
            if pagina_web:
                mensaje += f"\n\n🌐 {pagina_web}"
            
            print(f"🚀 [PASO 1] Enviando Info de {excursion.nombre} (texto)...")
            print(f"📝 [PASO 1] CONTENIDO A ENVIAR:")
            print(f"   Nombre: {excursion.nombre}")
            print(f"   Descripción: {descripcion[:100]}..." if len(descripcion) > 100 else f"   Descripción: {descripcion}")
            print(f"   Ubicación: {ubicacion}" if ubicacion else "   Ubicación: No disponible")
            print(f"   Mensaje completo ({len(mensaje)} chars): {mensaje[:200]}..." if len(mensaje) > 200 else f"   Mensaje completo: {mensaje}")
            resultado_info = enviar_mensaje_whatsapp(numero, mensaje)
            print(f"📊 [PASO 1] RESULTADO: success={resultado_info.get('success', False)}, error={resultado_info.get('error', 'N/A')}")
        
        # 2. VALIDACIÓN CRÍTICA: ¿WhatsApp nos dio un OK (Status 200)?
        info_enviada_exitosamente = resultado_info.get("success", False)
        message_id_valido = resultado_info.get("message_id") is not None and resultado_info.get("message_id") != "N/A"
        
        # Para imágenes, requerimos message_id válido (ahora más confiable porque se suben a WhatsApp)
        imagenes_disponibles_check = excursion.imagenes_url if hasattr(excursion, 'imagenes_url') and excursion.imagenes_url else []
        if not imagenes_disponibles_check and excursion.imagen_url:
            imagenes_disponibles_check = [excursion.imagen_url]
        
        if imagenes_disponibles_check:
            if not info_enviada_exitosamente or not message_id_valido:
                print(f"⚠️ [ADVERTENCIA] Imagen falló o sin message_id válido para {excursion.nombre}.")
                print(f"⚠️ [ADVERTENCIA] success={info_enviada_exitosamente}, message_id={resultado_info.get('message_id', 'N/A')}")
                print(f"⚠️ [ADVERTENCIA] Intentando fallback de texto...")
                info_enviada_exitosamente = False  # Forzar fallback
        
        print(f"✅ [PASO 1] VALIDACIÓN: info_enviada_exitosamente = {info_enviada_exitosamente}, message_id_válido = {message_id_valido}")
        
        # 3. SALVAVIDAS: Si la imagen falló, intentamos TEXTO SOLO
        if not info_enviada_exitosamente:
            print(f"⚠️ [SALVAVIDAS] Imagen falló para {excursion.nombre}. Intentando enviar solo TEXTO como respaldo...")
            mensaje_fallback = f"*{excursion.nombre}*\n\n{descripcion}"
            if ubicacion:
                mensaje_fallback += f"\n\n📍 {ubicacion}"
            
            print(f"📝 [SALVAVIDAS] CONTENIDO FALLBACK A ENVIAR:")
            print(f"   Mensaje fallback completo ({len(mensaje_fallback)} chars): {mensaje_fallback[:200]}..." if len(mensaje_fallback) > 200 else f"   Mensaje fallback completo: {mensaje_fallback}")
            resultado_fallback = enviar_mensaje_whatsapp(numero, mensaje_fallback)
            print(f"📊 [SALVAVIDAS] RESULTADO: success={resultado_fallback.get('success', False)}, error={resultado_fallback.get('error', 'N/A')}")
            # Para texto, verificamos success (puede que no haya message_id en la respuesta de texto)
            info_enviada_exitosamente = resultado_fallback.get("success", False)
            print(f"✅ [SALVAVIDAS] VALIDACIÓN: info_enviada_exitosamente = {info_enviada_exitosamente}")
        
        # 4. EL CANDADO: Si después de intentar Imagen y luego Texto NADA salió...
        if not info_enviada_exitosamente:
            print(f"❌ [BLOQUEO TOTAL] No se pudo enviar nada de {excursion.nombre} (ID: {excursion.id}). CANCELANDO QR.")
            timestamp_fin = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"📤 [LOG ENVÍO] FIN - {timestamp_fin} - Lugar ID: {excursion.id} - Información enviada: False")
            print(f"{'='*80}\n")
            return False  # AQUÍ SE CORTA TODO. No llega al sleep ni al QR.
        
        # 5. SOLO SI LLEGAMOS AQUÍ, procedemos con el QR
        if ruta_qr and os.path.exists(ruta_qr):
            print(f"✅ [CONFIRMACIÓN] Info confirmada. Enviando QR de {excursion.nombre}...")
            
            # Sanitizar ruta del QR
            ruta_qr_sanitizada = PlanViajeService._sanitizar_ruta_qr(ruta_qr, excursion)
            
            if ruta_qr_sanitizada and os.path.exists(ruta_qr_sanitizada):
                caption_qr = f"📱 *Código QR - {excursion.nombre}*\n\nMuestra este QR a la hora de pagar para poder acceder al descuento."
                
                timestamp_qr = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"🎯 [PASO 2] Enviando QR para: {excursion.nombre} (ID: {excursion.id}) - {timestamp_qr}")
                print(f"🎯 [PASO 2] Ruta QR: {ruta_qr_sanitizada}")
                
                resultado_qr = enviar_imagen_whatsapp(numero, ruta_qr_sanitizada, caption_qr)
                if resultado_qr.get("success"):
                    timestamp_qr_result = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f"✅ [PASO 2] ÉXITO - {timestamp_qr_result} - QR enviado para: {excursion.nombre} (ID: {excursion.id})")
                else:
                    timestamp_qr_result = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    error_qr = resultado_qr.get('error', 'Error desconocido')
                    print(f"⚠️ [AVISO] Error al enviar QR de {excursion.nombre} (ID: {excursion.id}), pero la info ya se envió. Error: {error_qr}")
                    logger.warning(f"Error al enviar QR para {excursion.nombre} (información ya enviada): {error_qr}")
            else:
                print(f"⚠️ [AVISO] QR no existe en ruta sanitizada: {ruta_qr_sanitizada}")
                logger.warning(f"QR no existe para {excursion.nombre} en ruta: {ruta_qr_sanitizada}")
        elif ruta_qr and not os.path.exists(ruta_qr):
            print(f"⚠️ [AVISO] QR no existe en ruta: {ruta_qr}")
        
        # LOG DETALLADO: Fin de envío
        timestamp_fin = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"📤 [LOG ENVÍO] FIN - {timestamp_fin}")
        print(f"📤 [LOG ENVÍO] Lugar ID: {excursion.id}")
        print(f"📤 [LOG ENVÍO] Lugar Nombre: {excursion.nombre}")
        print(f"📤 [LOG ENVÍO] Información enviada: {info_enviada_exitosamente}")
        print(f"📤 [LOG ENVÍO] QR enviado: {info_enviada_exitosamente and ruta_qr is not None and os.path.exists(ruta_qr) if ruta_qr else False}")
        print(f"{'='*80}\n")
        
        return info_enviada_exitosamente
    
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
        # BLINDAJE 1: Normalizar IDs a string para comparación consistente
        if lugares_excluidos:
            lugares_excluidos_normalizados = [str(lugar_id) for lugar_id in lugares_excluidos]
            excursiones = [exc for exc in excursiones if str(exc.id) not in lugares_excluidos_normalizados]
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
                    # BLINDAJE 1: Normalizar IDs para comparación consistente
                    lugares_excluidos_normalizados_aux = [str(lugar_id) for lugar_id in lugares_excluidos] if lugares_excluidos else []
                    for exc in excursiones_interes:
                        if exc.id not in ids_existentes and str(exc.id) not in lugares_excluidos_normalizados_aux:
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
            # BLINDAJE 1: Normalizar IDs para comparación consistente
            lugares_excluidos_normalizados_aux2 = [str(lugar_id) for lugar_id in lugares_excluidos] if lugares_excluidos else []
            for exc in excursiones_adicionales:
                if exc.id not in ids_existentes and str(exc.id) not in lugares_excluidos_normalizados_aux2 and len(excursiones) < 15:
                    # VERIFICAR que la categoría coincida con algún interés del usuario
                    if exc.categoria.lower() in categorias_interes:
                        excursiones.append(exc)
                        ids_existentes.add(exc.id)
                        print(f"🔍 [GENERAR_PLAN] Agregada excursión adicional: {exc.nombre} (ID: {exc.id}, Categoría: {exc.categoria})")
        
        # Filtrar excursiones: solo incluir las que tienen al menos una imagen
        excursiones_filtradas = []
        for exc in excursiones:
            imagenes_disponibles = exc.imagenes_url if hasattr(exc, 'imagenes_url') and exc.imagenes_url else []
            if not imagenes_disponibles and exc.imagen_url:
                imagenes_disponibles = [exc.imagen_url]
            if imagenes_disponibles:
                excursiones_filtradas.append(exc)
        excursiones = excursiones_filtradas
        
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
    def enviar_plan_con_imagen(numero: str, plan: PlanViaje, ruta_imagen: Optional[str] = None, chat=None):
        """
        Envía el plan con un mensaje individual por cada lugar.
        Primero envía imagen con resumen, luego cada excursión en mensajes separados con su imagen.
        
        Args:
            numero: Número de teléfono del usuario
            plan: Plan de viaje a enviar
            ruta_imagen: Ruta opcional a la imagen del resumen. Si no se proporciona, busca automáticamente
            chat: Objeto Chat opcional para actualizar lugares_enviados_seguimiento en conversation_data
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
        from datetime import datetime
        
        if imagen_a_enviar:
            try:
                # Caption con resumen corto (500-700 chars recomendado, usamos 700 como máximo seguro)
                caption = f"🎯 Tu Plan Personalizado para {plan.ciudad}\n\n{plan.resumen_ia[:700]}"
                
                # LOG DETALLADO: Resumen del plan
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"\n{'='*80}")
                print(f"📤 [LOG PLAN] ENVIANDO RESUMEN DEL PLAN (IMAGEN) - {timestamp}")
                print(f"📤 [LOG PLAN] Ciudad: {plan.ciudad}")
                print(f"📤 [LOG PLAN] Imagen URL: {imagen_a_enviar}")
                print(f"📤 [LOG PLAN] Contenido del mensaje:")
                print(f"{'─'*80}")
                print(caption)
                print(f"{'─'*80}")
                print(f"{'='*80}\n")
                
                resultado = enviar_imagen_whatsapp(numero, imagen_a_enviar, caption)
                
                if resultado.get("success"):
                    timestamp_result = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f"✅ [LOG PLAN] ÉXITO - {timestamp_result} - Ciudad: {plan.ciudad}")
                    # Pausa para mejor UX
                    time.sleep(2)
                else:
                    timestamp_result = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    error_msg = resultado.get('error', 'Error desconocido')
                    print(f"❌ [LOG PLAN] FALLO - {timestamp_result} - Ciudad: {plan.ciudad} - Error: {error_msg}")
                    logger.warning(f"No se pudo enviar imagen del plan: {error_msg}")
                    # Si falla la imagen, enviar resumen como texto
                    mensaje_resumen = f"🎯 *Tu Plan Personalizado para {plan.ciudad}*\n\n{plan.resumen_ia[:700]}"
                    
                    # LOG DETALLADO: Resumen del plan (texto fallback)
                    timestamp_fallback = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f"\n{'='*80}")
                    print(f"📤 [LOG PLAN] ENVIANDO RESUMEN DEL PLAN (TEXTO FALLBACK) - {timestamp_fallback}")
                    print(f"📤 [LOG PLAN] Ciudad: {plan.ciudad}")
                    print(f"📤 [LOG PLAN] Contenido del mensaje:")
                    print(f"{'─'*80}")
                    print(mensaje_resumen)
                    print(f"{'─'*80}")
                    print(f"{'='*80}\n")
                    
                    resultado_fallback = enviar_mensaje_whatsapp(numero, mensaje_resumen)
                    if resultado_fallback.get("success"):
                        timestamp_fallback_result = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        print(f"✅ [LOG PLAN] ÉXITO FALLBACK - {timestamp_fallback_result} - Ciudad: {plan.ciudad}")
                    else:
                        timestamp_fallback_result = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        print(f"❌ [LOG PLAN] FALLO FALLBACK - {timestamp_fallback_result} - Ciudad: {plan.ciudad} - Error: {resultado_fallback.get('error', 'Desconocido')}")
                    time.sleep(1)
                    
            except Exception as e:
                # Error silencioso: enviar resumen como texto
                timestamp_exception = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"❌ [LOG PLAN] EXCEPCIÓN - {timestamp_exception} - Ciudad: {plan.ciudad} - Error: {e}")
                logger.warning(f"No se pudo enviar imagen del plan: {e}")
                mensaje_resumen = f"🎯 *Tu Plan Personalizado para {plan.ciudad}*\n\n{plan.resumen_ia[:700]}"
                
                # LOG DETALLADO: Resumen del plan (texto excepción)
                print(f"\n{'='*80}")
                print(f"📤 [LOG PLAN] ENVIANDO RESUMEN DEL PLAN (TEXTO EXCEPCIÓN) - {timestamp_exception}")
                print(f"📤 [LOG PLAN] Ciudad: {plan.ciudad}")
                print(f"📤 [LOG PLAN] Contenido del mensaje:")
                print(f"{'─'*80}")
                print(mensaje_resumen)
                print(f"{'─'*80}")
                print(f"{'='*80}\n")
                
                resultado_exception = enviar_mensaje_whatsapp(numero, mensaje_resumen)
                if resultado_exception.get("success"):
                    timestamp_exception_result = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f"✅ [LOG PLAN] ÉXITO EXCEPCIÓN - {timestamp_exception_result} - Ciudad: {plan.ciudad}")
                else:
                    timestamp_exception_result = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f"❌ [LOG PLAN] FALLO EXCEPCIÓN - {timestamp_exception_result} - Ciudad: {plan.ciudad} - Error: {resultado_exception.get('error', 'Desconocido')}")
                time.sleep(1)
        else:
            # Si no hay imagen, enviar resumen como texto
            mensaje_resumen = f"🎯 *Tu Plan Personalizado para {plan.ciudad}*\n\n{plan.resumen_ia[:700]}"
            
            # LOG DETALLADO: Resumen del plan (texto)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"\n{'='*80}")
            print(f"📤 [LOG PLAN] ENVIANDO RESUMEN DEL PLAN (TEXTO) - {timestamp}")
            print(f"📤 [LOG PLAN] Ciudad: {plan.ciudad}")
            print(f"📤 [LOG PLAN] Contenido del mensaje:")
            print(f"{'─'*80}")
            print(mensaje_resumen)
            print(f"{'─'*80}")
            print(f"{'='*80}\n")
            
            resultado_texto = enviar_mensaje_whatsapp(numero, mensaje_resumen)
            if resultado_texto.get("success"):
                timestamp_result = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"✅ [LOG PLAN] ÉXITO - {timestamp_result} - Ciudad: {plan.ciudad}")
            else:
                timestamp_result = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"❌ [LOG PLAN] FALLO - {timestamp_result} - Ciudad: {plan.ciudad} - Error: {resultado_texto.get('error', 'Desconocido')}")
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
                imagenes_check = excursion.imagenes_url if hasattr(excursion, 'imagenes_url') and excursion.imagenes_url else []
                if not imagenes_check and excursion.imagen_url:
                    imagenes_check = [excursion.imagen_url]
                print(f"     - Tiene imagen/es: {len(imagenes_check)} imagen/es")
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
                    
                    # Usar función centralizada con verificación de 2 partes
                    info_enviada_exitosamente = PlanViajeService._enviar_informacion_y_qr(numero, excursion, ruta_qr)

                    # BLINDAJE 3: Verificación de persistencia inmediata
                    if info_enviada_exitosamente:
                        # CRÍTICO: Guardar en UsuarioService PRIMERO (persistencia principal)
                        UsuarioService.agregar_lugar_enviado(numero, excursion.id, excursion.categoria.lower())
                        # Asegurar que el usuario se actualice en memoria
                        usuario_actualizado = UsuarioService.obtener_usuario_por_telefono(numero)
                        if usuario_actualizado:
                            UsuarioService.actualizar_usuario(usuario_actualizado)
                            print(f"✅ [PLAN] Lugar {excursion.id} guardado en UsuarioService")
                        
                        # CRÍTICO: Actualizar lugares_enviados_seguimiento en conversation_data si chat está disponible
                        # BLINDAJE 1: Normalizar ID a string antes de guardar
                        # BLINDAJE 4: Persistencia síncrona inmediata
                        if chat and hasattr(chat, 'conversation_data'):
                            if 'lugares_enviados_seguimiento' not in chat.conversation_data:
                                chat.conversation_data['lugares_enviados_seguimiento'] = []
                            
                            lugar_id_str = str(excursion.id)  # Normalizar a string
                            if lugar_id_str not in chat.conversation_data['lugares_enviados_seguimiento']:
                                chat.conversation_data['lugares_enviados_seguimiento'].append(lugar_id_str)
                                print(f"✅ [PLAN] Agregado lugar {lugar_id_str} a lugares_enviados_seguimiento")
                                
                                # BLINDAJE 4: Persistencia síncrona - verificar inmediatamente después de guardar
                                lugares_guardados = chat.conversation_data.get('lugares_enviados_seguimiento', [])
                                if lugar_id_str in lugares_guardados:
                                    print(f"✅ [PLAN] Verificación: Lugar {lugar_id_str} confirmado en conversation_data")
                                else:
                                    logger.error(f"❌ [PLAN] ERROR: Lugar {lugar_id_str} NO se guardó correctamente en conversation_data")

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
        print(f"🔍 [SEGUIMIENTO] IMPORTANTE: Solo se enviarán lugares de estos nuevos intereses, NO de todos los intereses del usuario")
        print(f"🔍 [SEGUIMIENTO] Intereses totales del usuario: {usuario.intereses if usuario else 'N/A'}")
        print(f"🔍 [SEGUIMIENTO] Nuevos intereses (solo estos se usarán): {nuevos_intereses}")
        
        # SOLUCIÓN 3: Usar arreglo simple de lugares enviados en conversation_data
        lugares_ya_enviados_raw = chat.conversation_data.get('lugares_enviados_seguimiento', [])
        
        # CORRECCIÓN BUG IDs MIXTOS: Normalizar IDs al recuperarlos (no solo al guardarlos)
        # Si conversation_data se guarda en JSON/DB, los números pueden convertirse a int automáticamente
        lugares_ya_enviados = [str(lugar_id) for lugar_id in lugares_ya_enviados_raw]
        
        print(f"🔍 [SEGUIMIENTO] Lugares ya enviados en seguimiento: {len(lugares_ya_enviados)} lugares")
        
        # BLINDAJE DE IDs: Verificar tipos antes y después de normalizar
        print(f"🔍 [SEGUIMIENTO] BLINDAJE IDs - Tipos originales (raw): {[type(lugar_id).__name__ for lugar_id in lugares_ya_enviados_raw[:5]]}")  # Mostrar primeros 5 tipos
        print(f"🔍 [SEGUIMIENTO] BLINDAJE IDs - Valores originales (raw, primeros 5): {lugares_ya_enviados_raw[:5]}")
        print(f"🔍 [SEGUIMIENTO] BLINDAJE IDs - Tipos normalizados: {[type(lugar_id).__name__ for lugar_id in lugares_ya_enviados[:5]]}")
        print(f"🔍 [SEGUIMIENTO] BLINDAJE IDs - Valores normalizados (primeros 5): {lugares_ya_enviados[:5]}")

        # CRÍTICO: Obtener excursiones SOLO para los nuevos intereses (NO todos los intereses del usuario)
        print(f"🔍 [SEGUIMIENTO] Llamando a obtener_excursiones_por_intereses con SOLO nuevos intereses: {nuevos_intereses}")
        excursiones = ExcursionService.obtener_excursiones_por_intereses(
            ciudad=usuario.ciudad,
            intereses=nuevos_intereses,  # CRÍTICO: Solo nuevos intereses, NO usuario.intereses
            perfil=usuario.perfil
        )
        print(f"🔍 [SEGUIMIENTO] Excursiones obtenidas (antes de filtrar): {len(excursiones)} lugares")
        print(f"🔍 [SEGUIMIENTO] Verificando categorías de excursiones obtenidas:")
        for exc in excursiones[:5]:  # Mostrar primeros 5
            print(f"   - {exc.nombre} (Categoría: {exc.categoria})")

        # SOLUCIÓN 3: Filtrar lugares ya enviados usando el arreglo simple
        # CORRECCIÓN BUG IDs MIXTOS: lugares_ya_enviados ya está normalizado arriba
        excursiones_filtradas = []
        for exc in excursiones:
            exc_id_str = str(exc.id)
            if exc_id_str not in lugares_ya_enviados:
                excursiones_filtradas.append(exc)
            else:
                print(f"🔍 [SEGUIMIENTO] BLINDAJE IDs - Lugar {exc_id_str} ({exc.nombre}) EXCLUIDO (ya enviado)")
        
        print(f"🔍 [SEGUIMIENTO] Lugares a enviar después de filtrar: {len(excursiones_filtradas)}")
        
        # BLINDAJE 2: Manejo mejorado de resultados vacíos
        if not excursiones_filtradas:
            # Construir mensaje amigable con los intereses específicos
            if len(nuevos_intereses) == 1:
                interes_nombre = {
                    "restaurantes": "restaurantes",
                    "comercios": "comercios",
                    "compras": "compras",
                    "cultura": "cultura"
                }.get(nuevos_intereses[0].lower(), nuevos_intereses[0])
                mensaje = f"¡Ya te mostré todas nuestras opciones para {interes_nombre}! ¿Te gustaría probar con otra categoría?"
            else:
                intereses_texto = ", ".join(nuevos_intereses[:-1]) + f" y {nuevos_intereses[-1]}"
                mensaje = f"¡Ya te mostré todas nuestras opciones para {intereses_texto}! ¿Te gustaría probar con otra categoría?"
            
            print(f"⚠️ [SEGUIMIENTO] No hay lugares nuevos para enviar. Mensaje enviado al usuario.")
            
            # LOG DETALLADO: Mensaje de no hay lugares
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"\n{'='*80}")
            print(f"📤 [LOG MENSAJE] ENVIANDO MENSAJE (NO HAY LUGARES) - {timestamp}")
            print(f"📤 [LOG MENSAJE] Contenido del mensaje:")
            print(f"{'─'*80}")
            print(mensaje)
            print(f"{'─'*80}")
            print(f"{'='*80}\n")
            
            resultado_no_lugares = enviar_mensaje_whatsapp(numero, mensaje)
            if resultado_no_lugares.get("success"):
                timestamp_result = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"✅ [LOG MENSAJE] ÉXITO - {timestamp_result}")
            else:
                timestamp_result = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"❌ [LOG MENSAJE] FALLO - {timestamp_result} - Error: {resultado_no_lugares.get('error', 'Desconocido')}")
            
            # Retornar None para que el flujo continúe normalmente al mensaje de cierre
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
                    
                    # Usar función centralizada con verificación de 2 partes
                    info_enviada_exitosamente = PlanViajeService._enviar_informacion_y_qr(numero, excursion, ruta_qr)

                    # BLINDAJE 3: Verificación de persistencia inmediata
                    if info_enviada_exitosamente:
                        lugares_enviados_ids.append(excursion.id)
                        
                        # CRÍTICO: Guardar en UsuarioService PRIMERO (persistencia principal)
                        UsuarioService.agregar_lugar_enviado(numero, excursion.id, excursion.categoria.lower())
                        # Asegurar que el usuario se actualice en memoria
                        usuario_actualizado = UsuarioService.obtener_usuario_por_telefono(numero)
                        if usuario_actualizado:
                            UsuarioService.actualizar_usuario(usuario_actualizado)
                            print(f"✅ [SEGUIMIENTO] Lugar {excursion.id} guardado en UsuarioService")
                        
                        # CRÍTICO: Guardar en conversation_data SEGUNDO (para filtrado inmediato)
                        # CORRECCIÓN BUG IDs MIXTOS: Siempre normalizar a string antes de guardar
                        # BLINDAJE 4: Persistencia síncrona inmediata
                        if 'lugares_enviados_seguimiento' not in chat.conversation_data:
                            chat.conversation_data['lugares_enviados_seguimiento'] = []
                        
                        lugar_id_str = str(excursion.id)  # Normalizar a string SIEMPRE
                        # CORRECCIÓN BUG IDs MIXTOS: Normalizar la lista antes de verificar
                        lugares_actuales_normalizados = [str(lugar_id) for lugar_id in chat.conversation_data['lugares_enviados_seguimiento']]
                        if lugar_id_str not in lugares_actuales_normalizados:
                            chat.conversation_data['lugares_enviados_seguimiento'].append(lugar_id_str)
                            print(f"✅ [SEGUIMIENTO] Agregado lugar {lugar_id_str} a lugares_enviados_seguimiento")
                            
                            # BLINDAJE 4: Persistencia síncrona - verificar inmediatamente después de guardar
                            lugares_guardados_raw = chat.conversation_data.get('lugares_enviados_seguimiento', [])
                            lugares_guardados = [str(lugar_id) for lugar_id in lugares_guardados_raw]  # Normalizar para verificación
                            if lugar_id_str in lugares_guardados:
                                print(f"✅ [SEGUIMIENTO] Verificación: Lugar {lugar_id_str} confirmado en conversation_data")
                            else:
                                logger.error(f"❌ [SEGUIMIENTO] ERROR: Lugar {lugar_id_str} NO se guardó correctamente en conversation_data")

                    # CORRECCIÓN JUMBLE WHATSAPP: Aumentar delay entre lugares para evitar mezcla de mensajes
                    time.sleep(5)  # Pausa aumentada entre lugares para evitar jumble de WhatsApp
                    
                except Exception as e:
                    print(f"     ❌ Error al procesar {excursion.nombre}: {e}")
                    logger.error(f"Error al enviar lugar {excursion.nombre}: {e}")
                    continue
        
        print(f"✅ [SEGUIMIENTO] Finalizado envío de lugares. Total enviados: {len(lugares_enviados_ids)}")

