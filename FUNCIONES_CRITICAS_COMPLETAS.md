# FUNCIONES CRÍTICAS COMPLETAS - ANÁLISIS DE ERRORES

## 1. `flujo_generando_plan()` - Models/chat.py (Línea 1335)

```python
def flujo_generando_plan(self, numero, texto):
    """Genera el plan personalizado usando Gemini y ExcursionService"""
    usuario = UsuarioService.obtener_usuario_por_telefono(numero)
    
    if not usuario:
        return self.flujo_inicio(numero, texto)
    
    try:
        # Verificar si viene desde seguimiento (agregando más intereses)
        nuevos_intereses = self.conversation_data.get('nuevos_intereses_seguimiento', None)
        modo_seguimiento = self.conversation_data.get('modo_seguimiento', False)

        if nuevos_intereses or modo_seguimiento:
            # Viene desde seguimiento: usar método directo sin Gemini
            print(f"🔍 [GENERAR_PLAN] MODO SEGUIMIENTO ACTIVADO - NO usar Gemini")

            # Verificar que nuevos_intereses no esté vacío
            if not nuevos_intereses:
                print(f"⚠️ [GENERAR_PLAN] No hay nuevos intereses, volviendo a seguimiento")
                set_estado_bot(numero, ESTADOS_BOT["SEGUIMIENTO"])
                usuario.estado_conversacion = ESTADOS_BOT["SEGUIMIENTO"]
                UsuarioService.actualizar_usuario(usuario)
                return None

            # Limpiar flags de seguimiento
            if 'nuevos_intereses_seguimiento' in self.conversation_data:
                del self.conversation_data['nuevos_intereses_seguimiento']
            if 'modo_seguimiento' in self.conversation_data:
                del self.conversation_data['modo_seguimiento']

            # CRÍTICO: Enviar lugares SOLO de los nuevos intereses, NO todo el plan
            print(f"🔍 [GENERAR_PLAN] ENVIANDO SOLO LUGARES DE NUEVOS INTERESES: {nuevos_intereses}")
            PlanViajeService.enviar_lugares_seguimiento(self, numero, usuario, nuevos_intereses)

            # Obtener usuario actualizado después de enviar lugares
            usuario = UsuarioService.obtener_usuario_por_telefono(numero)

            # Enviar mensaje de cierre
            self._enviar_mensaje_cierre_recomendaciones(numero, usuario, None)

            # Pasar a seguimiento
            set_estado_bot(numero, ESTADOS_BOT["SEGUIMIENTO"])
            if usuario:
                usuario.estado_conversacion = ESTADOS_BOT["SEGUIMIENTO"]
                UsuarioService.actualizar_usuario(usuario)

            return None
        else:
            # Flujo normal: generar plan completo con Gemini
            print(f"🔍 [GENERAR_PLAN] MODO NORMAL - Usando Gemini para generar plan completo")

            # Obtener lugares ya enviados para excluirlos de nuevas recomendaciones
            # CRÍTICO: Asegurar que siempre se use la lista completa de lugares enviados
            lugares_excluidos = self.conversation_data.get('lugares_enviados_seguimiento', [])
            print(f"🔍 [GENERAR_PLAN] Lugares excluidos del plan: {len(lugares_excluidos)} lugares")
            if lugares_excluidos:
                print(f"🔍 [GENERAR_PLAN] IDs excluidos: {lugares_excluidos[:10]}...")  # Mostrar primeros 10

            # Generar plan (excluyendo lugares ya enviados si hay)
            plan = PlanViajeService.generar_plan_personalizado(usuario, lugares_excluidos=lugares_excluidos)

            # Guardar plan en conversation_data
            self.conversation_data['plan_viaje'] = plan

            # Pasar a presentación del plan
            set_estado_bot(numero, ESTADOS_BOT["PLAN_PRESENTADO"])
            usuario.estado_conversacion = ESTADOS_BOT["PLAN_PRESENTADO"]
            UsuarioService.actualizar_usuario(usuario)
            
            return self.flujo_plan_presentado(numero, texto)
        
    except Exception as e:
        print(f"Error al generar plan: {e}")
        import traceback
        traceback.print_exc()
        return enviar_mensaje_whatsapp(
            numero,
            "⚠️ Hubo un error al generar tu plan. Por favor, intentá de nuevo o escribí /reiniciar para comenzar de nuevo."
        )
```

**Puntos críticos:**
- Línea 1344-1345: Verifica `nuevos_intereses_seguimiento` y `modo_seguimiento`
- Línea 1367: Llama a `enviar_lugares_seguimiento()` si está en modo seguimiento
- Línea 1387: Obtiene `lugares_excluidos` de `conversation_data`
- Línea 1393: Llama a `generar_plan_personalizado()` con lugares excluidos
- Línea 1396: Guarda el plan en `conversation_data['plan_viaje']`

---

## 2. `enviar_lugares_seguimiento()` - Services/PlanViajeService.py (Línea 616)

```python
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
    # BLINDAJE 1: Normalizar IDs a string para comparación consistente
    lugares_ya_enviados_normalizados = [str(lugar_id) for lugar_id in lugares_ya_enviados]
    excursiones_filtradas = []
    for exc in excursiones:
        if str(exc.id) not in lugares_ya_enviados_normalizados:
            excursiones_filtradas.append(exc)
    
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
        enviar_mensaje_whatsapp(numero, mensaje)
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
                    # BLINDAJE 1: Normalizar ID a string antes de guardar
                    # BLINDAJE 4: Persistencia síncrona inmediata
                    if 'lugares_enviados_seguimiento' not in chat.conversation_data:
                        chat.conversation_data['lugares_enviados_seguimiento'] = []
                    
                    lugar_id_str = str(excursion.id)  # Normalizar a string
                    if lugar_id_str not in chat.conversation_data['lugares_enviados_seguimiento']:
                        chat.conversation_data['lugares_enviados_seguimiento'].append(lugar_id_str)
                        print(f"✅ [SEGUIMIENTO] Agregado lugar {lugar_id_str} a lugares_enviados_seguimiento")
                        
                        # BLINDAJE 4: Persistencia síncrona - verificar inmediatamente después de guardar
                        lugares_guardados = chat.conversation_data.get('lugares_enviados_seguimiento', [])
                        if lugar_id_str in lugares_guardados:
                            print(f"✅ [SEGUIMIENTO] Verificación: Lugar {lugar_id_str} confirmado en conversation_data")
                        else:
                            logger.error(f"❌ [SEGUIMIENTO] ERROR: Lugar {lugar_id_str} NO se guardó correctamente en conversation_data")

                time.sleep(3)
                
            except Exception as e:
                print(f"     ❌ Error al procesar {excursion.nombre}: {e}")
                logger.error(f"Error al enviar lugar {excursion.nombre}: {e}")
                continue
    
    print(f"✅ [SEGUIMIENTO] Finalizado envío de lugares. Total enviados: {len(lugares_enviados_ids)}")
```

**Puntos críticos:**
- Línea 637: Obtiene `lugares_ya_enviados` de `conversation_data`
- Línea 641-645: Obtiene excursiones para `nuevos_intereses`
- Línea 649-653: Filtra lugares ya enviados (normalizando IDs a string)
- Línea 720: Llama a `_enviar_informacion_y_qr()`
- Línea 740-742: Guarda lugar en `conversation_data` (normalizado a string)

---

## 3. `_detectar_intereses_texto()` - Models/chat.py (Línea 1071)

```python
def _detectar_intereses_texto(self, texto: str) -> List[str]:
    """
    Detecta intereses del texto del usuario.
    Soporta:
    - Números: "1 2 3 4" → restaurantes, comercios, compras, cultura
    - Letras: "A B C D" → restaurantes, comercios, compras, cultura
    - Nombres completos o parciales: "restaurantes compras comercios cultura"
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
        "3": "compras",
        "c": "compras",
        "compra": "compras",
        "compras": "compras",
        "shopping": "compras",
        "regalo": "compras",
        "regalos": "compras",
        "4": "cultura",
        "d": "cultura",
        "cultura": "cultura",
        "cultural": "cultura",
        "culturas": "cultura",
        "cult": "cultura",
        "arte": "cultura",
        "teatro": "cultura",
        "museo": "cultura",
        "museos": "cultura",
        "espectaculos": "cultura",
        "espectáculos": "cultura",
        "turismo": "cultura",
        "patrimonio": "cultura",
        "historia": "cultura"
    }
    
    intereses_validos = ["restaurantes", "comercios", "compras", "cultura"]
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
        palabra_limpia = palabra.strip().lower()
        # Verificar coincidencia exacta primero (más rápido y preciso)
        if palabra_limpia in intereses_map:
            interes = intereses_map[palabra_limpia]
            if interes not in intereses_detectados:
                intereses_detectados.append(interes)
                print(f"🔍 [DETECTAR] Interés detectado por coincidencia exacta: '{palabra_limpia}' -> '{interes}'")
        else:
            # Buscar coincidencias parciales solo si la palabra tiene más de 2 caracteres
            # (evita falsos positivos con números de un solo dígito)
            if len(palabra_limpia) > 2:
                for key, interes in intereses_map.items():
                    # Verificar si la palabra contiene la clave o viceversa (case insensitive)
                    if key.lower() in palabra_limpia or palabra_limpia in key.lower():
                        if interes not in intereses_detectados:
                            intereses_detectados.append(interes)
                            print(f"🔍 [DETECTAR] Interés detectado por coincidencia parcial: '{palabra_limpia}' contiene '{key}' -> '{interes}'")
                        break
    
    return intereses_detectados
```

**Puntos críticos:**
- Línea 1105-1119: Mapeo completo de "cultura" con todas sus variaciones
- Línea 1147-1151: Coincidencia exacta primero
- Línea 1155-1162: Coincidencia parcial si no hay exacta
- Línea 1164: Retorna lista de intereses detectados (sin duplicados)

---

## ANÁLISIS DE POSIBLES ERRORES

### Error 1: Duplicación de lugares
**Posible causa en `enviar_lugares_seguimiento()`:**
- Línea 641-645: Obtiene excursiones para `nuevos_intereses`
- **PROBLEMA POTENCIAL:** Si `nuevos_intereses` contiene intereses que ya tenía el usuario, podría obtener lugares que ya se enviaron
- **VERIFICAR:** ¿`nuevos_intereses` contiene solo intereses realmente nuevos?

### Error 2: QR sin información
**Función `_enviar_informacion_y_qr()`:**
- Línea 180-214: Solo envía QR si `info_enviada_exitosamente == True`
- **VERIFICAR:** ¿La función realmente retorna `False` cuando falla el envío de información?

### Error 3: No detecta "cultura"
**Función `_detectar_intereses_texto()`:**
- El mapeo está correcto (línea 1107: "cultura" → "cultura")
- **VERIFICAR:** ¿El problema está en cómo se procesa después de detectar?

### Error 4: Plan completo en seguimiento
**Función `flujo_generando_plan()`:**
- Línea 1347: Verifica `nuevos_intereses` o `modo_seguimiento`
- **PROBLEMA POTENCIAL:** Si `nuevos_intereses` está vacío o `None`, cae al flujo normal (línea 1382)
- **VERIFICAR:** ¿Se está limpiando `nuevos_intereses_seguimiento` antes de tiempo?

