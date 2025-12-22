from typing import Optional, List


class PerfilUsuario:
    def __init__(
        self,
        tipo_viaje: Optional[str] = None,  # "solo", "pareja", "familia", "amigos", "negocios"
        acompanantes: Optional[str] = None,  # "solo", "pareja", "familia", "amigos"
        preferencias_comida: Optional[str] = None,  # "local", "internacional", "vegetariano", "vegano", "sin_restricciones"
        presupuesto: Optional[str] = None,  # "economico", "medio", "alto", "premium"
        interes_regalos: Optional[bool] = None,
        interes_ropa: Optional[bool] = None,  # True si le interesa comprar ropa
        interes_tipo_recreacion: Optional[str] = None,  # "activa", "pasiva", "familiar", "romantica"
        viaja_con_ninos: Optional[bool] = None,  # True si viaja con niños/familiares chicos
        duracion_estadia: Optional[int] = None  # días
    ):
        self.tipo_viaje = tipo_viaje
        self.acompanantes = acompanantes
        self.preferencias_comida = preferencias_comida
        self.presupuesto = presupuesto
        self.interes_regalos = interes_regalos
        self.interes_ropa = interes_ropa
        self.interes_tipo_recreacion = interes_tipo_recreacion
        self.viaja_con_ninos = viaja_con_ninos
        self.duracion_estadia = duracion_estadia
    
    def actualizar_campo(self, campo: str, valor):
        """Actualiza un campo del perfil dinámicamente"""
        if hasattr(self, campo):
            setattr(self, campo, valor)
    
    def obtener_campos_faltantes(self, intereses: List[str] = None) -> List[str]:
        """
        Retorna lista de campos que aún no tienen valor.
        Considera campos obligatorios y condicionales según intereses.
        
        Campos obligatorios siempre:
        - tipo_viaje
        - acompanantes
        - presupuesto
        - duracion_estadia
        
        Campos condicionales:
        - preferencias_comida (solo si "restaurantes" en intereses)
        - interes_regalos (solo si "compras" en intereses)
        - interes_ropa (solo si "compras" en intereses)
        - interes_tipo_recreacion (solo si "recreacion" en intereses)
        """
        if intereses is None:
            intereses = []
        
        # Campos obligatorios siempre
        campos_obligatorios = [
            "tipo_viaje",
            "acompanantes",
            "presupuesto",
            "duracion_estadia"
        ]
        
        # Campos condicionales según intereses
        campos_condicionales = []
        
        if "restaurantes" in intereses:
            campos_condicionales.append("preferencias_comida")
        
        if "compras" in intereses:
            campos_condicionales.append("interes_regalos")
            campos_condicionales.append("interes_ropa")
        
        if "recreacion" in intereses:
            campos_condicionales.append("interes_tipo_recreacion")
        
        # Si viaja con familia, preguntar si hay niños
        if self.acompanantes == "familia" and self.viaja_con_ninos is None:
            campos_condicionales.append("viaja_con_ninos")
        
        # Combinar todos los campos requeridos
        campos_requeridos = campos_obligatorios + campos_condicionales
        
        # Retornar solo los que faltan
        return [campo for campo in campos_requeridos if getattr(self, campo) is None]
    
    def to_dict(self) -> dict:
        return {
            "tipo_viaje": self.tipo_viaje,
            "acompanantes": self.acompanantes,
            "preferencias_comida": self.preferencias_comida,
            "presupuesto": self.presupuesto,
            "interes_regalos": self.interes_regalos,
            "interes_ropa": self.interes_ropa,
            "interes_tipo_recreacion": self.interes_tipo_recreacion,
            "viaja_con_ninos": self.viaja_con_ninos,
            "duracion_estadia": self.duracion_estadia
        }

