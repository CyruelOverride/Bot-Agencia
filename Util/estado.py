"""
Variables locales para estado de sesión.
No se persisten en BD, son temporales por sesión.
"""

# Estados del bot de viaje
ESTADOS_BOT = {
    "INICIO": "INICIO",
    "SELECCION_INTERESES": "SELECCION_INTERESES",
    "ARMANDO_PERFIL": "ARMANDO_PERFIL",
    "GENERANDO_PLAN": "GENERANDO_PLAN",
    "PLAN_PRESENTADO": "PLAN_PRESENTADO",
    "SEGUIMIENTO": "SEGUIMIENTO"
}

# ESTADO: reemplaza SESSION - estado temporal de navegación (no se persiste en BD)
ESTADO = {}

def get_estado(numero):
    """Obtiene el estado de navegación del usuario."""
    return ESTADO.setdefault(numero, {
        "estado_bot": ESTADOS_BOT["INICIO"],  # Estado principal del bot de viaje
        "waiting_for": None,  # Función esperada para próximo mensaje
        "context_data": {},  # Datos de contexto para la función esperada
        "pregunta_actual": None,  # Campo del perfil que se está preguntando
        "intereses_seleccionados": []  # Intereses seleccionados por el usuario
    })

def reset_estado(numero):
    """Resetea el estado de navegación del usuario."""
    if numero in ESTADO:
        ESTADO[numero] = {
            "estado_bot": ESTADOS_BOT["INICIO"],
            "waiting_for": None,
            "context_data": {},
            "pregunta_actual": None,
            "intereses_seleccionados": []
        }

def get_estado_bot(numero):
    """Obtiene el estado actual del bot para un usuario."""
    estado = get_estado(numero)
    return estado.get("estado_bot", ESTADOS_BOT["INICIO"])

def set_estado_bot(numero, estado_bot: str):
    """Establece el estado del bot para un usuario."""
    estado = get_estado(numero)
    estado["estado_bot"] = estado_bot

def get_intereses_seleccionados(numero):
    """Obtiene los intereses seleccionados por el usuario."""
    estado = get_estado(numero)
    return estado.get("intereses_seleccionados", [])

def set_intereses_seleccionados(numero, intereses: list):
    """Establece los intereses seleccionados por el usuario."""
    estado = get_estado(numero)
    estado["intereses_seleccionados"] = intereses

def get_pregunta_actual(numero):
    """Obtiene la pregunta actual que se está haciendo al usuario."""
    estado = get_estado(numero)
    return estado.get("pregunta_actual")

def set_pregunta_actual(numero, pregunta: str):
    """Establece la pregunta actual que se está haciendo al usuario."""
    estado = get_estado(numero)
    estado["pregunta_actual"] = pregunta

def clear_pregunta_actual(numero):
    """Limpia la pregunta actual."""
    estado = get_estado(numero)
    estado["pregunta_actual"] = None

def get_waiting_for(numero):
    """Obtiene la función que está esperando respuesta del usuario."""
    estado = get_estado(numero)
    return estado.get("waiting_for")

def set_waiting_for(numero, func_name, context_data=None):
    """Establece la función esperada para próximo mensaje del usuario."""
    estado = get_estado(numero)
    estado["waiting_for"] = func_name
    estado["context_data"] = context_data or {}

def clear_waiting_for(numero):
    """Limpia la función esperada."""
    estado = get_estado(numero)
    estado["waiting_for"] = None
    estado["context_data"] = {}

# Mantener funciones de carrito para compatibilidad (aunque no se usen en el bot de viaje)
CARRITO = {}

def get_cart(numero):
    """Obtiene el carrito del usuario (legacy - no usado en bot de viaje)."""
    return CARRITO.setdefault(numero, {})

def clear_cart(numero):
    """Limpia el carrito del usuario (legacy - no usado en bot de viaje)."""
    if numero in CARRITO:
        del CARRITO[numero]

