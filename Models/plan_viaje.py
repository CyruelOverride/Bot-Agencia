from typing import List, Optional
from datetime import datetime
from Models.excursion import Excursion


class PlanViaje:
    def __init__(
        self,
        usuario_id: str,
        ciudad: str,
        resumen_ia: str,
        excursiones: List[Excursion],
        fecha_creacion: Optional[datetime] = None
    ):
        self.usuario_id = usuario_id
        self.ciudad = ciudad
        self.resumen_ia = resumen_ia
        self.excursiones = excursiones
        self.fecha_creacion = fecha_creacion or datetime.now()
    
    def obtener_excursiones_por_categoria(self) -> dict:
        """Agrupa las excursiones por categoría"""
        resultado = {}
        for exc in self.excursiones:
            if exc.categoria not in resultado:
                resultado[exc.categoria] = []
            resultado[exc.categoria].append(exc)
        return resultado
    
    def to_dict(self) -> dict:
        return {
            "usuario_id": self.usuario_id,
            "ciudad": self.ciudad,
            "resumen_ia": self.resumen_ia,
            "excursiones": [exc.to_dict() for exc in self.excursiones],
            "fecha_creacion": self.fecha_creacion.isoformat() if self.fecha_creacion else None
        }

