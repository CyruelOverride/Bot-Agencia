"""
Datos hardcodeados de lugares/excursiones por ciudad.
Estructura: {ciudad: {categoria: [Excursion, ...]}}

NOTA: Los datos están hardcodeados en listas. A futuro se implementará BDD.
La ciudad por defecto es Colonia (a futuro será configurable por medio de BDD).
"""

from Models.excursion import Excursion

# Datos hardcodeados para Colonia, Uruguay
DATOS_LUGARES = {
    "Colonia": {
        "restaurantes": [
            Excursion(
                id="rest_001",
                ciudad="Colonia",
                categoria="restaurantes",
                nombre="El Buen Suspiro",
                descripcion="Situado en la icónica Calle de los Suspiros, este local funciona en una construcción portuguesa del siglo XVIII que mantiene sus paredes de piedra y techos de madera originales. Es famoso por ofrecer una experiencia íntima donde se pueden degustar los mejores quesos de la región, fiambres artesanales y una selección premium de vinos uruguayos. Es el lugar ideal para una picada romántica o un brindis en un entorno que transporta al pasado colonial.\n\nHorario: Lunes a domingo de 11:00 a 20:00 hs.",
                ubicacion="https://www.google.com/maps/search/El+Buen+Suspiro+Colonia",
                tags=["quesos", "vinos", "romantico", "historico", "premium"],
                imagen_url="https://media-cdn.tripadvisor.com/media/photo-s/0e/d1/3a/50/fachada-de-la-casa-ano.jpg"
            ),
            Excursion(
                id="rest_002",
                ciudad="Colonia",
                categoria="restaurantes",
                nombre="Charco Bistró",
                descripcion="Este restaurante de autor se encuentra dentro de un hotel boutique ubicado en la faja costera del casco histórico. Se destaca por su diseño minimalista y elegante con una terraza que ofrece vistas espectaculares al Río de la Plata. Su propuesta culinaria es sofisticada, incluyendo mariscos frescos, pulpo a la parrilla, carnes de exportación y una pastelería de origen seleccionada, siendo una parada obligatoria para quienes buscan alta cocina frente al agua.\n\nHorario: Todos los días de 08:00 a 23:00 hs.",
                ubicacion="https://www.google.com/maps/search/Charco+Bistro+Colonia",
                tags=["alta_cocina", "mariscos", "premium", "vista_rio", "elegante"],
                imagen_url="https://media-cdn.tripadvisor.com/media/photo-s/0f/39/57/29/terrace.jpg"
            ),
            Excursion(
                id="rest_003",
                ciudad="Colonia",
                categoria="restaurantes",
                nombre="La Bodeguita",
                descripcion="Ubicada sobre la antigua muralla defensiva de la ciudad, esta pizzería y restaurante es reconocida por poseer una de las mejores terrazas para contemplar el atardecer. Su especialidad son las pizzas cocinadas en horno de barro, aunque también ofrecen chivitos uruguayos y pastas en un ambiente relajado y bohemio que suele llenarse al caer el sol.\n\nHorario: Todos los días a partir de las 20:00 hs.",
                ubicacion="https://www.google.com/maps/search/La+Bodeguita+Colonia",
                tags=["pizza", "horno_barro", "atardecer", "bohemio", "terraza"],
                imagen_url="https://th.bing.com/th/id/R.fd97452e324b98f82067527e105c3cae?rik=iP76bvNh%2fnrOhQ&pid=ImgRaw&r=0"
            ),
        ],
        "comercios": [
            Excursion(
                id="com_001",
                ciudad="Colonia",
                categoria="comercios",
                nombre="Manos del Uruguay",
                descripcion="Cooperativa nacional sin fines de lucro integrada a la Organización Mundial del Comercio Justo. Ofrece prendas de lana tejidas a mano de alta gama, accesorios de cuero, mantas de diseño y joyería artesanal de exportación.\n\nHorario: Lun-Dom 10:00-19:00 hs.",
                ubicacion="https://www.google.com/maps/search/Manos+del+Uruguay+Colonia",
                tags=["artesanias", "lana", "cuero", "joyeria", "comercio_justo", "premium"],
                imagen_url=None
            ),
            Excursion(
                id="com_002",
                ciudad="Colonia",
                categoria="comercios",
                nombre="Mercado Artesanal",
                descripcion="Espacio cultural ubicado en un antiguo galpón ferroviario recuperado cerca del puerto. Ofrece cerámica esmaltada, joyería de autor, textiles regionales, objetos de madera y vitrofusión realizados por artistas locales.\n\nHorario: Jue-Lun 10:00-20:00 hs.",
                ubicacion="https://www.google.com/maps/search/Mercado+Artesanal+Colonia",
                tags=["artesanias", "ceramica", "joyeria", "textiles", "cultural", "local"],
                imagen_url=None
            ),
            Excursion(
                id="com_003",
                ciudad="Colonia",
                categoria="comercios",
                nombre="Feria de Emprendedores",
                descripcion="Feria tradicional al aire libre donde productores de todo el departamento exhiben su trabajo. Se pueden encontrar dulces regionales, manualidades, antigüedades, mates trabajados y piezas únicas de decoración criolla.\n\nHorario: Domingos 07:00-14:00 hs.",
                ubicacion="https://www.google.com/maps/search/Feria+Productores+Colonia",
                tags=["feria", "artesanias", "dulces", "antiguedades", "decoracion", "tradicional"],
                imagen_url=None
            )
        ],
        "recreacion": [
            Excursion(
                id="rec_001",
                ciudad="Colonia",
                categoria="recreacion",
                nombre="Rambla de las Américas",
                descripcion="Es el paseo marítimo más extenso de la ciudad, con más de 7 kilómetros que bordean toda la bahía. Es el lugar preferido por turistas y locales para caminar, andar en bicicleta o simplemente sentarse a tomar mate mientras cae el sol. Al inicio del recorrido se encuentra el famoso cartel de letras de 'COLONIA', punto obligatorio para fotografías.\n\nHorario: Abierto las 24 hs.",
                ubicacion="https://www.google.com/maps/search/Rambla+Colonia+Sacramento",
                tags=["paseo", "maritimo", "naturaleza", "fotografia", "familiar", "gratis"],
                imagen_url="https://tse2.mm.bing.net/th/id/OIP.gq7cBke5qj6EDObvwUxwbwHaFh?cb=ucfimg2&ucfimg=1&rs=1&pid=ImgDetMain&o=7&rm=3"
            ),
            Excursion(
                id="rec_002",
                ciudad="Colonia",
                categoria="recreacion",
                nombre="Playa Ferrando",
                descripcion="Ubicada a pocos minutos del centro, es considerada la playa más linda y valorada de la ciudad. Se encuentra rodeada por un bosque de pinos y eucaliptos que proporcionan sombra natural, ideal para pasar el día en familia haciendo picnic. Sus arenas son finas y doradas, con aguas mansas que permiten un baño seguro en el río.\n\nHorario: Abierto las 24 hs.",
                ubicacion="https://www.google.com/maps/search/Playa+Ferrando+Colonia",
                tags=["playa", "naturaleza", "familiar", "picnic", "bosque", "gratis"],
                imagen_url="https://th.bing.com/th/id/R.4796de3daafd59c21249428e9da345e3?rik=7ZwfeqS9p1i%2blA&pid=ImgRaw&r=0"
            )
        ],
        "cultura": [
            Excursion(
                id="cul_001",
                ciudad="Colonia",
                categoria="cultura",
                nombre="Plaza de Toros Real de San Carlos",
                descripcion="Inaugurada en 1910 y recientemente restaurada, es hoy el mayor ícono cultural del departamento. Este imponente estadio de estilo neomudéjar ya no realiza corridas de toros, sino que funciona como un centro de espectáculos y museo taurino donde se puede recorrer su impactante arquitectura circular.\n\nCosto: Pago ($150 - $200 UYU).\nHorario: Lun-Dom 10:00-18:30 hs (Sábados hasta las 19:00).",
                ubicacion="https://www.google.com/maps/search/Plaza+de+Toros+Colonia",
                tags=["museo", "arquitectura", "historico", "espectaculos", "neomudejar"],
                imagen_url="https://www.civitatis.com/f/uruguay/colonia-del-sacramento/galeria/fachada-plaza-toros-real-san-carlos.jpg"
            ),
            Excursion(
                id="cul_002",
                ciudad="Colonia",
                categoria="cultura",
                nombre="Bastión del Carmen",
                descripcion="Este complejo cultural funciona en un antiguo fuerte militar y posteriormente fue fábrica. Actualmente es el epicentro de la movida cultural de Colonia, albergando salas de teatro, exposiciones de arte y música en vivo. Su patio trasero cuenta con un jardín de esculturas frente al río que es uno de los rincones más tranquilos y bellos de la ciudad.\n\nCosto: Entrada libre para el predio y jardines.\nHorario: Todos los días de 10:00 a 18:00 hs (dependiendo de funciones).",
                ubicacion="https://www.google.com/maps/search/Bastion+del+Carmen+Colonia",
                tags=["teatro", "arte", "musica", "jardin", "esculturas", "gratis", "cultural"],
                imagen_url="https://th.bing.com/th/id/R.ac549ad43f254f69a12695c3c7b387f7?rik=oXipcCMAOBqJlg&pid=ImgRaw&r=0"
            )
        ],
        "compras": [
            Excursion(
                id="compr_001",
                ciudad="Colonia",
                categoria="compras",
                nombre="Colonia Shopping",
                descripcion="El centro comercial cerrado más importante de la ciudad. Cuenta con más de cien marcas nacionales e internacionales, salas de cine, un gran supermercado (Ta-Ta) y una plaza de comidas variada.\n\nHorario: Lun-Dom 10:00-22:00 hs.",
                ubicacion="https://www.google.com/maps/search/Colonia+Shopping",
                tags=["shopping", "marcas", "cine", "supermercado", "comida", "variedad"],
                imagen_url=None
            ),
            Excursion(
                id="compr_002",
                ciudad="Colonia",
                categoria="compras",
                nombre="Av. General Flores",
                descripcion="Es el 'shopping a cielo abierto' y la arteria principal de la ciudad. Concentra las mayores tiendas de ropa, zapaterías, bancos y farmacias, además de ser el eje central donde se desarrolla la vida social de Colonia.\n\nHorario: Variable (aprox. 10:00-19:00 hs).",
                ubicacion="https://www.google.com/maps/search/Avenida+General+Flores+Colonia",
                tags=["avenida", "tiendas", "ropa", "zapatos", "bancos", "social"],
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
