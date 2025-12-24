from typing import List, Optional


class Excursion:
    def __init__(
        self,
        id: str,
        ciudad: str,
        categoria: str,  # "restaurantes", "comercios", "recreacion", "cultura", "compras"
        nombre: str,
        descripcion: str,
        ubicacion: Optional[str] = None,
        tags: Optional[List[str]] = None,
        imagen_url: Optional[str] = None  # URL de la imagen del lugar
    ):
        self.id = id
        self.ciudad = ciudad
        self.categoria = categoria
        self.nombre = nombre
        self.descripcion = descripcion
        self.ubicacion = ubicacion
        self.tags = tags or []
        self.imagen_url = imagen_url
    
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
            "imagen_url": self.imagen_url
        }

