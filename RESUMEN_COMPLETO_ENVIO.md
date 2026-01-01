# RESUMEN COMPLETO: ARCHIVOS Y FUNCIÓN DE ENVÍO

## 📁 ARCHIVOS INVOLUCRADOS EN EL ENVÍO DE LUGARES Y QR

### ⭐ ARCHIVO PRINCIPAL: `Services/PlanViajeService.py`

#### Función que envía AMBAS cosas (información + QR):
**`_enviar_informacion_y_qr()`** - Línea 78

**Esta función:**
1. **PARTE 1** (líneas 100-178): Envía información del lugar
   - Intenta enviar imagen con caption
   - Si falla → fallback a texto
   - Si exitoso → `info_enviada_exitosamente = True`

2. **PARTE 2** (líneas 180-214): Envía QR
   - Solo si `info_enviada_exitosamente == True`
   - Sanitiza ruta del QR
   - Envía QR con caption
   - Si falla → loguea pero NO afecta el retorno

**Dónde se llama:**
- Línea ~566 en `enviar_plan_con_imagen()`
- Línea ~720 en `enviar_lugares_seguimiento()`

---

#### Función: `enviar_plan_con_imagen()` - Línea 440
- Envía resumen del plan (imagen con caption de Gemini)
- Para cada excursión:
  - Genera QR (`obtener_ruta_qr()`)
  - Llama a `_enviar_informacion_y_qr()`
  - Guarda en `UsuarioService` y `conversation_data`

#### Función: `enviar_lugares_seguimiento()` - Línea 616
- Filtra lugares ya enviados
- Para cada lugar nuevo:
  - Genera QR
  - Llama a `_enviar_informacion_y_qr()`
  - Guarda en `UsuarioService` y `conversation_data`

---

### Otros archivos:

1. **`Util/qr_helper.py`**
   - `obtener_ruta_qr(excursion_id)` - Obtiene/genera ruta del QR
   - `debe_enviar_qr(categoria)` - Verifica si debe tener QR

2. **`whatsapp_api.py`**
   - `enviar_imagen_whatsapp(numero, imagen_url, caption)`
   - `enviar_mensaje_whatsapp(numero, mensaje)`

3. **`Models/chat.py`**
   - `flujo_plan_presentado()` - Llama a `enviar_plan_con_imagen()`
   - `flujo_generando_plan()` - Llama a `enviar_lugares_seguimiento()`

---

## 🔧 FUNCIÓN PRINCIPAL COMPLETA

```python
# Services/PlanViajeService.py - Línea 78
@staticmethod
def _enviar_informacion_y_qr(numero: str, excursion: Excursion, ruta_qr: Optional[str] = None) -> bool:
    """
    Envía la información del lugar y luego el QR si corresponde.
    Verificación de 2 partes:
    1. Primero envía la información del lugar
    2. Solo si la información se envió exitosamente, envía el QR
    """
    # PARTE 1: Enviar información (líneas 100-178)
    # PARTE 2: Enviar QR (líneas 180-214)
    return info_enviada_exitosamente
```

---

## 🔍 PROBLEMA CON "CULTURA"

**Archivo:** `Models/chat.py`  
**Función:** `_detectar_intereses_texto()` - Línea 1071

**El mapeo está correcto:**
- "cultura" → "cultura" ✅
- "4" → "cultura" ✅
- "d" → "cultura" ✅
- Y muchas variaciones más ✅

**Posible problema:**
- La normalización con `str()` en línea 694 podría estar causando problemas
- `usuario.agregar_interes()` compara directamente sin normalizar (línea 32 de usuario.py)

**Revisar:**
- Si `_detectar_intereses_texto()` está retornando "cultura" correctamente
- Si `usuario.agregar_interes()` está comparando correctamente
- Si hay algún problema de normalización en la comparación

