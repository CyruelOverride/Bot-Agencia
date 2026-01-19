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
                descripcion="Ubicado en la emblemática Calle de los Suspiros, este local del siglo XVIII conserva su arquitectura original y ofrece un ambiente íntimo para disfrutar quesos regionales, fiambres artesanales y vinos uruguayos premium, ideal para una picada o brindis romántico. Abre todos los días de 11:00 a 20:00 hs.",
                ubicacion="https://www.google.com/maps/search/El+Buen+Suspiro+Colonia",
                tags=["mañana", "tarde", "noche", "quesos", "vinos", "romantico", "historico", "premium"],
                imagenes_url=[
                    "https://media-cdn.tripadvisor.com/media/photo-s/0e/d1/3a/50/fachada-de-la-casa-ano.jpg",
                    "https://tse2.mm.bing.net/th/id/OIP.dQPA01pCW5z2QsTAWvpPmAHaEK?rs=1&pid=ImgDetMain&o=7&rm=3"
                ],
                pagina_web="no cuenta con sitio web actualmente"
            ),
            Excursion(
                id="rest_002",
                ciudad="Colonia",
                categoria="restaurantes",
                nombre="Charco Bistró",
                descripcion="Restaurante de autor ubicado en un hotel boutique del casco histórico, con diseño elegante y terraza con vistas al Río de la Plata. Ofrece una propuesta de alta cocina con mariscos, pulpo a la parrilla, carnes premium y pastelería seleccionada. Abre todos los días de 08:00 a 23:00 hs.",
                ubicacion="https://www.google.com/maps/search/Charco+Bistro+Colonia",
                tags=["mañana","tarde","noche", "alta_cocina", "mariscos", "premium", "vista_rio", "elegante"],
                imagenes_url=[
                    "https://media-cdn.tripadvisor.com/media/photo-s/0f/39/57/29/terrace.jpg",
                    "https://img.hellofresh.com/w_3840,q_auto,f_auto,c_fill,fl_lossy/hellofresh_website/es/cms/SEO/recipes/gourmet/entrecot-de-ternera.jpeg"
                ],
                pagina_web="no cuenta con sitio web actualmente"
            ),
            Excursion(
                id="rest_003",
                ciudad="Colonia",
                categoria="restaurantes",
                nombre="La Bodeguita",
                descripcion="Pizzería y restaurante ubicada sobre la antigua muralla de la ciudad, famosa por su terraza ideal para ver el atardecer. Se especializa en pizzas de horno de barro y también ofrece chivitos y pastas en un ambiente relajado y bohemio. Abre todos los días a partir de las 20:00 hs.",
                ubicacion="https://www.google.com/maps/search/La+Bodeguita+Colonia",
                tags=["noche", "pizza", "horno_barro", "atardecer", "bohemio", "terraza"],
                imagenes_url=[
                    "https://th.bing.com/th/id/R.fd97452e324b98f82067527e105c3cae?rik=iP76bvNh%2fnrOhQ&pid=ImgRaw&r=0",
                    "https://tse3.mm.bing.net/th/id/OIP.pbrxeUZsbRcWg30Y95bscwHaFj?rs=1&pid=ImgDetMain&o=7&rm=3",
                ],
                pagina_web="no cuenta con sitio web actualmente"
            ),
        ],
        "comercios": [
            Excursion(
                id="com_001",
                ciudad="Colonia",
                categoria="comercios",
                nombre="Manos del Uruguay",
                descripcion="Cooperativa nacional sin fines de lucro integrada a la Organización Mundial del Comercio Justo. Ofrece prendas de lana tejidas a mano de alta gama, accesorios de cuero, mantas de diseño y joyería artesanal de exportación. Abre todos los días de 10:00 a 19:00 hs.",
                ubicacion="https://www.google.com/maps/search/Manos+del+Uruguay+Colonia",
                tags=["tarde","noche", "artesanias", "lana", "cuero", "joyeria", "comercio_justo", "premium"],
                imagenes_url=[
                    "https://th.bing.com/th/id/R.fcc02c6e342e664aefe296212cc5bd7a?rik=w%2fH9MgtB2e%2b4Rg&riu=http%3a%2f%2fwww.explore-uruguay.com%2fimage-files%2fmanos-del-uruguay-yarn.jpg&ehk=EQYO4bfb1LD6MA9CYcLVC1jkdJZPoitS8qd7TIy1j0s%3d&risl=&pid=ImgRaw&r=0",
                    "https://www.designscene.net/wp-content/uploads/2019/02/M-Missoni-FW19-03-620x930.jpg"
                ],
                pagina_web="https://www.manos.com.uy/"
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
                    "https://rosarioweb.com.uy/wp-content/uploads/2023/05/FB_IMG_1683663472591.jpg",
                    "https://tse4.mm.bing.net/th/id/OIP.AzlfAo3zU7sTth156auKEwHaFj?rs=1&pid=ImgDetMain&o=7&rm=3"
                ],
                pagina_web="no cuenta con sitio web actualmente"
            ),
            Excursion(
                id="com_003",
                ciudad="Colonia",
                categoria="comercios",
                nombre="Lemon",
                descripcion="Lemon es una reconocida marca uruguaya de indumentaria femenina con estilo casual y urbano. Su local en la avenida principal de Colonia ofrece prendas de temporada que combinan diseño moderno y comodidad. Abre de lunes a viernes de 10:00 a 19:00 hs y sábados de 10:00 a 14:00 hs.",
                ubicacion="https://www.google.com/maps/search/Lemon+Colonia+Gral+Flores+435",
                tags=["mañana","tarde","noche", "ropa", "indumentaria", "mujer", "moda", "nacional", "premium"],
                imagenes_url=[
                    "https://kronelectronics.uy/wp-content/uploads/2025/04/LEMON.jpeg"  # REPETIDA: también en compr_001 (Colonia Shopping)
                ],
                pagina_web="https://lemon.com.uy/"
            ),
            Excursion(
                id="com_004",
                ciudad="Colonia",
                categoria="comercios",
                nombre="Cosas Bellas",
                descripcion="Como su nombre lo indica, esta tienda es un refugio de objetos hermosos y curiosidades seleccionadas. Alejándose del souvenir masivo, ofrece artesanías de alta calidad, textiles, joyería de diseño, y productos gourmet locales. Es el sitio ideal para quienes desean llevarse un recuerdo auténtico de Colonia, en un local que en sí mismo es un paseo visual.\n\nHorario: Todos los días de 10:30 a 18:30 hs.",
                ubicacion="https://www.google.com/maps/search/Cosas+Bellas+Colonia+Misiones+Tapes",
                tags=["mañana","tarde","souvenirs", "artesanias", "joyeria", "textiles", "gourmet", "local", "premium"],
                imagenes_url=[
                    "https://dynamic-media-cdn.tripadvisor.com/media/photo-o/1c/2a/4b/3a/6.jpg?w=1200&h=1200&s=1",  # REPETIDA: también en com_003 (Feria de Emprendedores)
                    "https://th.bing.com/th/id/R.56f669861b8254e6113582d1178bc5cf?rik=b%2bx%2fvXGN226reA&pid=ImgRaw&r=0"  # REPETIDA: también en com_006 (Lombardía Arte & Joyas)
                ],
                pagina_web="no cuenta con sitio web actualmente"
            ),
            Excursion(
                id="com_005",
                ciudad="Colonia",
                categoria="comercios",
                nombre="Lombardía Arte & Joyas",
                descripcion="Prestigioso taller de orfebrería dirigido por Gino Martinelli, especializado en joyas artesanales clásicas y contemporáneas, así como en platería criolla tradicional. Sus piezas únicas combinan metales nobles, tradición y elegancia moderna. Atiende de lunes a viernes de 09:00 a 12:00 hs y de 14:30 a 18:30 hs.",
                ubicacion="https://www.google.com/maps/search/Lombardia+Arte+y+Joyas+Nueva+Helvecia",
                tags=["mañana","tarde","joyeria", "orfebreria", "plateria", "artesanal", "premium", "tradicional"],
                imagenes_url=[
                    "https://lombardia.com.uy/wp-content/uploads/2024/12/2-17.jpg",
                    "https://tse1.explicit.bing.net/th/id/OIP.B4MZSyGssd2D7iMBWlo_CAHaEK?rs=1&pid=ImgDetMain&o=7&rm=3"  # REPETIDA: también en com_002 (Mercado Artesanal)
                ],
                pagina_web="https://lombardia.com.uy/"
            )
        ],
        "compras": [
            Excursion(
                id="compr_001",
                ciudad="Colonia",
                categoria="compras",
                nombre="Colonia Shopping",
                descripcion="El centro comercial cerrado más importante de la ciudad. Cuenta con más de cien marcas nacionales e internacionales, salas de cine, un gran supermercado (Ta-Ta) y una plaza de comidas variada. Abre todos los días de 10:00 a 22:00 hs.",
                ubicacion="https://www.google.com/maps/search/Colonia+Shopping",
                tags=["mañana","tarde","noche","shopping", "marcas", "cine", "supermercado", "comida", "variedad"],
                imagenes_url=[
                    "https://kronelectronics.uy/wp-content/uploads/2025/04/LEMON.jpeg",  # REPETIDA: también en com_004 (Lemon)
                    "https://tse1.mm.bing.net/th/id/OIP.jHoP55C9sIXPDXWUeJjHPgHaEO?rs=1&pid=ImgDetMain&o=7&rm=3"  # REPETIDA: también en com_001 (Manos del Uruguay)
                ],
                pagina_web="no cuenta con sitio web actualmente"
            ),
            Excursion(
                id="compr_002",
                ciudad="Colonia",
                categoria="compras",
                nombre="Av. General Flores",
                descripcion="Es el 'shopping a cielo abierto' y la arteria principal de la ciudad. Concentra las mayores tiendas de ropa, zapaterías, bancos y farmacias, además de ser el eje central donde se desarrolla la vida social de Colonia. Abre todos los días de 10:00 a 19:00 hs.",
                ubicacion="https://www.google.com/maps/search/Avenida+General+Flores+Colonia",
                tags=["mañana","tarde","avenida", "tiendas", "ropa", "zapatos", "bancos", "social"],
                imagenes_url=[
                    "https://tse2.mm.bing.net/th/id/OIP.ONCJKpXjHK1WNTy5hDQNfgHaEo?w=1200&h=750&rs=1&pid=ImgDetMain&o=7&rm=3",  # REPETIDA: también en com_003 (Feria de Emprendedores) y com_004 (Lemon)
                    "https://media-cdn.tripadvisor.com/media/photo-s/0e/fe/98/25/acervo.jpg"  # REPETIDA: también en cult_004 (Museo Municipal Dr. Bautista Rebuffo)
                ],
                pagina_web="no cuenta con sitio web actualmente"
            )
        ],
        "cultural": [
            Excursion(
                id="cult_001",
                ciudad="Colonia",
                categoria="cultural",
                nombre="Teatro Bastión del Carmen",
                descripcion="Un centro cultural vibrante construido sobre los restos de una antigua fortificación española y una posterior fábrica de jabón. Este espacio combina muros de piedra originales con una arquitectura moderna, ofreciendo una sala de teatro, galerías de arte y un hermoso jardín que bordea la muralla con vista al río. Es el epicentro de la actividad artística local, albergando obras de teatro, conciertos y exposiciones de artes visuales durante todo el año. La galería abierta está abierta de 12:00 a 20:00 hs.",
                ubicacion="https://goo.gl/maps/8V9R2Y7L1M4",
                tags=["mañana","tarde","teatro", "arte", "musica", "vistas", "arquitectura"],
                imagenes_url=[
                    "https://salimos.uy/wp-content/uploads/2021/01/bastion-del-carmen-en-colonia-del-sacramento.jpg",  # REPETIDA: también en cult_004 (Museo Municipal Dr. Bautista Rebuffo)
                    "https://images.adsttc.com/media/images/61f0/4592/3e4b/313f/8900/001e/newsletter/DJI_0992.jpg?1643136376",  # REPETIDA: también en cult_002 (Plaza de Toros Real de San Carlos) y cult_003 (Museo del Período Histórico Portugués)
                    "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRyEbSkf-lD6Cnroy9tnsllSCGmC6RmK4yGLjX3UbqCcw&s=10"  # REPETIDA: también en cult_002 (Plaza de Toros Real de San Carlos) y cult_003 (Museo del Período Histórico Portugués)
                ],
                pagina_web="no cuenta con sitio web actualmente"
            ),
            Excursion(
                id="cult_002",
                ciudad="Colonia",
                categoria="cultural",
                nombre="Plaza de Toros Real de San Carlos",
                ubicacion="https://maps.app.goo.gl/3P3Z5G9J6XN2",
                descripcion="Inaugurada en 1910, es la única plaza de toros neomudéjar del Río de la Plata. Restaurada en 2021, hoy funciona como centro de espectáculos y convenciones, con museo taurino, vinoteca y restaurante, destacándose por su excelente acústica. Abre de lunes, jueves a domingos de 10:00 a 18:30 hs (sábados hasta las 19:00 hs).",
                tags=["mañana","tarde","historia", "arquitectura", "espectaculos", "museo", "patrimonio"],
                imagenes_url=[
                    "https://images.adsttc.com/media/images/61f0/4592/3e4b/313f/8900/001e/newsletter/DJI_0992.jpg?1643136376",  # REPETIDA: también en cult_001 (Teatro Bastión del Carmen) y cult_003 (Museo del Período Histórico Portugués)
                    "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRyEbSkf-lD6Cnroy9tnsllSCGmC6RmK4yGLjX3UbqCcw&s=10"  # REPETIDA: también en cult_001 (Teatro Bastión del Carmen) y cult_003 (Museo del Período Histórico Portugués)
                ],
                pagina_web="no cuenta con sitio web actualmente"
            ),
            Excursion(
                id="cult_003",
                ciudad="Colonia",
                categoria="cultural",
                nombre="Museo del Período Histórico Portugués",
                descripcion="Museo ubicado en una casona de 1720 frente a la Plaza Mayor, dedicado a la historia portuguesa de Colonia del Sacramento. Exhibe armas, uniformes, mobiliario y cartografía del período fundacional, clave para comprender la identidad y el valor estratégico de la ciudad. Abre de jueves a martes de 11:30 a 16:30 hs.",
                ubicacion="https://www.google.com/maps/search/Museo+Portugues+Colonia+del+Sacramento",
                tags=["mañana","tarde","historia", "museo", "portugal", "colonial", "patrimonio"],
                imagenes_url=[
                    "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRyEbSkf-lD6Cnroy9tnsllSCGmC6RmK4yGLjX3UbqCcw&s=10",  # REPETIDA: también en cult_001 (Teatro Bastión del Carmen) y cult_002 (Plaza de Toros Real de San Carlos)
                    "https://images.adsttc.com/media/images/61f0/4592/3e4b/313f/8900/001e/newsletter/DJI_0992.jpg?1643136376"  # REPETIDA: también en cult_001 (Teatro Bastión del Carmen) y cult_002 (Plaza de Toros Real de San Carlos)
                ],
                pagina_web="no cuenta con sitio web actualmente"
            ),
            Excursion(
                id="cult_004",
                ciudad="Colonia",
                categoria="cultural",
                nombre="Museo Municipal Dr. Bautista Rebuffo",
                descripcion="Museo más antiguo y completo de la ciudad, fundado en 1951 y ubicado en la histórica Casa de Brown. Su colección abarca arqueología indígena, restos fósiles, documentos y mobiliario colonial, siendo clave para entender la identidad y evolución de Colonia del Sacramento. Abre de martes a domingo de 11:30 a 16:30 hs.",
                ubicacion="https://www.google.com/maps/search/Museo+Municipal+Dr+Bautista+Rebuffo+Colonia",
                tags=["mañana","tarde","historia", "museo", "arqueologia", "paleontologia", "patrimonio"],
                imagenes_url=[
                    "https://media-cdn.tripadvisor.com/media/photo-s/0e/fe/98/25/acervo.jpg",  # REPETIDA: también en compr_002 (Av. General Flores)
                    "https://salimos.uy/wp-content/uploads/2021/01/bastion-del-carmen-en-colonia-del-sacramento.jpg"  # REPETIDA: también en cult_001 (Teatro Bastión del Carmen)
                ],
                pagina_web="no cuenta con sitio web actualmente"
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
