# ARCHIVOS Y FUNCIONES INVOLUCRADAS EN EL ENVÍO DE LUGARES Y QR

## ARCHIVOS PRINCIPALES

### 1. `Services/PlanViajeService.py`
**Archivo principal que contiene la lógica de envío**

#### Función principal: `_enviar_informacion_y_qr()`
**Ubicación:** Línea ~78
**Descripción:** Función centralizada que envía información del lugar y luego el QR (verificación de 2 partes)

```python
@staticmethod
def _enviar_informacion_y_qr(numero: str, excursion: Excursion, ruta_qr: Optional[str] = None) -> bool:
    """
    Envía la información del lugar y luego el QR si corresponde.
    Verificación de 2 partes:
    1. Primero envía la información del lugar
    2. Solo si la información se envió exitosamente, envía el QR
    """
```

**Flujo:**
1. **PARTE 1:** Intenta enviar información del lugar (imagen con caption o texto)
2. Si exitoso → `info_enviada_exitosamente = True`
3. **PARTE 2:** Solo si `info_enviada_exitosamente == True` y existe `ruta_qr`, envía el QR
4. Retorna `True` si la información se envió (independientemente del QR)

**Dependencias:**
- `whatsapp_api.enviar_imagen_whatsapp()` - Para enviar imágenes
- `whatsapp_api.enviar_mensaje_whatsapp()` - Para enviar texto
- `_sanitizar_ruta_qr()` - Para manejar acentos en rutas de QR

---

#### Función: `enviar_plan_con_imagen()`
**Ubicación:** Línea ~440
**Descripción:** Envía el plan completo (resumen + lugares individuales)

**Flujo:**
1. Envía imagen con resumen del plan (generado por Gemini)
2. Para cada excursión del plan:
   - Genera QR si corresponde (`obtener_ruta_qr()`)
   - Llama a `_enviar_informacion_y_qr()` para enviar información + QR
   - Si exitoso → guarda en `UsuarioService` y `conversation_data`

**Llamadas a `_enviar_informacion_y_qr()`:**
- Línea ~566: `info_enviada_exitosamente = PlanViajeService._enviar_informacion_y_qr(numero, excursion, ruta_qr)`

---

#### Función: `enviar_lugares_seguimiento()`
**Ubicación:** Línea ~616
**Descripción:** Envía lugares nuevos en modo seguimiento (sin usar Gemini)

**Flujo:**
1. Filtra lugares ya enviados usando `lugares_enviados_seguimiento`
2. Para cada lugar nuevo:
   - Genera QR si corresponde
   - Llama a `_enviar_informacion_y_qr()` para enviar información + QR
   - Si exitoso → guarda en `UsuarioService` y `conversation_data`

**Llamadas a `_enviar_informacion_y_qr()`:**
- Línea ~720: `info_enviada_exitosamente = PlanViajeService._enviar_informacion_y_qr(numero, excursion, ruta_qr)`

---

### 2. `Util/qr_helper.py`
**Archivo que maneja la generación y obtención de QRs**

#### Funciones principales:
- `obtener_ruta_qr(excursion_id: str)` - Obtiene/genera la ruta del archivo QR
- `debe_enviar_qr(categoria: str)` - Verifica si la categoría debe tener QR (restaurantes/comercios)

---

### 3. `whatsapp_api.py` (o similar)
**Archivo que contiene las funciones de envío a WhatsApp**

#### Funciones utilizadas:
- `enviar_imagen_whatsapp(numero, imagen_url, caption)` - Envía imagen con caption
- `enviar_mensaje_whatsapp(numero, mensaje)` - Envía mensaje de texto

---

### 4. `Models/chat.py`
**Archivo que orquesta el flujo de conversación**

#### Funciones que llaman a los métodos de envío:
- `flujo_plan_presentado()` (línea ~1391):
  - Llama a `PlanViajeService.enviar_plan_con_imagen(numero, plan, chat=self)`
  
- `flujo_generando_plan()` (línea ~1308):
  - Si modo seguimiento → llama a `PlanViajeService.enviar_lugares_seguimiento(self, numero, usuario, nuevos_intereses)`
  - Si modo normal → genera plan y pasa a `flujo_plan_presentado()`

---

## FLUJO COMPLETO DE ENVÍO

### Flujo Normal (Plan Inicial):
```
Models/chat.py
  └─ flujo_plan_presentado()
      └─ PlanViajeService.enviar_plan_con_imagen()
          ├─ Envía resumen del plan (imagen con caption)
          └─ Para cada excursión:
              ├─ obtener_ruta_qr() [Util/qr_helper.py]
              └─ _enviar_informacion_y_qr()
                  ├─ PARTE 1: enviar_imagen_whatsapp() o enviar_mensaje_whatsapp() [whatsapp_api.py]
                  └─ PARTE 2: enviar_imagen_whatsapp() [whatsapp_api.py] (solo si PARTE 1 exitosa)
```

### Flujo Seguimiento (Agregar más intereses):
```
Models/chat.py
  └─ flujo_generando_plan()
      └─ PlanViajeService.enviar_lugares_seguimiento()
          └─ Para cada lugar nuevo:
              ├─ obtener_ruta_qr() [Util/qr_helper.py]
              └─ _enviar_informacion_y_qr()
                  ├─ PARTE 1: enviar_imagen_whatsapp() o enviar_mensaje_whatsapp() [whatsapp_api.py]
                  └─ PARTE 2: enviar_imagen_whatsapp() [whatsapp_api.py] (solo si PARTE 1 exitosa)
```

---

## FUNCIÓN PRINCIPAL: `_enviar_informacion_y_qr()`

**Archivo:** `Services/PlanViajeService.py`
**Línea:** ~78
**Tipo:** Método estático de la clase `PlanViajeService`

**Parámetros:**
- `numero: str` - Número de teléfono del usuario
- `excursion: Excursion` - Objeto Excursion con la información del lugar
- `ruta_qr: Optional[str]` - Ruta al archivo QR (opcional)

**Retorna:**
- `bool` - `True` si la información se envió exitosamente, `False` en caso contrario

**Lógica:**
1. **PARTE 1 - Envío de información:**
   - Si `excursion.imagen_url` existe:
     - Intenta enviar imagen con caption (incluye nombre, descripción, ubicación)
     - Si falla → fallback a texto
   - Si no hay imagen:
     - Envía mensaje de texto
   - Si exitoso → `info_enviada_exitosamente = True`

2. **PARTE 2 - Envío de QR:**
   - Solo si `info_enviada_exitosamente == True` y `ruta_qr` existe:
     - Sanitiza ruta del QR (`_sanitizar_ruta_qr()`)
     - Verifica que el archivo existe
     - Envía QR con caption
     - Si falla → loguea error pero NO afecta el retorno

**Características:**
- ✅ Verificación de 2 partes (información primero, QR después)
- ✅ Manejo de acentos en rutas de QR
- ✅ Fallback de imagen a texto
- ✅ No lanza excepciones si el QR falla (la información ya se envió)
- ✅ Retorna `True` si la información se envió, independientemente del QR

---

## PROBLEMA CON "CULTURA"

**Archivo:** `Models/chat.py`
**Función:** `_detectar_intereses_texto()` (línea ~1050)

**Mapeo de "cultura" (línea ~1105-1119):**
```python
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
```

**Lógica de detección (línea ~1123-1138):**
```python
for palabra in palabras:
    palabra_limpia = palabra.strip().lower()
    # Verificar coincidencia exacta primero
    if palabra_limpia in intereses_map:
        interes = intereses_map[palabra_limpia]
        if interes not in intereses_detectados:
            intereses_detectados.append(interes)
            print(f"🔍 [DETECTAR] Interés detectado por coincidencia exacta: '{palabra_limpia}' -> '{interes}'")
    else:
        # Buscar coincidencias parciales
        if len(palabra_limpia) > 2:
            for key, interes in intereses_map.items():
                if key.lower() in palabra_limpia or palabra_limpia in key.lower():
                    if interes not in intereses_detectados:
                        intereses_detectados.append(interes)
                        print(f"🔍 [DETECTAR] Interés detectado por coincidencia parcial: '{palabra_limpia}' contiene '{key}' -> '{interes}'")
                    break
```

**Posible problema:** La normalización con `deepcopy` y `str()` podría estar afectando la comparación. Necesito revisar si hay algún problema en la normalización.

