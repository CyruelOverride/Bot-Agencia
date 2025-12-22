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
        """Verifica si el perfil tiene información suficiente para generar un plan"""
        if not self.perfil:
            return False
        
        # Mínimo: tener al menos un interés y alguna preferencia básica
        if len(self.intereses) == 0:
            return False
        
        # Verificar que el perfil tenga al menos información básica
        perfil = self.perfil
        tiene_info_basica = (
            perfil.tipo_viaje is not None or
            perfil.preferencias_comida is not None or
            perfil.presupuesto is not None or
            perfil.duracion_estadia is not None
        )
        
        return tiene_info_basica
    
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

