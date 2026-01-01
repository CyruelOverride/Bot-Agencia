# RESUMEN: ARCHIVOS Y FUNCIÓN PRINCIPAL DE ENVÍO

## 📁 ARCHIVOS INVOLUCRADOS EN EL ENVÍO DE LUGARES Y QR

### 1. **`Services/PlanViajeService.py`** ⭐ ARCHIVO PRINCIPAL
   - **Función principal:** `_enviar_informacion_y_qr()` (línea ~78)
   - **Función que llama:** `enviar_plan_con_imagen()` (línea ~440)
   - **Función que llama:** `enviar_lugares_seguimiento()` (línea ~616)

### 2. **`Util/qr_helper.py`**
   - `obtener_ruta_qr()` - Obtiene/genera la ruta del archivo QR
   - `debe_enviar_qr()` - Verifica si debe tener QR

### 3. **`whatsapp_api.py`** (o similar)
   - `enviar_imagen_whatsapp()` - Envía imagen con caption
   - `enviar_mensaje_whatsapp()` - Envía mensaje de texto

### 4. **`Models/chat.py`**
   - `flujo_plan_presentado()` - Llama a `enviar_plan_con_imagen()`
   - `flujo_generando_plan()` - Llama a `enviar_lugares_seguimiento()`

---

## 🔧 FUNCIÓN PRINCIPAL: `_enviar_informacion_y_qr()`

**Archivo:** `Services/PlanViajeService.py`  
**Línea:** ~78  
**Tipo:** Método estático

**Esta función envía AMBAS cosas:**
1. **PARTE 1:** Información del lugar (imagen con caption o texto)
2. **PARTE 2:** Código QR (solo si la PARTE 1 fue exitosa)

**Código completo:**
```python
@staticmethod
def _enviar_informacion_y_qr(numero: str, excursion: Excursion, ruta_qr: Optional[str] = None) -> bool:
    """
    Envía la información del lugar y luego el QR si corresponde.
    Verificación de 2 partes:
    1. Primero envía la información del lugar
    2. Solo si la información se envió exitosamente, envía el QR
    """
    # PARTE 1: Enviar información
    # ... código de envío ...
    
    # PARTE 2: Solo si info_enviada_exitosamente == True, enviar QR
    # ... código de envío QR ...
    
    return info_enviada_exitosamente
```

**Dónde se llama:**
- Línea ~566 en `enviar_plan_con_imagen()`
- Línea ~720 en `enviar_lugares_seguimiento()`

---

## 🔍 PROBLEMA CON "CULTURA"

**Archivo:** `Models/chat.py`  
**Función:** `_detectar_intereses_texto()` (línea ~1050)

**El mapeo incluye "cultura" correctamente:**
- "cultura" → "cultura" ✅
- "4" → "cultura" ✅
- "d" → "cultura" ✅
- Y muchas variaciones más ✅

**Posible causa del problema:**
- La normalización con `str()` que agregamos podría estar afectando la comparación
- Necesito revisar si hay algún problema en la lógica de detección

