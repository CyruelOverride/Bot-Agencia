from typing import Optional, List


class PerfilUsuario:
    def __init__(
        self,
        tipo_viaje: Optional[str] = None,  # "solo", "pareja", "familia", "amigos", "negocios"
        acompanantes: Optional[str] = None,  # "solo", "pareja", "familia", "amigos"
        preferencias_comida: Optional[str] = None,  # "local", "internacional", "vegetariano", "vegano", "sin_restricciones"
        presupuesto: Optional[str] = None,  # "economico", "medio", "alto", "premium"
        interes_regalos: Optional[bool] = None,
        duracion_estadia: Optional[int] = None  # días
    ):
        self.tipo_viaje = tipo_viaje
        self.acompanantes = acompanantes
        self.preferencias_comida = preferencias_comida
        self.presupuesto = presupuesto
        self.interes_regalos = interes_regalos
        self.duracion_estadia = duracion_estadia
    
    def actualizar_campo(self, campo: str, valor):
        """Actualiza un campo del perfil dinámicamente"""
        if hasattr(self, campo):
            setattr(self, campo, valor)
    
    def obtener_campos_faltantes(self) -> List[str]:
        """Retorna lista de campos que aún no tienen valor"""
        campos = [
            "tipo_viaje",
            "acompanantes", 
            "preferencias_comida",
            "presupuesto",
            "interes_regalos",
            "duracion_estadia"
        ]
        return [campo for campo in campos if getattr(self, campo) is None]
    
    def to_dict(self) -> dict:
        return {
            "tipo_viaje": self.tipo_viaje,
            "acompanantes": self.acompanantes,
            "preferencias_comida": self.preferencias_comida,
            "presupuesto": self.presupuesto,
            "interes_regalos": self.interes_regalos,
            "duracion_estadia": self.duracion_estadia
        }

