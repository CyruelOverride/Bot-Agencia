from typing import List, Optional
import os
import logging
from Models.plan_viaje import PlanViaje
from Models.usuario import Usuario
from Models.excursion import Excursion
from Services.ExcursionService import ExcursionService
from Services.GeminiOrchestratorService import GeminiOrchestratorService

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
            ids_existentes = {exc.id for exc in excursiones}
            for exc in excursiones_adicionales:
                if exc.id not in ids_existentes and len(excursiones) < 15:
                    excursiones.append(exc)
                    ids_existentes.add(exc.id)
        
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
                rows.append({
                    "id": f"exc_{exc.id}",
                    "title": f"{emoji} {exc.nombre}",
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
                    "text": f"{plan.ciudad} - {len(plan.excursiones)} recomendaciones"
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
        Envía el plan con una imagen principal y el resumen como caption.
        Prioriza imágenes de las excursiones del plan. Si no hay, busca imagen local por defecto.
        Si falla la imagen, continúa enviando el texto sin interrumpir el flujo.
        
        Args:
            numero: Número de teléfono del usuario
            plan: Plan de viaje a enviar
            ruta_imagen: Ruta opcional a la imagen. Si no se proporciona, busca automáticamente
        """
        from whatsapp_api import enviar_imagen_whatsapp, enviar_mensaje_whatsapp
        import time
        
        # Determinar imagen a usar
        imagen_a_enviar = None
        
        # Prioridad 1: Imagen proporcionada explícitamente
        if ruta_imagen:
            imagen_a_enviar = ruta_imagen
        else:
            # Prioridad 2: Buscar imagen_url en las excursiones del plan (solo si tienen URL)
            for excursion in plan.excursiones:
                if excursion.imagen_url:
                    imagen_a_enviar = excursion.imagen_url
                    break  # Usar la primera que encuentre
            
            # Prioridad 3: Si no hay imagen en excursiones, buscar imagen local por defecto
            if not imagen_a_enviar:
                base_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "imagenes")
                ciudad_lower = plan.ciudad.lower().replace(" ", "_")
                ruta_especifica = os.path.join(base_path, f"plan_{ciudad_lower}.png")
                ruta_default = os.path.join(base_path, "plan_default.png")
                
                if os.path.exists(ruta_especifica):
                    imagen_a_enviar = ruta_especifica
                elif os.path.exists(ruta_default):
                    imagen_a_enviar = ruta_default
        
        # Intentar enviar imagen solo si existe (evitar errores)
        if imagen_a_enviar:
            try:
                # Caption con resumen corto (500-700 chars recomendado, usamos 700 como máximo seguro)
                caption = f"🎯 Tu Plan Personalizado para {plan.ciudad}\n\n{plan.resumen_ia[:700]}"
                
                resultado = enviar_imagen_whatsapp(numero, imagen_a_enviar, caption)
                
                if resultado.get("success"):
                    # Pequeña pausa para mejor UX
                    time.sleep(1)
                else:
                    logger.warning(f"No se pudo enviar imagen del plan: {resultado.get('error', 'Error desconocido')}")
                    
            except Exception as e:
                # Error silencioso: no interrumpir el flujo si falla la imagen
                logger.warning(f"No se pudo enviar imagen del plan: {e}")
        
        # Siempre enviar el plan detallado como texto (incluso si no hay imagen o falló)
        mensaje_plan = PlanViajeService.formatear_plan_para_whatsapp(plan)
        enviar_mensaje_whatsapp(numero, mensaje_plan)

