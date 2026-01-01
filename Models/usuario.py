from typing import Optional, List, Dict
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
        fecha_ultima_interaccion: Optional[datetime] = None,
        lugares_enviados: Optional[Dict[str, List[str]]] = None
    ):
        self.telefono = telefono
        self.nombre = nombre
        self.ciudad = ciudad
        self.intereses = intereses or []
        self.perfil = perfil
        self.estado_conversacion = estado_conversacion
        self.fecha_ultima_interaccion = fecha_ultima_interaccion or datetime.now()
        # Diccionario donde la clave es el interés y el valor es una lista de IDs de lugares enviados
        self.lugares_enviados = lugares_enviados or {}
    
    def actualizar_ultima_interaccion(self):
        self.fecha_ultima_interaccion = datetime.now()
    
    def agregar_interes(self, interes: str):
        if interes not in self.intereses:
            self.intereses.append(interes)
    
    def agregar_lugar_enviado(self, lugar_id: str, interes: str):
        """
        Agrega un lugar enviado al diccionario de lugares enviados.
        
        Args:
            lugar_id: ID del lugar enviado
            interes: Interés al que pertenece el lugar (restaurantes, comercios, compras, cultura)
        """
        if interes not in self.lugares_enviados:
            self.lugares_enviados[interes] = []
        if lugar_id not in self.lugares_enviados[interes]:
            self.lugares_enviados[interes].append(lugar_id)
    
    def obtener_lugares_enviados_por_interes(self, interes: str) -> List[str]:
        """
        Obtiene la lista de IDs de lugares enviados para un interés específico.
        
        Args:
            interes: Interés del cual obtener los lugares enviados
            
        Returns:
            Lista de IDs de lugares enviados para ese interés
        """
        return self.lugares_enviados.get(interes, [])
    
    def obtener_todos_lugares_enviados(self) -> List[str]:
        """
        Obtiene todos los IDs de lugares enviados sin importar el interés.
        
        Returns:
            Lista de todos los IDs de lugares enviados
        """
        todos_lugares = []
        for lugares in self.lugares_enviados.values():
            todos_lugares.extend(lugares)
        return todos_lugares
    
    def tiene_perfil_completo(self) -> bool:
        """
        Verifica si el perfil está completo según las reglas definidas.
        
        Perfil completo cuando tiene:
        - Campos obligatorios siempre: tipo_viaje, duracion_estadia
        - Campos condicionales según intereses:
          * preferencias_comida (solo si "restaurantes" en intereses)
          * interes_regalos (solo si "compras" en intereses)
          * interes_ropa (solo si "compras" en intereses)
          * interes_tipo_comercios (solo si "comercios" en intereses)
          * interes_tipo_cultura (solo si "cultura" en intereses)
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
        
        if "comercios" in self.intereses:
            if perfil.interes_tipo_comercios is None:
                return False
        
        if "cultura" in self.intereses:
            if perfil.interes_tipo_cultura is None:
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
            "fecha_ultima_interaccion": self.fecha_ultima_interaccion.isoformat() if self.fecha_ultima_interaccion else None,
            "lugares_enviados": self.lugares_enviados
        }

