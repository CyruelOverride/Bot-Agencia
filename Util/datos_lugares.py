"""
Datos hardcodeados de lugares/excursiones por ciudad.
Estructura: {ciudad: {categoria: [Excursion, ...]}}

NOTA: Los datos están hardcodeados en listas. A futuro se implementará BDD.
La ciudad por defecto es Canelones (a futuro será configurable por medio de BDD).
"""

from Models.excursion import Excursion

# Datos hardcodeados para Canelones, Uruguay
DATOS_LUGARES = {
    "Canelones": {
        "restaurantes": [
            Excursion(
                id="rest_001",
                ciudad="Canelones",
                categoria="restaurantes",
                nombre="Parrilla El Fogón",
                descripcion="Parrilla tradicional uruguaya, ambiente familiar y relajado. Especialidad en asado y chivito.",
                ubicacion="Centro de Canelones",
                tags=["local", "parrilla", "economico", "familiar"]
            ),
            Excursion(
                id="rest_002",
                ciudad="Canelones",
                categoria="restaurantes",
                nombre="La Casona",
                descripcion="Cocina casera y platos típicos. Ambiente acogedor, ideal para familias.",
                ubicacion="Zona Centro",
                tags=["local", "casero", "economico", "familiar"]
            ),
            Excursion(
                id="rest_003",
                ciudad="Canelones",
                categoria="restaurantes",
                nombre="Restaurante del Parque",
                descripcion="Vista al parque, especialidad en pescados y mariscos. Ambiente romántico ideal para parejas.",
                ubicacion="Frente al Parque Rodó",
                tags=["pescados", "romantico", "medio", "vista_parque"]
            ),
            Excursion(
                id="rest_004",
                ciudad="Canelones",
                categoria="restaurantes",
                nombre="Bistro Canelones",
                descripcion="Restaurante con cocina internacional y ambiente moderno. Ideal para ocasiones especiales.",
                ubicacion="Zona Centro",
                tags=["internacional", "premium", "romantico", "especial"]
            ),
            Excursion(
                id="rest_005",
                ciudad="Canelones",
                categoria="restaurantes",
                nombre="Veggie Life",
                descripcion="Opción vegetariana y vegana. Platos saludables y creativos con ingredientes frescos.",
                ubicacion="Centro de Canelones",
                tags=["vegetariano", "vegano", "saludable", "medio"]
            )
        ],
        "comercios": [
            Excursion(
                id="com_001",
                ciudad="Canelones",
                categoria="comercios",
                nombre="Shopping Canelones",
                descripcion="Centro comercial con tiendas de ropa, electrónica y servicios. Variedad de opciones.",
                ubicacion="Zona Centro",
                tags=["shopping", "ropa", "electronica", "variedad"]
            ),
            Excursion(
                id="com_002",
                ciudad="Canelones",
                categoria="comercios",
                nombre="Mercado Artesanal Municipal",
                descripcion="Artesanías locales, souvenirs y productos típicos uruguayos. Ideal para regalos y recuerdos.",
                ubicacion="Plaza Principal",
                tags=["artesanias", "souvenirs", "regalos", "local"]
            ),
            Excursion(
                id="com_003",
                ciudad="Canelones",
                categoria="comercios",
                nombre="Feria de los Sábados",
                descripcion="Feria al aire libre con productos locales, artesanías y comida. Sábados por la mañana.",
                ubicacion="Plaza Principal",
                tags=["feria", "artesanias", "local", "sabados"]
            )
        ],
        "recreacion": [
            Excursion(
                id="rec_001",
                ciudad="Canelones",
                categoria="recreacion",
                nombre="Parque Rodó",
                descripcion="Parque principal ideal para caminar, descansar y disfrutar de la naturaleza. Espacios verdes y juegos para niños.",
                ubicacion="Centro de Canelones",
                tags=["parque", "naturaleza", "familiar", "tranquilo"]
            ),
            Excursion(
                id="rec_002",
                ciudad="Canelones",
                categoria="recreacion",
                nombre="Rambla Costera",
                descripcion="Paseo costero recomendado al atardecer. Vista al río, ideal para caminar o andar en bicicleta.",
                ubicacion="Costanera",
                tags=["paseo", "rio", "atardecer", "activo"]
            ),
            Excursion(
                id="rec_003",
                ciudad="Canelones",
                categoria="recreacion",
                nombre="Playa Municipal",
                descripcion="Playa sobre el río. Ideal para días de calor, con servicios y seguridad. Espacio familiar.",
                ubicacion="Costanera",
                tags=["playa", "rio", "verano", "familiar"]
            ),
            Excursion(
                id="rec_004",
                ciudad="Canelones",
                categoria="recreacion",
                nombre="Club Deportivo Canelones",
                descripcion="Instalaciones deportivas con canchas, piscina y áreas recreativas. Ideal para actividades físicas.",
                ubicacion="Zona Sur",
                tags=["deportes", "piscina", "activo", "familiar"]
            )
        ],
        "cultura": [
            Excursion(
                id="cul_001",
                ciudad="Canelones",
                categoria="cultura",
                nombre="Museo Histórico de Canelones",
                descripcion="Museo que muestra la historia y evolución de la ciudad y la región. Interesante para toda la familia.",
                ubicacion="Centro de Canelones",
                tags=["museo", "historia", "cultura", "familiar"]
            ),
            Excursion(
                id="cul_002",
                ciudad="Canelones",
                categoria="cultura",
                nombre="Teatro Municipal",
                descripcion="Teatro histórico con programación cultural variada. Espectáculos y eventos culturales durante todo el año.",
                ubicacion="Centro de Canelones",
                tags=["teatro", "cultura", "espectaculos", "medio"]
            ),
            Excursion(
                id="cul_003",
                ciudad="Canelones",
                categoria="cultura",
                nombre="Plaza Principal",
                descripcion="Plaza principal de la ciudad con monumentos históricos. Centro histórico y punto de encuentro.",
                ubicacion="Centro de Canelones",
                tags=["plaza", "historia", "centro", "gratis"]
            ),
            Excursion(
                id="cul_004",
                ciudad="Canelones",
                categoria="cultura",
                nombre="Iglesia Catedral",
                descripcion="Catedral histórica de la ciudad. Arquitectura colonial, punto de interés religioso y cultural.",
                ubicacion="Centro de Canelones",
                tags=["iglesia", "historia", "arquitectura", "gratis"]
            )
        ],
        "compras": [
            Excursion(
                id="compr_001",
                ciudad="Canelones",
                categoria="compras",
                nombre="Centro Comercial Abierto",
                descripcion="Zona comercial con tiendas variadas, ideal para compras de ropa, calzado y accesorios.",
                ubicacion="Centro de Canelones",
                tags=["compras", "ropa", "accesorios", "economico"]
            ),
            Excursion(
                id="compr_002",
                ciudad="Canelones",
                categoria="compras",
                nombre="Tiendas de Regalos y Souvenirs",
                descripcion="Variedad de tiendas especializadas en souvenirs y regalos típicos uruguayos.",
                ubicacion="Zona Centro",
                tags=["regalos", "souvenirs", "local", "variedad"]
            )
        ]
    }
}

def obtener_lugares_por_ciudad(ciudad: str) -> dict:
    """Obtiene todos los lugares de una ciudad organizados por categoría"""
    return DATOS_LUGARES.get(ciudad, {})

def obtener_lugares_por_categoria(ciudad: str, categoria: str) -> list:
    """Obtiene lugares de una categoría específica en una ciudad"""
    lugares_ciudad = DATOS_LUGARES.get(ciudad, {})
    return lugares_ciudad.get(categoria, [])

def obtener_todas_las_categorias(ciudad: str) -> list:
    """Obtiene todas las categorías disponibles para una ciudad"""
    lugares_ciudad = DATOS_LUGARES.get(ciudad, {})
    return list(lugares_ciudad.keys())

def obtener_todas_las_ciudades() -> list:
    """Obtiene todas las ciudades disponibles"""
    return list(DATOS_LUGARES.keys())
