from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
import traceback
from Models.chat import Chat
from whatsapp_api import procesar_mensaje_recibido, WHATSAPP_PHONE_NUMBER_ID, extraer_nombre_del_webhook
from Services.UsuarioService import UsuarioService

app = FastAPI()
VERIFY_TOKEN = "Chacalitas2025"

@app.on_event("startup")
async def startup_event():
    # ============================================================
    # CÓDIGO DE BASE DE DATOS COMENTADO - NO HAY MÁS BDD
    # ============================================================
    # try:
    #     with engine.connect() as conn:
    #         result = conn.execute(text("""
    #             SELECT EXISTS (
    #                 SELECT FROM information_schema.tables 
    #                 WHERE table_schema = 'public' 
    #                 AND table_name = 'cliente'
    #             );
    #         """))
    #         tabla_existe = result.scalar()
    #     
    #     if not tabla_existe:
    #         print("🔄 Tablas no encontradas. Inicializando base de datos...")
    #         init_db()
    #         print("✅ Tablas creadas correctamente")
    #         
    #         print("🌱 Ejecutando seeding de datos iniciales...")
    #         try:
    #             seed_main()
    #         except Exception as e:
    #             print(f"⚠️ Error en seeding automático: {e}")
    #             print("💡 Puedes ejecutar el seeding manualmente visitando /seed-db")
    #     else:
    #         print("✅ Base de datos ya inicializada")
    #     
    #     print("🚀 Sistema de colas en memoria inicializado")
    #     
    # except Exception as e:
    #     print(f"⚠️ Error al verificar/inicializar base de datos: {e}")
    #     print("💡 Puedes inicializar manualmente visitando /init-db")
    print("🚀 Servidor iniciado (sin base de datos)")


@app.get("/")
async def root():
    return {
        "message": "WhatsApp Webhook Server funcionando",
        "phone_number_id": WHATSAPP_PHONE_NUMBER_ID,
        "endpoints": {
            "webhook": "/webhook",
            "health": "/health"
        },
    }


@app.get("/health")
async def health():
    return {"status": "ok"}


# ============================================================
# ENDPOINTS DE BASE DE DATOS COMENTADOS - NO HAY MÁS BDD
# ============================================================

# @app.get("/init-db")
# async def init_database():
#     """Endpoint para inicializar las tablas manualmente (si no se inicializaron automáticamente)."""
#     try:
#         init_db()
#         return {
#             "status": "success",
#             "message": "✅ Tablas creadas correctamente",
#             "tablas": [
#                 "categoria", "producto", "cliente", "repartidor",
#                 "chat", "mensaje", "pedido", "detalle_pedido"
#             ]
#         }
#     except Exception as e:
#         return {
#             "status": "error",
#             "message": f"❌ Error al inicializar: {str(e)}"
#         }


# @app.get("/seed-db")
# async def seed_database():
#     """Endpoint para poblar la base de datos con datos de prueba (categorías, productos, repartidores)."""
#     try:
#         seed_main()
#         return {
#             "status": "success",
#             "message": "✅ Seeding completado exitosamente",
#             "datos": {
#                 "categorias": 8,
#                 "productos": "32+ productos",
#                 "repartidores": 6
#             }
#         }
#     except Exception as e:
#         return {
#             "status": "error",
#             "message": f"❌ Error en seeding: {str(e)}"
#         }


@app.get("/webhook")
async def verify(request: Request):
    try:
        mode = request.query_params.get("hub.mode")
        token = request.query_params.get("hub.verify_token")
        challenge = request.query_params.get("hub.challenge")
        
        # Log para debugging
        print(f"🔍 Verificación webhook recibida:")
        print(f"   Mode: {mode}")
        print(f"   Token recibido: {token}")
        print(f"   Token esperado: {VERIFY_TOKEN}")
        print(f"   Challenge: {challenge}")
        print(f"   URL completa: {request.url}")
        
        # WhatsApp requiere que mode sea "subscribe" y el token coincida exactamente
        if mode == "subscribe" and token == VERIFY_TOKEN:
            if challenge:
                # Convertir challenge a string explícitamente y devolverlo sin formato adicional
                challenge_str = str(challenge)
                print(f"✅ Verificación exitosa, devolviendo challenge: {challenge_str}")
                # WhatsApp requiere que la respuesta sea exactamente el challenge como texto plano
                return PlainTextResponse(challenge_str, status_code=200)
            else:
                print("⚠️ Challenge vacío")
                return PlainTextResponse("Challenge requerido", status_code=400)
        
        print(f"❌ Verificación fallida - Mode: {mode}, Token válido: {token == VERIFY_TOKEN}")
        return PlainTextResponse("Token inválido", status_code=403)
    except Exception as e:
        print(f"❌ Error en verificación webhook: {e}")
        traceback.print_exc()
        return PlainTextResponse(f"Error: {str(e)}", status_code=500)


@app.post("/webhook")
async def receive(request: Request):
    try:
        data = await request.json()
        resultado = procesar_mensaje_recibido(data)

        if not resultado:
            return PlainTextResponse("EVENT_RECEIVED", status_code=200)

        numero, mensaje, tipo = resultado
        print(f"Mensaje recibido ({tipo}) de {numero}: {mensaje}")

        # Extraer nombre del contacto del webhook si está disponible
        nombre_contacto = extraer_nombre_del_webhook(data)
        if nombre_contacto:
            UsuarioService.actualizar_nombre(numero, nombre_contacto)
            print(f"Nombre extraído del webhook: {nombre_contacto}")

        # Obtener o crear usuario
        usuario = UsuarioService.obtener_o_crear_usuario(numero, nombre_contacto)
        
        id_chat = f"chat_{numero}"
        
        chat = Chat(
            id_chat=id_chat,
            id_cliente=usuario.telefono
        )

        if tipo in ("text", "interactive"):
            chat.handle_text(numero, mensaje)
        elif tipo == "location":
            chat.handle_location(numero, mensaje)
        else:
            chat.handle_text(numero, "Tipo de mensaje no soportado aún.")

        return PlainTextResponse("EVENT_RECEIVED", status_code=200)

    except Exception:
        traceback.print_exc()
        return PlainTextResponse("ERROR", status_code=500)