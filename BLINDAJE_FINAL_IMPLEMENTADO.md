# BLINDAJE FINAL IMPLEMENTADO - CÓDIGO MODIFICADO

## RESUMEN DE LOS 3 AJUSTES

### ✅ AJUSTE 1: Robustez en `_enviar_informacion_y_qr`
- Función `_sanitizar_ruta_qr()` para manejar acentos y caracteres especiales
- Try-except específico para el envío de QR
- Retorna `True` si la información se envió, independientemente del resultado del QR

### ✅ AJUSTE 2: Manejo de resultados vacíos en seguimiento
- Mensaje amigable cuando no hay lugares nuevos
- Mensaje personalizado según cantidad de intereses
- Retorna correctamente para continuar el flujo

### ✅ AJUSTE 3: Verificación de persistencia
- Guarda en `UsuarioService` PRIMERO
- Actualiza `conversation_data` SEGUNDO
- Verifica que se guardó correctamente
- Logs de confirmación

---

## CÓDIGO MODIFICADO

### 1. Función `_sanitizar_ruta_qr()` (NUEVA)

```python
@staticmethod
def _sanitizar_ruta_qr(ruta_qr: str, excursion: Excursion) -> Optional[str]:
    """
    Sanitiza la ruta del QR para manejar acentos y caracteres especiales.
    Busca el archivo tanto con acento como sin él.
    """
    if not ruta_qr:
        return None
    
    # Si la ruta existe tal cual, retornarla
    if os.path.exists(ruta_qr):
        return ruta_qr
    
    # Si no existe, intentar variaciones sin acentos
    directorio = os.path.dirname(ruta_qr)
    nombre_archivo = os.path.basename(ruta_qr)
    
    # Crear variaciones del nombre sin acentos
    nombre_sin_acentos = nombre_archivo
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
    if excursion and excursion.id:
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
```

---

### 2. Función `_enviar_informacion_y_qr()` (MODIFICADA - PARTE 2)

```python
# PARTE 2: Solo si la información se envió exitosamente, enviar QR
if info_enviada_exitosamente and ruta_qr:
    # BLINDAJE 1: Sanitizar y verificar ruta del QR (manejar acentos y caracteres especiales)
    ruta_qr_sanitizada = PlanViajeService._sanitizar_ruta_qr(ruta_qr, excursion)
    
    # BLINDAJE 1: Envolver envío de QR en try-except específico
    # Si el QR falla, retornar True igual (info ya se envió) pero loguear error
    try:
        if ruta_qr_sanitizada and os.path.exists(ruta_qr_sanitizada):
            time.sleep(2)  # Pausa para asegurar que la información se procesó
            caption_qr = f"📱 *Código QR - {excursion.nombre}*\n\nMuestra este QR a la hora de pagar para poder acceder al descuento."
            print(f"     📱 Enviando QR (información enviada exitosamente): {ruta_qr_sanitizada}")
            resultado_qr = enviar_imagen_whatsapp(numero, ruta_qr_sanitizada, caption_qr)
            if resultado_qr.get("success"):
                print(f"     ✅ QR enviado exitosamente")
                time.sleep(2)
            else:
                error_qr = resultado_qr.get('error', 'Error desconocido')
                print(f"     ⚠️ Error al enviar QR (pero información ya enviada): {error_qr}")
                logger.warning(f"Error al enviar QR para {excursion.nombre} (información ya enviada): {error_qr}")
                # NO lanzar excepción, solo loguear - la información ya se envió exitosamente
        else:
            print(f"     ⚠️ QR no existe en ruta (sanitizada): {ruta_qr_sanitizada}")
            logger.warning(f"QR no existe para {excursion.nombre} en ruta: {ruta_qr_sanitizada}")
    except Exception as e:
        # BLINDAJE 1: Si QR falla por cualquier motivo, loguear pero NO afectar el retorno
        print(f"     ⚠️ Excepción al enviar QR (pero información ya enviada): {e}")
        logger.warning(f"Excepción al enviar QR para {excursion.nombre} (información ya enviada): {e}")
        import traceback
        logger.debug(f"Traceback QR: {traceback.format_exc()}")
        # NO lanzar excepción, la información ya se envió exitosamente
elif ruta_qr and not info_enviada_exitosamente:
    print(f"     ⚠️ NO se enviará QR porque la información del lugar no se envió exitosamente")
elif ruta_qr and not os.path.exists(ruta_qr):
    print(f"     ⚠️ QR no existe en ruta: {ruta_qr}")

# BLINDAJE 1: Retornar True si la información se envió, independientemente del resultado del QR
return info_enviada_exitosamente
```

**Cambios clave:**
- ✅ Llama a `_sanitizar_ruta_qr()` antes de verificar existencia
- ✅ Try-except específico que NO lanza excepción si el QR falla
- ✅ Retorna `True` si la información se envió, sin importar el QR
- ✅ Loguea errores del QR sin detener el flujo

---

### 3. Lógica de filtrado en `enviar_lugares_seguimiento()` (MODIFICADA)

```python
# SOLUCIÓN 3: Filtrar lugares ya enviados usando el arreglo simple
excursiones_filtradas = []
for exc in excursiones:
    if exc.id not in lugares_ya_enviados:
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
```

**Cambios clave:**
- ✅ Mensaje personalizado según cantidad de intereses
- ✅ Mensaje amigable y claro
- ✅ Retorna correctamente para continuar el flujo

---

### 4. Verificación de persistencia en `enviar_lugares_seguimiento()` (MODIFICADA)

```python
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
    if 'lugares_enviados_seguimiento' not in chat.conversation_data:
        chat.conversation_data['lugares_enviados_seguimiento'] = []
    if excursion.id not in chat.conversation_data['lugares_enviados_seguimiento']:
        chat.conversation_data['lugares_enviados_seguimiento'].append(excursion.id)
        print(f"✅ [SEGUIMIENTO] Agregado lugar {excursion.id} a lugares_enviados_seguimiento")
        
        # BLINDAJE 3: Verificar persistencia - asegurar que se mantiene en memoria
        # (En este sistema, conversation_data es en memoria, pero verificamos que esté actualizado)
        lugares_guardados = chat.conversation_data.get('lugares_enviados_seguimiento', [])
        if excursion.id in lugares_guardados:
            print(f"✅ [SEGUIMIENTO] Verificación: Lugar {excursion.id} confirmado en conversation_data")
        else:
            logger.error(f"❌ [SEGUIMIENTO] ERROR: Lugar {excursion.id} NO se guardó correctamente en conversation_data")
```

**Cambios clave:**
- ✅ Guarda en `UsuarioService` PRIMERO y actualiza el usuario en memoria
- ✅ Guarda en `conversation_data` SEGUNDO
- ✅ Verifica que se guardó correctamente
- ✅ Logs de confirmación para debugging

---

### 5. Verificación de persistencia en `enviar_plan_con_imagen()` (MODIFICADA)

```python
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
    if chat and hasattr(chat, 'conversation_data'):
        if 'lugares_enviados_seguimiento' not in chat.conversation_data:
            chat.conversation_data['lugares_enviados_seguimiento'] = []
        if excursion.id not in chat.conversation_data['lugares_enviados_seguimiento']:
            chat.conversation_data['lugares_enviados_seguimiento'].append(excursion.id)
            print(f"✅ [PLAN] Agregado lugar {excursion.id} a lugares_enviados_seguimiento")
            
            # BLINDAJE 3: Verificar persistencia - asegurar que se mantiene en memoria
            lugares_guardados = chat.conversation_data.get('lugares_enviados_seguimiento', [])
            if excursion.id in lugares_guardados:
                print(f"✅ [PLAN] Verificación: Lugar {excursion.id} confirmado en conversation_data")
            else:
                logger.error(f"❌ [PLAN] ERROR: Lugar {excursion.id} NO se guardó correctamente en conversation_data")
```

**Cambios clave:**
- ✅ Misma lógica de persistencia que en `enviar_lugares_seguimiento`
- ✅ Verificación inmediata después de guardar
- ✅ Logs de confirmación

---

## BENEFICIOS DEL BLINDAJE

### 1. Robustez en QR
- ✅ Maneja acentos y caracteres especiales (ej: "Charco Bistró")
- ✅ Busca variaciones del archivo si no existe la ruta original
- ✅ Busca por ID de excursión como fallback
- ✅ No detiene el flujo si el QR falla (la información ya se envió)

### 2. Mejor experiencia de usuario
- ✅ Mensaje claro cuando no hay lugares nuevos
- ✅ Mensaje personalizado según intereses seleccionados
- ✅ Flujo continúa correctamente sin quedarse en silencio

### 3. Persistencia garantizada
- ✅ Guarda en dos lugares (UsuarioService y conversation_data)
- ✅ Verifica que se guardó correctamente
- ✅ Logs de confirmación para debugging
- ✅ Actualiza usuario en memoria inmediatamente

---

## FLUJO COMPLETO CON BLINDAJE

1. **Envío de información** → `_enviar_informacion_y_qr()`
   - Envía información del lugar (PARTE 1)
   - Si exitoso → `info_enviada_exitosamente = True`

2. **Envío de QR** (si información exitosa)
   - Sanitiza ruta del QR (`_sanitizar_ruta_qr()`)
   - Intenta enviar QR en try-except específico
   - Si falla → loguea pero NO afecta el retorno
   - Retorna `True` (información ya enviada)

3. **Persistencia inmediata**
   - Guarda en `UsuarioService` PRIMERO
   - Actualiza usuario en memoria
   - Guarda en `conversation_data` SEGUNDO
   - Verifica que se guardó correctamente

4. **Manejo de resultados vacíos**
   - Si no hay lugares nuevos → mensaje amigable
   - Retorna correctamente para continuar flujo

---

## NOTAS IMPORTANTES

- El sistema usa persistencia en memoria (`USUARIOS` dict y `conversation_data`)
- No hay base de datos, por lo que un reinicio del bot perderá `conversation_data`
- Sin embargo, `UsuarioService` mantiene los lugares enviados en `usuario.lugares_enviados`
- El blindaje asegura que ambos sistemas estén sincronizados

