# VERIFICACIÓN: ¿Dónde se envía el QR?

## ✅ RESPUESTA: El QR NO se envía de forma independiente

El QR **solo** se envía desde **una función centralizada**: `_enviar_informacion_y_qr()` en `Services/PlanViajeService.py`.

---

## 📍 ÚNICO LUGAR DONDE SE ENVÍA QR (FLUJO NORMAL)

### `Services/PlanViajeService.py` - Línea 206

```206:206:Services/PlanViajeService.py
resultado_qr = enviar_imagen_whatsapp(numero, ruta_qr_sanitizada, caption_qr)
```

**Contexto completo:**
```188:236:Services/PlanViajeService.py
# PARTE 2: El QR solo si hay ruta y la parte 1 fue confirmada
if ruta_qr and os.path.exists(ruta_qr):
    # CORRECCIÓN RACE CONDITION: Aumentar delay con log de bloqueo
    print(f"⏳ [PAUSA] Bloqueando 6s para asegurar que INFO llegue antes que QR...")
    print(f"⏳ [PAUSA] Lugar: {excursion.nombre} (ID: {excursion.id})")
    time.sleep(6)
    
    # Sanitizar ruta del QR
    ruta_qr_sanitizada = PlanViajeService._sanitizar_ruta_qr(ruta_qr, excursion)
    
    if ruta_qr_sanitizada and os.path.exists(ruta_qr_sanitizada):
        caption_qr = f"📱 *Código QR - {excursion.nombre}*\n\nMuestra este QR a la hora de pagar para poder acceder al descuento."
        
        timestamp_qr = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"🎯 [PASO 2] Enviando QR para: {excursion.nombre} (ID: {excursion.id}) - {timestamp_qr}")
        print(f"🎯 [PASO 2] Ruta QR: {ruta_qr_sanitizada}")
        
        try:
            resultado_qr = enviar_imagen_whatsapp(numero, ruta_qr_sanitizada, caption_qr)
            if resultado_qr.get("success"):
                timestamp_qr_result = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"✅ [PASO 2] ÉXITO - {timestamp_qr_result} - QR enviado para: {excursion.nombre} (ID: {excursion.id})")
                # Pausa adicional después de confirmación
                time.sleep(3)
            else:
                timestamp_qr_result = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                error_qr = resultado_qr.get('error', 'Error desconocido')
                print(f"⚠️ [AVISO] QR de {excursion.nombre} (ID: {excursion.id}) falló, pero la info ya se envió. Error: {error_qr}")
                logger.warning(f"Error al enviar QR para {excursion.nombre} (información ya enviada): {error_qr}")
        except Exception as e:
            timestamp_qr_exception = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"⚠️ [AVISO] Excepción al enviar QR de {excursion.nombre} (ID: {excursion.id}), pero la info ya se envió. Error: {e}")
            logger.warning(f"Excepción al enviar QR para {excursion.nombre} (información ya enviada): {e}")
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
print(f"📤 [LOG ENVÍO] Información enviada: True")
print(f"📤 [LOG ENVÍO] QR enviado: {ruta_qr is not None and os.path.exists(ruta_qr) if ruta_qr else False}")
print(f"{'='*80}\n")

return True
```

**Condiciones para enviar QR:**
1. ✅ `ruta_qr` debe existir (no ser None)
2. ✅ `os.path.exists(ruta_qr)` debe ser True
3. ✅ La información del lugar debe haberse enviado exitosamente (PARTE 1)
4. ✅ Delay de 6 segundos después de enviar INFO
5. ✅ Ruta QR sanitizada y verificada

---

## 🔍 DÓNDE SE LLAMA `_enviar_informacion_y_qr()`

### 1. `enviar_plan_con_imagen()` - Línea 663

```630:663:Services/PlanViajeService.py
# Para cada lugar (excursión) de este interés, enviar un mensaje individual
for excursion in excursiones:
    print(f"  → Enviando lugar: {excursion.nombre}")
    # ... obtener ruta_qr ...
    
    # Usar función centralizada con verificación de 2 partes
    info_enviada_exitosamente = PlanViajeService._enviar_informacion_y_qr(numero, excursion, ruta_qr)
```

### 2. `enviar_lugares_seguimiento()` - Línea 849

```831:849:Services/PlanViajeService.py
for excursion in excursiones_cat:
    print(f"  → Enviando lugar: {excursion.nombre}")
    # ... obtener ruta_qr ...
    
    # Usar función centralizada con verificación de 2 partes
    info_enviada_exitosamente = PlanViajeService._enviar_informacion_y_qr(numero, excursion, ruta_qr)
```

---

## ⚠️ CÓDIGO DE TEST (NO INTERFIERE CON FLUJO NORMAL)

### `Models/chat.py` - Líneas 242-364

**Este código SOLO se ejecuta si el usuario escribe `#QR` o `#qr`:**

```242:242:Models/chat.py
if texto_lower == "#qr" or texto_strip == "#QR":
```

**Este código es para testing y NO se ejecuta en el flujo normal del bot.**

---

## ✅ CONCLUSIÓN

**El QR NO se envía de forma independiente.** 

El flujo es:
1. Se llama a `_enviar_informacion_y_qr()`
2. Esta función envía INFO primero (PARTE 1)
3. Si INFO es exitosa, espera 6 segundos
4. Luego envía QR (PARTE 2)

**No hay ningún otro lugar en el código que envíe QR de forma independiente en el flujo normal.**

---

## 🔍 SI VES QRs DUPLICADOS O INESPERADOS

Si estás viendo QRs que llegan de forma inesperada, revisa:

1. **Logs de `[PASO 2]`**: Cada QR enviado debe tener un log `🎯 [PASO 2] Enviando QR`
2. **Timestamps**: Verifica que el QR se envíe después de la INFO (6 segundos de diferencia)
3. **IDs de lugares**: Verifica que cada QR tenga el ID correcto del lugar
4. **Código de TEST**: Verifica que no se esté ejecutando el código de `#QR` accidentalmente

---

## 📊 LOGS ESPERADOS PARA CADA QR

```
🎯 [PASO 2] Enviando QR para: [Nombre] (ID: [ID]) - [Timestamp]
🎯 [PASO 2] Ruta QR: [ruta]
✅ [PASO 2] ÉXITO - [Timestamp] - QR enviado para: [Nombre] (ID: [ID])
```

Si ves estos logs, el QR se está enviando correctamente desde `_enviar_informacion_y_qr()`.

