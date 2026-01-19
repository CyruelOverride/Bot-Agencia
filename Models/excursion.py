from typing import List, Optional


class Excursion:
    def __init__(
        self,
        id: str,
        ciudad: str,
        categoria: str,  # "restaurantes", "comercios", "compras", "cultural"
        nombre: str,
        descripcion: str,
        ubicacion: Optional[str] = None,
        tags: Optional[List[str]] = None,
        imagen_url: Optional[str] = None,  # URL de la imagen del lugar (deprecated, usar imagenes_url)
        imagenes_url: Optional[List[str]] = None,  # Lista de URLs de imágenes del lugar
        pagina_web: Optional[str] = None  # URL de la página web del lugar
    ):
        self.id = id
        self.ciudad = ciudad
        self.categoria = categoria
        self.nombre = nombre
        self.descripcion = descripcion
        self.ubicacion = ubicacion
        self.tags = tags or []
        self.pagina_web = pagina_web
        # Soporte para múltiples imágenes
        if imagenes_url is not None:
            self.imagenes_url = imagenes_url if isinstance(imagenes_url, list) else [imagenes_url]
        elif imagen_url is not None:
            # Compatibilidad hacia atrás: convertir imagen_url única a lista
            self.imagenes_url = [imagen_url]
        else:
            self.imagenes_url = []
        # Mantener imagen_url para compatibilidad hacia atrás (primera imagen)
        self.imagen_url = self.imagenes_url[0] if self.imagenes_url else None
    
    def tiene_tag(self, tag: str) -> bool:
        """Verifica si la excursión tiene un tag específico"""
        return tag.lower() in [t.lower() for t in self.tags]
    
    def coincide_con_perfil(self, perfil) -> bool:
        """Verifica si la excursión coincide con el perfil del usuario"""
        # Lógica básica de coincidencia
        if perfil.preferencias_comida:
            if self.categoria == "restaurantes":
                if perfil.preferencias_comida == "vegetariano" and not self.tiene_tag("vegetariano"):
                    return False
                if perfil.preferencias_comida == "vegano" and not self.tiene_tag("vegano"):
                    return False
        
        return True
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "ciudad": self.ciudad,
            "categoria": self.categoria,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "ubicacion": self.ubicacion,
            "tags": self.tags,
            "imagen_url": self.imagen_url,  # Mantener para compatibilidad
            "imagenes_url": self.imagenes_url,
            "pagina_web": self.pagina_web
        }

