# EXPLICACIÓN DEL FLUJO Y CORRECCIONES REALIZADAS

## FLUJO COMPLETO DEL SISTEMA

### FLUJO NORMAL (Primera vez - Plan inicial)

1. **Usuario inicia conversación** → `flujo_inicio`
   - El bot saluda y pregunta por el nombre

2. **Usuario completa perfil** → `flujo_armando_perfil`
   - El bot pregunta: tipo de viaje, acompañantes, duración, preferencias de comida, etc.
   - Usa Gemini para interpretar las respuestas

3. **Usuario selecciona intereses** → `flujo_seleccion_intereses`
   - El bot muestra opciones: Restaurantes, Comercios, Compras, Cultura
   - Usuario puede seleccionar por texto ("1 2 3" o "restaurantes compras") o por botones
   - Cuando confirma → pasa a `GENERANDO_PLAN`

4. **Sistema genera plan** → `flujo_generando_plan`
   - Llama a `generar_plan_personalizado()` que:
     - Obtiene excursiones según intereses del usuario
     - **USA GEMINI** para generar un resumen personalizado del plan
     - Crea un objeto `PlanViaje` con todas las excursiones
   - Guarda el plan en `conversation_data['plan_viaje']`
   - Pasa a estado `PLAN_PRESENTADO`

5. **Sistema presenta plan** → `flujo_plan_presentado`
   - Llama a `enviar_plan_con_imagen()` que:
     - Envía imagen con resumen del plan (generado por Gemini)
     - Para cada excursión del plan:
       - Genera QR si es restaurante/comercio
       - Llama a `_enviar_informacion_y_qr()` que:
         - **PARTE 1**: Envía información del lugar (imagen con caption o texto)
         - **PARTE 2**: Solo si la información se envió exitosamente, envía el QR
       - Si se envió exitosamente → guarda en `UsuarioService` y en `conversation_data['lugares_enviados_seguimiento']`
   - Envía mensaje de cierre con botones
   - Pasa a estado `SEGUIMIENTO`

### FLUJO DE SEGUIMIENTO (Agregar más intereses)

1. **Usuario en estado SEGUIMIENTO**
   - El bot muestra mensaje: "¿Querés agregar más intereses?"
   - Botones: "Sí, agregar más" / "No, gracias"

2. **Usuario presiona "Sí, agregar más"**
   - Se activa `agregando_mas_intereses = True`
   - Se guarda `intereses_anteriores = usuario.intereses.copy()`
   - Se muestra lista de intereses (excluyendo los ya seleccionados)

3. **Usuario selecciona nuevos intereses** (texto o botón)
   - Si es texto → `_detectar_intereses_texto()` detecta los intereses
   - Se agregan a `usuario.intereses` (sin duplicar)
   - Si viene de seguimiento:
     - Se guarda `nuevos_intereses_seguimiento = intereses_nuevos`
     - Se activa `modo_seguimiento = True` (BANDERA CRÍTICA)
     - Se pasa a estado `GENERANDO_PLAN`

4. **Sistema procesa nuevos intereses** → `flujo_generando_plan`
   - **VERIFICA**: ¿Hay `nuevos_intereses_seguimiento` o `modo_seguimiento`?
   - **SI HAY BANDERA**:
     - **NO usa Gemini** (evita generar plan completo)
     - Llama directamente a `enviar_lugares_seguimiento()` que:
       - Obtiene excursiones SOLO para los nuevos intereses
       - Filtra lugares ya enviados usando `lugares_enviados_seguimiento`
       - Para cada lugar nuevo:
         - Llama a `_enviar_informacion_y_qr()` (verificación de 2 partes)
         - Si se envió exitosamente → guarda en `lugares_enviados_seguimiento`
   - **SI NO HAY BANDERA** (flujo normal):
     - Usa Gemini para generar plan completo
     - Pasa a `PLAN_PRESENTADO`

5. **Sistema envía mensaje de cierre**
   - Verifica si el usuario tiene todos los intereses
   - Si no → muestra botón "Sí, agregar más"
   - Si sí → solo muestra "No, gracias"

---

## ERRORES IDENTIFICADOS Y CORREGIDOS

### ERROR 1: Código QR se envía sin información del lugar

**Problema:**
- El QR se enviaba incluso cuando la información del lugar no se había enviado exitosamente
- No había verificación de 2 partes consistente

**Causa raíz:**
- La lógica de envío estaba duplicada en `enviar_plan_con_imagen` y `enviar_lugares_seguimiento`
- No había una función centralizada que garantizara la verificación de 2 partes

**Solución implementada:**
1. Creé función centralizada `_enviar_informacion_y_qr()` en `PlanViajeService`:
   ```python
   def _enviar_informacion_y_qr(numero, excursion, ruta_qr):
       # PARTE 1: Enviar información
       info_enviada_exitosamente = False
       # Intenta enviar imagen, si falla intenta texto
       # Solo marca True si realmente se envió
       
       # PARTE 2: Solo si info_enviada_exitosamente == True
       if info_enviada_exitosamente and ruta_qr:
           # Enviar QR
       
       return info_enviada_exitosamente
   ```

2. Reemplacé toda la lógica duplicada en ambos métodos para usar esta función

3. Ahora el QR **SOLO** se envía si:
   - La información se envió exitosamente (`info_enviada_exitosamente == True`)
   - Existe el archivo QR (`ruta_qr` existe)
   - El archivo QR está en el sistema (`os.path.exists(ruta_qr)`)

---

### ERROR 2: Sigue enviando lugares que ya había enviado antes

**Problema:**
- En seguimiento, cuando se agregaban nuevos intereses, se enviaban lugares que ya se habían enviado en el plan inicial

**Causa raíz:**
1. En `flujo_plan_presentado`, se guardaban **TODOS** los lugares del plan en `lugares_enviados_seguimiento` **ANTES** de enviarlos:
   ```python
   # ❌ INCORRECTO (antes)
   lugares_enviados = [exc.id for exc in plan.excursiones]
   self.conversation_data['lugares_enviados_seguimiento'].extend(lugares_enviados)
   PlanViajeService.enviar_plan_con_imagen(numero, plan)  # Se envían después
   ```
   Esto marcaba lugares como "enviados" aunque no se hubieran enviado realmente.

2. En `enviar_plan_con_imagen`, los lugares se guardaban en `UsuarioService` pero **NO** se actualizaba `lugares_enviados_seguimiento` en `conversation_data`.

3. En `enviar_lugares_seguimiento`, se filtraba usando `lugares_enviados_seguimiento`, pero como estaba desactualizado, no filtraba correctamente.

**Solución implementada:**
1. **Eliminé** la guarda previa de lugares en `flujo_plan_presentado`:
   ```python
   # ✅ CORRECTO (ahora)
   # NO guardar antes, solo inicializar lista vacía
   if 'lugares_enviados_seguimiento' not in self.conversation_data:
       self.conversation_data['lugares_enviados_seguimiento'] = []
   
   # Pasar chat para que pueda actualizar conversation_data
   PlanViajeService.enviar_plan_con_imagen(numero, plan, chat=self)
   ```

2. **Modifiqué** `enviar_plan_con_imagen` para:
   - Aceptar parámetro `chat` opcional
   - Actualizar `lugares_enviados_seguimiento` **SOLO** cuando un lugar se envía exitosamente:
   ```python
   if info_enviada_exitosamente:
       UsuarioService.agregar_lugar_enviado(...)
       
       # CRÍTICO: Actualizar conversation_data
       if chat and hasattr(chat, 'conversation_data'):
           if excursion.id not in chat.conversation_data['lugares_enviados_seguimiento']:
               chat.conversation_data['lugares_enviados_seguimiento'].append(excursion.id)
   ```

3. **Aseguré** que `enviar_lugares_seguimiento` también actualice `lugares_enviados_seguimiento` cuando envía lugares nuevos

4. **Corregí** `flujo_plan_presentado` para que solo actualice `UsuarioService` con los lugares que realmente se enviaron (los que están en `conversation_data`)

---

### ERROR 3: Sigue usando Gemini en seguimiento (envía plan completo)

**Problema:**
- En seguimiento, cuando se agregaban nuevos intereses, el sistema generaba un plan completo nuevo usando Gemini en lugar de enviar solo los lugares de los nuevos intereses

**Causa raíz:**
- Cuando el usuario escribía intereses desde texto en modo seguimiento, se llamaba a `flujo_generando_plan` pero **NO** se activaba la bandera `modo_seguimiento`
- `flujo_generando_plan` no detectaba que venía de seguimiento y usaba Gemini normalmente

**Solución implementada:**
1. **Activé** la bandera `modo_seguimiento` cuando se detectan intereses desde texto en seguimiento:
   ```python
   if self.conversation_data.get('agregando_mas_intereses', False):
       if intereses_nuevos:
           self.conversation_data['nuevos_intereses_seguimiento'] = intereses_nuevos
           # CRÍTICO: Activar bandera para evitar Gemini
           self.conversation_data['modo_seguimiento'] = True
   ```

2. **Verifiqué** en `flujo_generando_plan` que detecte correctamente el modo seguimiento:
   ```python
   nuevos_intereses = self.conversation_data.get('nuevos_intereses_seguimiento', None)
   modo_seguimiento = self.conversation_data.get('modo_seguimiento', False)
   
   if nuevos_intereses or modo_seguimiento:
       # NO usar Gemini, enviar lugares directamente
       PlanViajeService.enviar_lugares_seguimiento(self, numero, usuario, nuevos_intereses)
   else:
       # Flujo normal: usar Gemini
       plan = PlanViajeService.generar_plan_personalizado(...)
   ```

---

### ERROR 4: No detecta "cultura" como interés

**Problema:**
- Cuando el usuario escribía "cultura", el sistema no lo detectaba como interés válido

**Causa raíz:**
- La comparación en `_detectar_intereses_texto` no era completamente case-insensitive
- Si el usuario escribía "Cultura" (con mayúscula), no coincidía con "cultura" (minúscula) en el mapa

**Solución implementada:**
1. **Mejoré** la normalización de palabras:
   ```python
   palabra_limpia = palabra.strip().lower()  # Asegurar lowercase
   ```

2. **Mejoré** la comparación en coincidencias parciales para ser case-insensitive:
   ```python
   if key.lower() in palabra_limpia or palabra_limpia in key.lower():
   ```

3. **Agregué** logs de depuración para ver qué se detecta:
   ```python
   print(f"🔍 [DETECTAR] Interés detectado: '{palabra_limpia}' -> '{interes}'")
   ```

---

## RESUMEN DE LO ÚLTIMO QUE HICE

### Cambios en `Models/chat.py`:

1. **`flujo_plan_presentado`** (línea ~1398):
   - ❌ **ANTES**: Guardaba todos los lugares del plan en `lugares_enviados_seguimiento` ANTES de enviarlos
   - ✅ **AHORA**: Solo inicializa la lista vacía, los lugares se guardan DESPUÉS de enviarlos exitosamente
   - ✅ **AHORA**: Pasa `chat=self` a `enviar_plan_con_imagen` para que pueda actualizar `conversation_data`

2. **`flujo_plan_presentado`** (línea ~1409):
   - ❌ **ANTES**: Actualizaba `UsuarioService` con TODOS los lugares del plan
   - ✅ **AHORA**: Solo actualiza con los lugares que realmente se enviaron (los que están en `conversation_data['lugares_enviados_seguimiento']`)

3. **`_detectar_intereses_texto`** (línea ~1123):
   - ✅ **MEJORADO**: Normalización a lowercase más robusta
   - ✅ **MEJORADO**: Comparación case-insensitive en coincidencias parciales
   - ✅ **AGREGADO**: Logs de depuración para ver qué se detecta

### Cambios en `Services/PlanViajeService.py`:

1. **`enviar_plan_con_imagen`** (línea ~361):
   - ✅ **AGREGADO**: Parámetro `chat` opcional
   - ✅ **AGREGADO**: Actualiza `lugares_enviados_seguimiento` en `conversation_data` cuando un lugar se envía exitosamente (línea ~489-495)

2. **`_enviar_informacion_y_qr`** (ya existía, se usa correctamente):
   - Esta función garantiza la verificación de 2 partes
   - Se usa en `enviar_plan_con_imagen` y `enviar_lugares_seguimiento`

---

## FLUJO CORREGIDO (Resumen)

### Plan Inicial:
1. Usuario selecciona intereses → `flujo_seleccion_intereses`
2. Sistema genera plan con Gemini → `flujo_generando_plan` → `generar_plan_personalizado()`
3. Sistema presenta plan → `flujo_plan_presentado` → `enviar_plan_con_imagen()`
4. **Para cada lugar**:
   - Genera QR si corresponde
   - Llama a `_enviar_informacion_y_qr()`:
     - Envía información (PARTE 1)
     - Si exitoso → envía QR (PARTE 2)
     - Si exitoso → guarda en `lugares_enviados_seguimiento`
5. Pasa a `SEGUIMIENTO`

### Seguimiento (Agregar más intereses):
1. Usuario presiona "Sí, agregar más"
2. Usuario selecciona nuevos intereses (texto o botón)
3. Se activa `modo_seguimiento = True` y `nuevos_intereses_seguimiento`
4. Sistema va a `flujo_generando_plan`
5. **Detecta bandera** → NO usa Gemini
6. Llama a `enviar_lugares_seguimiento()`:
   - Filtra usando `lugares_enviados_seguimiento` (solo lugares nuevos)
   - Para cada lugar nuevo:
     - Llama a `_enviar_informacion_y_qr()` (verificación de 2 partes)
     - Si exitoso → guarda en `lugares_enviados_seguimiento`
7. Envía mensaje de cierre

---

## PUNTOS CRÍTICOS CORREGIDOS

1. ✅ **QR solo se envía si la información se envió exitosamente** (función centralizada)
2. ✅ **Lugares se guardan SOLO después de enviarlos exitosamente** (no antes)
3. ✅ **Bandera `modo_seguimiento` se activa correctamente** (evita Gemini en seguimiento)
4. ✅ **Detección de "cultura" mejorada** (case-insensitive)
5. ✅ **`lugares_enviados_seguimiento` se mantiene sincronizado** (se actualiza en todos los flujos)

