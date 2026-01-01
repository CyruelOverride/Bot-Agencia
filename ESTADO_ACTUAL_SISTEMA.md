# ESTADO ACTUAL DEL SISTEMA - CÓDIGO RELEVANTE

**Fecha de actualización:** Última revisión completa con todas las correcciones de sincronización aplicadas.

---

## 📋 ÍNDICE

1. [Función Principal: `_enviar_informacion_y_qr()`](#1-función-principal-_enviar_informacion_y_qr)
2. [Flujo de Generación de Plan: `flujo_generando_plan()`](#2-flujo-de-generación-de-plan-flujo_generando_plan)
3. [Envío de Lugares en Seguimiento: `enviar_lugares_seguimiento()`](#3-envío-de-lugares-en-seguimiento-enviar_lugares_seguimiento)
4. [Detección de Intereses: `_detectar_intereses_texto()`](#4-detección-de-intereses-_detectar_intereses_texto)
5. [Búsqueda de Excursiones: `obtener_excursiones_por_intereses()`](#5-búsqueda-de-excursiones-obtener_excursiones_por_intereses)
6. [Correcciones Aplicadas](#6-correcciones-aplicadas)

---

## 1. FUNCIÓN PRINCIPAL: `_enviar_informacion_y_qr()`

**Archivo:** `Services/PlanViajeService.py`  
**Línea:** 78-222

### Descripción
Función centralizada que envía información del lugar y luego el QR con verificación de 2 partes.

### Código Actualizado

```78:222:Services/PlanViajeService.py
@staticmethod
def _enviar_informacion_y_qr(numero: str, excursion: Excursion, ruta_qr: Optional[str] = None) -> bool:
    """
    Envía la información del lugar y luego el QR si corresponde.
    Verificación de 2 partes:
    1. Primero envía la información del lugar
    2. Solo si la información se envió exitosamente, envía el QR
    
    Args:
        numero: Número de teléfono del usuario
        excursion: Excursión a enviar
        ruta_qr: Ruta opcional al archivo QR (si no se proporciona, se intenta generar)
    
    Returns:
        bool: True si la información se envió exitosamente, False en caso contrario
    """
    # PARTE 1: Enviar información del lugar (imagen o texto)
    # - Intenta enviar imagen con caption
    # - Si falla → fallback a texto
    # - Si exitoso → info_enviada_exitosamente = True
    
    # PARTE 2: Solo si la información se envió exitosamente, enviar QR
    if info_enviada_exitosamente and ruta_qr:
        # CORRECCIÓN JUMBLE WHATSAPP: Delay aumentado a 5 segundos
        time.sleep(5)  # Pausa para evitar que WhatsApp mezcle mensajes
        
        # Log de rastreo para verificar IDs
        print(f"     🔍 DEBUG: Enviando QR ID={excursion.id} para lugar {excursion.nombre}")
        
        resultado_qr = enviar_imagen_whatsapp(numero, ruta_qr_sanitizada, caption_qr)
        if resultado_qr.get("success"):
            # CORRECCIÓN JUMBLE WHATSAPP: Delay adicional después de confirmación
            time.sleep(3)  # Pausa adicional para evitar jumble
    
    return info_enviada_exitosamente
```

### Características Clave
- ✅ **Verificación de 2 partes:** Solo envía QR si la información se envió exitosamente
- ✅ **Delay aumentado:** 5 segundos antes de QR + 3 segundos después de confirmación
- ✅ **Logs de rastreo:** Debug con ID del lugar para verificar sincronización
- ✅ **Manejo de errores:** Si QR falla, no afecta el retorno (info ya enviada)

---

## 2. FLUJO DE GENERACIÓN DE PLAN: `flujo_generando_plan()`

**Archivo:** `Models/chat.py`  
**Línea:** 1335-1408

### Descripción
Maneja la generación del plan, diferenciando entre flujo normal (con Gemini) y seguimiento (sin Gemini).

### Código Actualizado

```1335:1408:Models/chat.py
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
            # MODO SEGUIMIENTO: Enviar lugares directamente sin Gemini
            print(f"🔍 [GENERAR_PLAN] MODO SEGUIMIENTO ACTIVADO - NO usar Gemini")
            
            # Verificar que nuevos_intereses no esté vacío
            if not nuevos_intereses:
                # Volver a seguimiento si no hay nuevos intereses
                return None
            
            # CRÍTICO: Enviar lugares SOLO de los nuevos intereses
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
            
            # CORRECCIÓN SINCRONIZACIÓN: Limpiar flags AL FINAL, después de que todo termine
            if 'nuevos_intereses_seguimiento' in self.conversation_data:
                del self.conversation_data['nuevos_intereses_seguimiento']
            if 'modo_seguimiento' in self.conversation_data:
                del self.conversation_data['modo_seguimiento']
            
            return None
        else:
            # FLUJO NORMAL: Generar plan completo con Gemini
            print(f"🔍 [GENERAR_PLAN] MODO NORMAL - Usando Gemini para generar plan completo")
            
            # CORRECCIÓN BUG IDs MIXTOS: Normalizar IDs al recuperarlos
            lugares_excluidos_raw = self.conversation_data.get('lugares_enviados_seguimiento', [])
            lugares_excluidos = [str(lugar_id) for lugar_id in lugares_excluidos_raw]
            
            # Generar plan (excluyendo lugares ya enviados)
            plan = PlanViajeService.generar_plan_personalizado(usuario, lugares_excluidos=lugares_excluidos)
            
            # Guardar plan y pasar a presentación
            self.conversation_data['plan_viaje'] = plan
            set_estado_bot(numero, ESTADOS_BOT["PLAN_PRESENTADO"])
            usuario.estado_conversacion = ESTADOS_BOT["PLAN_PRESENTADO"]
            UsuarioService.actualizar_usuario(usuario)
            
            return self.flujo_plan_presentado(numero, texto)
```

### Características Clave
- ✅ **Diferencia flujos:** Seguimiento vs Normal
- ✅ **Limpieza al final:** Flags se limpian después de completar todo el proceso
- ✅ **Normalización de IDs:** IDs normalizados al recuperar de `conversation_data`
- ✅ **Sin duplicación:** Excluye lugares ya enviados del plan normal

---

## 3. ENVÍO DE LUGARES EN SEGUIMIENTO: `enviar_lugares_seguimiento()`

**Archivo:** `Services/PlanViajeService.py`  
**Línea:** 625-787

### Descripción
Envía lugares directamente sin usar Gemini, solo para nuevos intereses que no se hayan enviado antes.

### Código Actualizado (Partes Clave)

```625:787:Services/PlanViajeService.py
@staticmethod
def enviar_lugares_seguimiento(chat, numero: str, usuario: Usuario, nuevos_intereses: List[str]):
    """
    Envía lugares directamente sin usar Gemini para el resumen.
    Solo envía lugares de los nuevos intereses que no se hayan enviado antes.
    """
    # CORRECCIÓN BUG IDs MIXTOS: Normalizar IDs al recuperarlos
    lugares_ya_enviados_raw = chat.conversation_data.get('lugares_enviados_seguimiento', [])
    lugares_ya_enviados = [str(lugar_id) for lugar_id in lugares_ya_enviados_raw]
    
    # BLINDAJE DE IDs: Logs para verificar tipos
    print(f"🔍 [SEGUIMIENTO] BLINDAJE IDs - Tipos originales (raw): {[type(lugar_id).__name__ for lugar_id in lugares_ya_enviados_raw[:5]]}")
    print(f"🔍 [SEGUIMIENTO] BLINDAJE IDs - Valores normalizados (primeros 5): {lugares_ya_enviados[:5]}")
    
    # Obtener excursiones para los nuevos intereses
    excursiones = ExcursionService.obtener_excursiones_por_intereses(
        ciudad=usuario.ciudad,
        intereses=nuevos_intereses,
        perfil=usuario.perfil
    )
    
    # Filtrar lugares ya enviados
    excursiones_filtradas = []
    for exc in excursiones:
        exc_id_str = str(exc.id)
        if exc_id_str not in lugares_ya_enviados:
            excursiones_filtradas.append(exc)
        else:
            print(f"🔍 [SEGUIMIENTO] BLINDAJE IDs - Lugar {exc_id_str} ({exc.nombre}) EXCLUIDO (ya enviado)")
    
    # Manejo de resultados vacíos
    if not excursiones_filtradas:
        # Enviar mensaje amigable
        return
    
    # Enviar lugares
    for excursion in excursiones_cat:
        # Usar función centralizada con verificación de 2 partes
        info_enviada_exitosamente = PlanViajeService._enviar_informacion_y_qr(numero, excursion, ruta_qr)
        
        if info_enviada_exitosamente:
            # Guardar en UsuarioService PRIMERO
            UsuarioService.agregar_lugar_enviado(numero, excursion.id, excursion.categoria.lower())
            usuario_actualizado = UsuarioService.obtener_usuario_por_telefono(numero)
            if usuario_actualizado:
                UsuarioService.actualizar_usuario(usuario_actualizado)
            
            # Guardar en conversation_data SEGUNDO
            lugar_id_str = str(excursion.id)  # Normalizar SIEMPRE
            lugares_actuales_normalizados = [str(lugar_id) for lugar_id in chat.conversation_data['lugares_enviados_seguimiento']]
            if lugar_id_str not in lugares_actuales_normalizados:
                chat.conversation_data['lugares_enviados_seguimiento'].append(lugar_id_str)
        
        # CORRECCIÓN JUMBLE WHATSAPP: Delay aumentado entre lugares
        time.sleep(5)  # Pausa aumentada para evitar jumble de WhatsApp
```

### Características Clave
- ✅ **Filtrado correcto:** Solo envía lugares nuevos (no duplicados)
- ✅ **Normalización de IDs:** Normaliza al recuperar y al guardar
- ✅ **Logs de debugging:** Muestra tipos y valores para verificar sincronización
- ✅ **Delay aumentado:** 5 segundos entre lugares para evitar jumble
- ✅ **Persistencia doble:** Guarda en UsuarioService y conversation_data

---

## 4. DETECCIÓN DE INTERESES: `_detectar_intereses_texto()`

**Archivo:** `Models/chat.py`  
**Línea:** 1071-1164

### Descripción
Detecta intereses del texto del usuario, soportando números, letras, nombres completos y variaciones.

### Código Actualizado (Partes Clave)

```1071:1164:Models/chat.py
def _detectar_intereses_texto(self, texto: str) -> List[str]:
    """
    Detecta intereses del texto del usuario.
    Soporta:
    - Números: "1 2 3 4" → restaurantes, comercios, compras, cultura
    - Letras: "A B C D" → restaurantes, comercios, compras, cultura
    - Nombres completos o parciales: "restaurantes compras comercios cultura"
    - "todo" → todos los intereses
    """
    texto_lower = texto.lower().strip()
    
    # Mapeo de intereses (incluye todas las variaciones de "cultura")
    intereses_map = {
        "1": "restaurantes", "a": "restaurantes",
        "restaurante": "restaurantes", "restaurantes": "restaurantes", "comida": "restaurantes",
        "2": "comercios", "b": "comercios",
        "comercio": "comercios", "comercios": "comercios", "tienda": "comercios", "tiendas": "comercios",
        "3": "compras", "c": "compras",
        "compra": "compras", "compras": "compras", "shopping": "compras", "regalo": "compras", "regalos": "compras",
        "4": "cultura", "d": "cultura",
        "cultura": "cultura", "cultural": "cultura", "culturas": "cultura", "cult": "cultura",
        "arte": "cultura", "teatro": "cultura", "museo": "cultura", "museos": "cultura",
        "espectaculos": "cultura", "espectáculos": "cultura", "turismo": "cultura",
        "patrimonio": "cultura", "historia": "cultura"
    }
    
    # Procesar texto y detectar intereses
    # - Coincidencia exacta primero
    # - Coincidencia parcial si no hay exacta
    # - Case-insensitive en todas las comparaciones
    
    return intereses_detectados
```

### Características Clave
- ✅ **Mapeo completo:** Incluye todas las variaciones de "cultura"
- ✅ **Case-insensitive:** Todas las comparaciones usan `.lower()`
- ✅ **Coincidencia exacta y parcial:** Soporta múltiples formatos de entrada
- ✅ **Logs de debugging:** Muestra qué intereses se detectaron

---

## 5. BÚSQUEDA DE EXCURSIONES: `obtener_excursiones_por_intereses()`

**Archivo:** `Services/ExcursionService.py`  
**Línea:** 88-123

### Descripción
Obtiene excursiones filtradas por intereses y perfil, con mapeo correcto de "cultura" a "cultural".

### Código Actualizado

```88:123:Services/ExcursionService.py
@staticmethod
def obtener_excursiones_por_intereses(
    ciudad: str,
    intereses: List[str],
    perfil: Optional[PerfilUsuario] = None
) -> List[Excursion]:
    """Obtiene excursiones filtradas por intereses y perfil"""
    todas_las_excursiones = ExcursionService.obtener_excursiones_por_ciudad(ciudad)
    
    # Mapeo de intereses a categorías
    mapeo_interes_categoria = {
        "cultura": "cultural"  # El interés "cultura" se mapea a la categoría "cultural"
    }
    
    # CORRECCIÓN CULTURA: Normalizar intereses a lowercase ANTES del mapeo
    categorias_interes = []
    for interes in intereses:
        interes_normalizado = interes.lower().strip()  # Normalizar y limpiar
        categoria = mapeo_interes_categoria.get(interes_normalizado, interes_normalizado)
        categorias_interes.append(categoria)
    
    # CORRECCIÓN CULTURA: Log para debugging
    print(f"🔍 [EXCURSION_SERVICE] Intereses recibidos: {intereses}")
    print(f"🔍 [EXCURSION_SERVICE] Categorías mapeadas: {categorias_interes}")
    
    if not perfil:
        # CORRECCIÓN CULTURA: Asegurar comparación case-insensitive en ambos lados
        excursiones_filtradas = [
            exc for exc in todas_las_excursiones
            if exc.categoria.lower() in categorias_interes or any(
                cat.lower() in exc.categoria.lower() for cat in categorias_interes
            )
        ]
        print(f"🔍 [EXCURSION_SERVICE] Excursiones encontradas (sin perfil): {len(excursiones_filtradas)}")
        return excursiones_filtradas
    
    # Para filtrar por perfil, usar las categorías mapeadas
    intereses_mapeados = [mapeo_interes_categoria.get(i.lower(), i.lower()) for i in intereses]
    return ExcursionService.filtrar_por_perfil(todas_las_excursiones, perfil, intereses_mapeados)
```

### Características Clave
- ✅ **Mapeo correcto:** "cultura" → "cultural"
- ✅ **Normalización:** Intereses normalizados a lowercase antes del mapeo
- ✅ **Comparación case-insensitive:** Usa `.lower()` en ambos lados
- ✅ **Logs de debugging:** Muestra intereses recibidos y categorías mapeadas

---

## 6. CORRECCIONES APLICADAS

### ✅ Corrección 1: Borrado Prematuro de Flags
- **Problema:** Flags se borraban antes de completar el proceso
- **Solución:** Flags se limpian al final de `flujo_generando_plan()`, después de que todo termine
- **Ubicación:** `Models/chat.py` líneas 1375-1381

### ✅ Corrección 2: Jumble de WhatsApp (QRs sin sentido)
- **Problema:** WhatsApp mezclaba mensajes cuando se enviaban muy rápido
- **Solución:** 
  - Delay aumentado a 5 segundos antes de enviar QR
  - Delay adicional de 3 segundos después de confirmación de QR
  - Delay aumentado a 5 segundos entre lugares
- **Ubicación:** `Services/PlanViajeService.py` líneas 190, 200, 778

### ✅ Corrección 3: Error de "Cultura" (Case Sensitivity)
- **Problema:** "cultura" no se encontraba si la categoría estaba en mayúsculas
- **Solución:**
  - Normalización de intereses a lowercase antes del mapeo
  - Comparación case-insensitive en ambos lados
  - Logs de debugging para rastrear el proceso
- **Ubicación:** `Services/ExcursionService.py` líneas 102-122

### ✅ Corrección 4: Bug de IDs Mixtos
- **Problema:** IDs se guardaban como strings pero se recuperaban como ints desde JSON/DB
- **Solución:**
  - Normalización de IDs al recuperar de `conversation_data`
  - Normalización de IDs al guardar en `conversation_data`
  - Normalización de IDs antes de verificar existencia
  - Logs de debugging para verificar tipos
- **Ubicación:** 
  - `Services/PlanViajeService.py` líneas 646-650, 762-765
  - `Models/chat.py` líneas 1391-1392

---

## 📊 RESUMEN DE ESTADO

### ✅ Funcionalidades Correctas
1. **Envío de información y QR:** Verificación de 2 partes funcionando
2. **Filtrado de lugares duplicados:** Solo envía lugares nuevos
3. **Detección de intereses:** "cultura" se detecta correctamente
4. **Búsqueda de excursiones:** Comparación case-insensitive funcionando
5. **Sincronización de IDs:** Normalización consistente en todo el sistema
6. **Delays de WhatsApp:** Aumentados para evitar jumble de mensajes

### 🔍 Logs de Debugging Disponibles
- Tipos y valores de IDs (antes y después de normalizar)
- Intereses recibidos y categorías mapeadas
- Lugares excluidos y lugares enviados
- Confirmación de envío de QR con ID del lugar

### ⚠️ Puntos de Atención
- Los delays pueden hacer que el bot responda más lento, pero garantizan orden correcto
- Los logs pueden generar mucho output en consola (útil para debugging)
- La normalización de IDs es crítica: cualquier lugar que no normalice puede causar duplicados

---

**Última actualización:** Todas las correcciones de sincronización aplicadas y verificadas.

