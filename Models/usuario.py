from typing import Optional, List
from datetime import datetime
from Models.perfil_usuario import PerfilUsuario


class Usuario:
    def __init__(
        self,
        telefono: str,
        nombre: Optional[str] = None,
        ciudad: Optional[str] = None,
        intereses: Optional[List[str]] = None,
        perfil: Optional[PerfilUsuario] = None,
        estado_conversacion: str = "INICIO",
        fecha_ultima_interaccion: Optional[datetime] = None
    ):
        self.telefono = telefono
        self.nombre = nombre
        self.ciudad = ciudad
        self.intereses = intereses or []
        self.perfil = perfil
        self.estado_conversacion = estado_conversacion
        self.fecha_ultima_interaccion = fecha_ultima_interaccion or datetime.now()
    
    def actualizar_ultima_interaccion(self):
        self.fecha_ultima_interaccion = datetime.now()
    
    def agregar_interes(self, interes: str):
        if interes not in self.intereses:
            self.intereses.append(interes)
    
    def tiene_perfil_completo(self) -> bool:
        """
        Verifica si el perfil está completo según las reglas definidas.
        
        Perfil completo cuando tiene:
        - Campos obligatorios siempre: tipo_viaje, duracion_estadia
        - Campos condicionales según intereses:
          * preferencias_comida (solo si "restaurantes" en intereses)
          * interes_regalos (solo si "compras" en intereses)
          * interes_ropa (solo si "compras" en intereses)
          * interes_tipo_recreacion (solo si "recreacion" en intereses)
        """
        if not self.perfil:
            return False
        
        # Debe tener al menos un interés
        if len(self.intereses) == 0:
            return False
        
        perfil = self.perfil
        
        # Verificar campos obligatorios (siempre requeridos)
        campos_obligatorios_completos = (
            perfil.tipo_viaje is not None and
            perfil.duracion_estadia is not None
        )
        
        if not campos_obligatorios_completos:
            return False
        
        # Verificar campos condicionales según intereses
        if "restaurantes" in self.intereses:
            if perfil.preferencias_comida is None:
                return False
        
        if "compras" in self.intereses:
            if perfil.interes_regalos is None:
                return False
            if perfil.interes_ropa is None:
                return False
        
        if "recreacion" in self.intereses:
            if perfil.interes_tipo_recreacion is None:
                return False
        
        # Si viaja con familia, debe tener respuesta sobre niños
        if perfil.tipo_viaje == "familia":
            if perfil.viaja_con_ninos is None:
                return False
        
        # Si llegamos aquí, el perfil está completo
        return True
    
    def to_dict(self) -> dict:
        return {
            "telefono": self.telefono,
            "nombre": self.nombre,
            "ciudad": self.ciudad,
            "intereses": self.intereses,
            "perfil": self.perfil.to_dict() if self.perfil else None,
            "estado_conversacion": self.estado_conversacion,
            "fecha_ultima_interaccion": self.fecha_ultima_interaccion.isoformat() if self.fecha_ultima_interaccion else None
        }

