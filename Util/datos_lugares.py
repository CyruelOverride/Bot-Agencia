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
                nombre="Parrillada La Rueda",
                descripcion="Situada en la Ruta 11, es un referente en cortes bovinos y platos italo-uruguayos, destacando su milanesa a la napolitana por su tamaño y sabor. Su relación calidad-precio es de las mejores del departamento, con un servicio atento y un ambiente acogedor.",
                ubicacion="Ruta 11 km 97.500",
                tags=["parrilla", "italo-uruguayo", "economico", "familiar"],
                imagen_url="https://static.wixstatic.com/media/482a1d_5945b5509e1941509d023545b56b8e28~mv2.jpg/v1/fill/w_720,h_900,al_c,q_85/482a1d_5945b5509e1941509d023545b56b8e28~mv2.jpg"
            ),
            Excursion(
                id="rest_002",
                ciudad="Canelones",
                categoria="restaurantes",
                nombre="El Rancho",
                descripcion="Establecimiento polivalente ideal para eventos o almuerzos familiares, conocido por su buffet variado y su excelente parrilla en un entorno natural a las afueras de la ciudad.",
                ubicacion="Rivera km 47",
                tags=["parrilla", "buffet", "eventos", "familiar", "medio"],
                imagen_url="https://media-cdn.tripadvisor.com/media/photo-s/02/8f/1a/a4/el-rancho.jpg"
            ),
            Excursion(
                id="rest_003",
                ciudad="Canelones",
                categoria="restaurantes",
                nombre="Parador Chivitos",
                descripcion="Especializado en el plato nacional uruguayo, ofrece chivitos abundantes con ingredientes frescos y lomo de primera calidad. Es una opción accesible para el turismo de paso con horarios extendidos.",
                ubicacion="FPG6+7FP, Canelones",
                tags=["chivitos", "rapido", "economico", "local"],
                imagen_url=None
            ),
            Excursion(
                id="rest_004",
                ciudad="Canelones",
                categoria="restaurantes",
                nombre="Lo Del Vasco",
                descripcion="Representa la cocina casera y artesanal por excelencia en la capital canaria. Con una política de precios muy competitiva, es el lugar preferido por locales para una comida rápida pero de alta calidad.",
                ubicacion="Luis A. de Herrera, Canelones",
                tags=["casero", "artesanal", "economico", "local", "rapido"],
                imagen_url=None
            ),
            Excursion(
                id="rest_005",
                ciudad="Canelones",
                categoria="restaurantes",
                nombre="Santoral Restaurante y Posada",
                descripcion="En Atlántida, ofrece una propuesta cosmopolita frente a la Rambla Mansa. Destaca por su política de no propinas, su dulcería artesanal y una carta que fusiona influencias portuguesas, africanas y mexicanas.",
                ubicacion="Rambla Mansa, Atlántida",
                tags=["internacional", "premium", "cosmopolita", "romantico"],
                imagen_url="https://media-cdn.tripadvisor.com/media/photo-s/0e/d1/3a/50/fachada-de-la-casa-ano.jpg"
            )
        ],
        "comercios": [
            Excursion(
                id="com_001",
                ciudad="Canelones",
                categoria="comercios",
                nombre="Otherside",
                descripcion="Retail textil con prendas casuales y contemporáneas. Ideal para ropa urbana de temporada.",
                ubicacion="Treinta y Tres 598, Canelones",
                tags=["ropa", "urbana", "casual", "contemporaneo"],
                imagen_url=None
            ),
            Excursion(
                id="com_002",
                ciudad="Canelones",
                categoria="comercios",
                nombre="Manos del Uruguay",
                descripcion="Cooperativas de mujeres rurales que producen lana, cuero y joyería de exportación bajo comercio justo.",
                ubicacion="Costa Urbana Shopping",
                tags=["artesanias", "lana", "cuero", "joyeria", "comercio_justo"],
                imagen_url=None
            ),
            Excursion(
                id="com_003",
                ciudad="Canelones",
                categoria="comercios",
                nombre="Feria Artesanal de Atlántida",
                descripcion="Paseo clásico para comprar souvenirs de cerámica, cuero, lana y mates trabajados por artesanos locales.",
                ubicacion="Centro de Atlántida",
                tags=["feria", "artesanias", "souvenirs", "local", "ceramica"],
                imagen_url=None
            )
        ],
        "recreacion": [
            Excursion(
                id="rec_001",
                ciudad="Canelones",
                categoria="recreacion",
                nombre="Parque Roosevelt",
                descripcion="Pulmón verde con tren eléctrico y deportes. Ideal para actividades al aire libre y recreación familiar.",
                ubicacion="Av. Giannattasio km 21",
                tags=["parque", "naturaleza", "deportes", "familiar", "tren"],
                imagen_url=None
            ),
            Excursion(
                id="rec_002",
                ciudad="Canelones",
                categoria="recreacion",
                nombre="Quinta Capurro",
                descripcion="Jardín histórico con especies exóticas del siglo XIX. Espacio verde con valor patrimonial y botánico.",
                ubicacion="Bv. Federico Capurro 555",
                tags=["jardin", "historico", "patrimonio", "botanico", "tranquilo"],
                imagen_url=None
            )
        ],
        "cultura": [
            Excursion(
                id="cul_001",
                ciudad="Canelones",
                categoria="cultura",
                nombre="Iglesia Cristo Obrero",
                descripcion="Patrimonio UNESCO, obra de Eladio Dieste. Arquitectura única en ladrillo visto, referente de la arquitectura moderna uruguaya.",
                ubicacion="Ruta 11 km 164",
                tags=["iglesia", "unesco", "arquitectura", "dieste", "patrimonio", "gratis"],
                imagen_url=None
            ),
            Excursion(
                id="cul_002",
                ciudad="Canelones",
                categoria="cultura",
                nombre="Museo de la Uva",
                descripcion="Museo que muestra la historia de la vitivinicultura uruguaya. Exposiciones sobre el cultivo de la vid y la producción de vino en la región.",
                ubicacion="Ruta 48 km 18.500",
                tags=["museo", "vino", "historia", "vitivinicultura", "gratis"],
                imagen_url=None
            )
        ],
        "compras": [
            Excursion(
                id="compr_001",
                ciudad="Canelones",
                categoria="compras",
                nombre="Costa Urbana Shopping",
                descripcion="Centro comercial con cine, tiendas y Centro Cívico Público. Oferta variada de compras, entretenimiento y servicios.",
                ubicacion="Av. Giannattasio km 21",
                tags=["shopping", "cine", "tiendas", "entretenimiento", "variedad"],
                imagen_url=None
            ),
            Excursion(
                id="compr_002",
                ciudad="Canelones",
                categoria="compras",
                nombre="Las Piedras Shopping",
                descripcion="Centro comercial con tiendas de moda, cines y gastronomía. Oferta completa para compras y entretenimiento.",
                ubicacion="Bulevar del Bicentenario",
                tags=["shopping", "moda", "cine", "gastronomia", "variedad"],
                imagen_url=None
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
