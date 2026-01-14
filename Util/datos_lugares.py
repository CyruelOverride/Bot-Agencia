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
                tags=["mañana", "tarde", "noche", "quesos", "vinos", "romantico", "historico", "premium"],
                imagenes_url=[
                    "https://media-cdn.tripadvisor.com/media/photo-s/0e/d1/3a/50/fachada-de-la-casa-ano.jpg",
                    "https://tse2.mm.bing.net/th/id/OIP.dQPA01pCW5z2QsTAWvpPmAHaEK?rs=1&pid=ImgDetMain&o=7&rm=3"
                ]
            ),
            Excursion(
                id="rest_002",
                ciudad="Colonia",
                categoria="restaurantes",
                nombre="Charco Bistró",
                descripcion="Este restaurante de autor se encuentra dentro de un hotel boutique ubicado en la faja costera del casco histórico. Se destaca por su diseño minimalista y elegante con una terraza que ofrece vistas espectaculares al Río de la Plata. Su propuesta culinaria es sofisticada, incluyendo mariscos frescos, pulpo a la parrilla, carnes de exportación y una pastelería de origen seleccionada, siendo una parada obligatoria para quienes buscan alta cocina frente al agua.\n\nHorario: Todos los días de 08:00 a 23:00 hs.",
                ubicacion="https://www.google.com/maps/search/Charco+Bistro+Colonia",
                tags=["mañana","tarde","noche", "alta_cocina", "mariscos", "premium", "vista_rio", "elegante"],
                imagenes_url=[
                    "https://media-cdn.tripadvisor.com/media/photo-s/0f/39/57/29/terrace.jpg",
                    "https://img.hellofresh.com/w_3840,q_auto,f_auto,c_fill,fl_lossy/hellofresh_website/es/cms/SEO/recipes/gourmet/entrecot-de-ternera.jpeg"
                ]
            ),
            Excursion(
                id="rest_003",
                ciudad="Colonia",
                categoria="restaurantes",
                nombre="La Bodeguita",
                descripcion="Ubicada sobre la antigua muralla defensiva de la ciudad, esta pizzería y restaurante es reconocida por poseer una de las mejores terrazas para contemplar el atardecer. Su especialidad son las pizzas cocinadas en horno de barro, aunque también ofrecen chivitos uruguayos y pastas en un ambiente relajado y bohemio que suele llenarse al caer el sol.\n\nHorario: Todos los días a partir de las 20:00 hs.",
                ubicacion="https://www.google.com/maps/search/La+Bodeguita+Colonia",
                tags=["noche", "pizza", "horno_barro", "atardecer", "bohemio", "terraza"],
                imagenes_url=[
                    "https://th.bing.com/th/id/R.fd97452e324b98f82067527e105c3cae?rik=iP76bvNh%2fnrOhQ&pid=ImgRaw&r=0",
                    "https://tse3.mm.bing.net/th/id/OIP.pbrxeUZsbRcWg30Y95bscwHaFj?rs=1&pid=ImgDetMain&o=7&rm=3",
                ]
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
                tags=["tarde","noche", "artesanias", "lana", "cuero", "joyeria", "comercio_justo", "premium"],
                imagenes_url=[
                    "https://tse1.mm.bing.net/th/id/OIP.jHoP55C9sIXPDXWUeJjHPgHaEO?rs=1&pid=ImgDetMain&o=7&rm=3",
                    "https://cdn.shopify.com/s/files/1/0591/9096/8528/files/PU02190_Joyas_de_Acero_Uruguay_Pulsera_Acero_Dorado.jpg?v=1682552381"
                ]
            ),
            Excursion(
                id="com_002",
                ciudad="Colonia",
                categoria="comercios",
                nombre="Mercado Artesanal",
                descripcion="Espacio cultural ubicado en un antiguo galpón ferroviario recuperado cerca del puerto. Ofrece cerámica esmaltada, joyería de autor, textiles regionales, objetos de madera y vitrofusión realizados por artistas locales.\n\nHorario: Jue-Lun 10:00-20:00 hs.",
                ubicacion="https://www.google.com/maps/search/Mercado+Artesanal+Colonia",
                tags=["mañana","tarde","noche","artesanias", "ceramica", "joyeria", "textiles", "cultural", "local"],
                imagenes_url=[
                    "https://tse1.explicit.bing.net/th/id/OIP.B4MZSyGssd2D7iMBWlo_CAHaEK?rs=1&pid=ImgDetMain&o=7&rm=3",
                    "https://cdn.shopify.com/s/files/1/0591/9096/8528/files/PU02190_Joyas_de_Acero_Uruguay_Pulsera_Acero_Dorado.jpg?v=1682552381"
                ]
            ),
            Excursion(
                id="com_003",
                ciudad="Colonia",
                categoria="comercios",
                nombre="Feria de Emprendedores",
                descripcion="Feria tradicional al aire libre donde productores de todo el departamento exhiben su trabajo. Se pueden encontrar dulces regionales, manualidades, antigüedades, mates trabajados y piezas únicas de decoración criolla.\n\nHorario: Domingos 07:00-14:00 hs.",
                ubicacion="https://www.google.com/maps/search/Feria+Productores+Colonia",
                tags=["mañana","tarde","feria", "artesanias", "dulces", "antiguedades", "decoracion", "tradicional"],
                imagenes_url=[
                    "https://tse2.mm.bing.net/th/id/OIP.ONCJKpXjHK1WNTy5hDQNfgHaEo?w=1200&h=750&rs=1&pid=ImgDetMain&o=7&rm=3",
                    "https://dynamic-media-cdn.tripadvisor.com/media/photo-o/1c/2a/4b/3a/6.jpg?w=1200&h=1200&s=1"
                ]
            ),
            Excursion(
                id="com_004",
                ciudad="Colonia",
                categoria="comercios",
                nombre="Lemon",
                descripcion="Lemon es una de las marcas de indumentaria femenina más importantes de Uruguay, destacada por su estilo casual, contemporáneo y urbano. Su local en la avenida principal de Colonia ofrece una amplia variedad de prendas de temporada que combinan diseño moderno con comodidad, siendo una parada obligada para quienes buscan renovar su vestidor con calidad nacional.\n\nHorario: Lunes a Viernes de 10:00 a 19:00 hs, Sábados de 10:00 a 14:00 hs.",
                ubicacion="https://www.google.com/maps/search/Lemon+Colonia+Gral+Flores+435",
                tags=["mañana","tarde","noche", "ropa", "indumentaria", "mujer", "moda", "nacional", "premium"],
                imagenes_url=[
                    "https://kronelectronics.uy/wp-content/uploads/2025/04/LEMON.jpeg",
                    "https://tse2.mm.bing.net/th/id/OIP.ONCJKpXjHK1WNTy5hDQNfgHaEo?w=1200&h=750&rs=1&pid=ImgDetMain&o=7&rm=3"
                ]
            ),
            Excursion(
                id="com_005",
                ciudad="Colonia",
                categoria="comercios",
                nombre="Cosas Bellas",
                descripcion="Como su nombre lo indica, esta tienda es un refugio de objetos hermosos y curiosidades seleccionadas. Alejándose del souvenir masivo, ofrece artesanías de alta calidad, textiles, joyería de diseño, y productos gourmet locales. Es el sitio ideal para quienes desean llevarse un recuerdo auténtico de Colonia, en un local que en sí mismo es un paseo visual.\n\nHorario: Todos los días de 10:30 a 18:30 hs.",
                ubicacion="https://www.google.com/maps/search/Cosas+Bellas+Colonia+Misiones+Tapes",
                tags=["mañana","tarde","souvenirs", "artesanias", "joyeria", "textiles", "gourmet", "local", "premium"],
                imagenes_url=[
                    "https://dynamic-media-cdn.tripadvisor.com/media/photo-o/1c/2a/4b/3a/6.jpg?w=1200&h=1200&s=1",
                    "https://lombardia.com.uy/wp-content/uploads/2023/11/22-3.jpg"
                ]
            ),
            Excursion(
                id="com_006",
                ciudad="Colonia",
                categoria="comercios",
                nombre="Lombardía Arte & Joyas",
                descripcion="Es un prestigioso taller de orfebrería dirigido por Gino Martinelli, con fuerte presencia en Nueva Helvecia (Colonia). Se especializan en la fabricación artesanal de joyas clásicas y contemporáneas, además de ser expertos en platería criolla, una técnica tradicional uruguaya. Sus piezas son únicas, elaboradas con metales nobles y diseños que combinan la tradición orfebre con la elegancia moderna.\n\nHorario: Lunes a Viernes de 09:00 a 12:00 hs y de 14:30 a 18:30 hs (Aprox).",
                ubicacion="https://www.google.com/maps/search/Lombardia+Arte+y+Joyas+Nueva+Helvecia",
                tags=["mañana","tarde","joyeria", "orfebreria", "plateria", "artesanal", "premium", "tradicional"],
                imagenes_url=[
                    "https://lombardia.com.uy/wp-content/uploads/2023/11/22-3.jpg",
                    "https://tse1.explicit.bing.net/th/id/OIP.B4MZSyGssd2D7iMBWlo_CAHaEK?rs=1&pid=ImgDetMain&o=7&rm=3"
                ]
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
                tags=["mañana","tarde","noche","shopping", "marcas", "cine", "supermercado", "comida", "variedad"],
                imagenes_url=[
                    "https://kronelectronics.uy/wp-content/uploads/2025/04/LEMON.jpeg",
                    "https://tse1.mm.bing.net/th/id/OIP.jHoP55C9sIXPDXWUeJjHPgHaEO?rs=1&pid=ImgDetMain&o=7&rm=3"
                ]
            ),
            Excursion(
                id="compr_002",
                ciudad="Colonia",
                categoria="compras",
                nombre="Av. General Flores",
                descripcion="Es el 'shopping a cielo abierto' y la arteria principal de la ciudad. Concentra las mayores tiendas de ropa, zapaterías, bancos y farmacias, además de ser el eje central donde se desarrolla la vida social de Colonia.\n\nHorario: Variable (aprox. 10:00-19:00 hs).",
                ubicacion="https://www.google.com/maps/search/Avenida+General+Flores+Colonia",
                tags=["mañana","tarde","avenida", "tiendas", "ropa", "zapatos", "bancos", "social"],
                imagenes_url=[
                    "https://tse2.mm.bing.net/th/id/OIP.ONCJKpXjHK1WNTy5hDQNfgHaEo?w=1200&h=750&rs=1&pid=ImgDetMain&o=7&rm=3",
                    "https://media-cdn.tripadvisor.com/media/photo-s/0e/fe/98/25/acervo.jpg"
                ]
            )
        ],
        "cultural": [
            Excursion(
                id="cult_001",
                ciudad="Colonia",
                categoria="cultural",
                nombre="Teatro Bastión del Carmen",
                descripcion="Un centro cultural vibrante construido sobre los restos de una antigua fortificación española y una posterior fábrica de jabón. Este espacio combina muros de piedra originales con una arquitectura moderna, ofreciendo una sala de teatro, galerías de arte y un hermoso jardín que bordea la muralla con vista al río. Es el epicentro de la actividad artística local, albergando obras de teatro, conciertos y exposiciones de artes visuales durante todo el año.\n\nHorario: Depende de la programación; galería abierta de 12:00 a 20:00 hs.",
                ubicacion="https://goo.gl/maps/8V9R2Y7L1M4",
                tags=["mañana","tarde","teatro", "arte", "musica", "vistas", "arquitectura"],
                imagenes_url=[
                    "https://salimos.uy/wp-content/uploads/2021/01/bastion-del-carmen-en-colonia-del-sacramento.jpg",
                    "https://images.adsttc.com/media/images/61f0/4592/3e4b/313f/8900/001e/newsletter/DJI_0992.jpg?1643136376",
                    "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRyEbSkf-lD6Cnroy9tnsllSCGmC6RmK4yGLjX3UbqCcw&s=10"
                ]
            ),
            Excursion(
                id="cult_002",
                ciudad="Colonia",
                categoria="cultural",
                nombre="Plaza de Toros Real de San Carlos",
                descripcion="Inaugurada originalmente en 1910, es la única plaza de toros de estilo neomudéjar que queda en pie en el Río de la Plata. Tras un siglo de abandono debido a la prohibición de las corridas en Uruguay (1912), fue majestuosamente rehabilitada en 2021. Hoy funciona como un moderno centro de espectáculos y convenciones con capacidad para miles de personas. El complejo incluye un museo taurino que exhibe trajes de toreros y afiches de época, una vinoteca y un restaurante. Su acústica circular es tan perfecta que artistas como Jorge Drexler han elogiado el sonido del lugar.\n\nHorario: Lunes, jueves, viernes, sábados y domingos de 10:00 a 18:30 hs. (Sábados hasta las 19:00 hs).",
                ubicacion="https://maps.app.goo.gl/3P3Z5G9J6XN2",
                tags=["mañana","tarde","historia", "arquitectura", "espectaculos", "museo", "patrimonio"],
                imagenes_url=[
                    "https://images.adsttc.com/media/images/61f0/4592/3e4b/313f/8900/001e/newsletter/DJI_0992.jpg?1643136376",
                    "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRyEbSkf-lD6Cnroy9tnsllSCGmC6RmK4yGLjX3UbqCcw&s=10"
                ]
            ),
            Excursion(
                id="cult_003",
                ciudad="Colonia",
                categoria="cultural",
                nombre="Museo del Período Histórico Portugués",
                descripcion="Ubicado en una antigua casona de 1720 frente a la Plaza Mayor, este museo recrea fielmente la presencia lusitana en la ciudad. El acervo se centra en la historia política y bélica, exhibiendo armas, escudos, uniformes militares, mobiliario y cartografía original que marcaron el período de fundación de Colonia del Sacramento por parte de los portugueses. Es una pieza fundamental para entender la identidad binacional y el valor estratégico que tuvo la ciudad durante el siglo XVIII.\n\nHorario: Jueves a martes de 11:30 a 16:30 hs.",
                ubicacion="https://www.google.com/maps/search/Museo+Portugues+Colonia+del+Sacramento",
                tags=["mañana","tarde","historia", "museo", "portugal", "colonial", "patrimonio"],
                imagenes_url=[
                    "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRyEbSkf-lD6Cnroy9tnsllSCGmC6RmK4yGLjX3UbqCcw&s=10",
                    "https://images.adsttc.com/media/images/61f0/4592/3e4b/313f/8900/001e/newsletter/DJI_0992.jpg?1643136376"
                ]
            ),
            Excursion(
                id="cult_004",
                ciudad="Colonia",
                categoria="cultural",
                nombre="Museo Municipal Dr. Bautista Rebuffo",
                descripcion="Es el museo más antiguo y completo de la ciudad (fundado en 1951). Se ubica en la 'Casa de Brown', una construcción principalmente portuguesa del siglo XVIII con intervenciones españolas. Su colección es sumamente variada, abarcando desde arqueología indígena y restos fósiles (incluyendo un esqueleto de ballena azul en el patio trasero) hasta documentos y mobiliario de la época colonial. Es una parada obligatoria para comprender la identidad y evolución de esta ciudad declarada Patrimonio de la Humanidad por la UNESCO.\n\nHorario: Martes a domingo de 11:30 a 16:30 hs.",
                ubicacion="https://www.google.com/maps/search/Museo+Municipal+Dr+Bautista+Rebuffo+Colonia",
                tags=["mañana","tarde","historia", "museo", "arqueologia", "paleontologia", "patrimonio"],
                imagenes_url=[
                    "https://media-cdn.tripadvisor.com/media/photo-s/0e/fe/98/25/acervo.jpg",
                    "https://salimos.uy/wp-content/uploads/2021/01/bastion-del-carmen-en-colonia-del-sacramento.jpg"
                ]
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
