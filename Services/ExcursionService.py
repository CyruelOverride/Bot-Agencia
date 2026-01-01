from typing import List, Optional
from Models.excursion import Excursion
from Models.perfil_usuario import PerfilUsuario
from Util.datos_lugares import (
    obtener_lugares_por_ciudad,
    obtener_lugares_por_categoria,
    obtener_todas_las_categorias
)


class ExcursionService:
    @staticmethod
    def obtener_excursiones_por_categoria(ciudad: str, categoria: str) -> List[Excursion]:
        """Obtiene excursiones de una categoría específica en una ciudad"""
        return obtener_lugares_por_categoria(ciudad, categoria)
    
    @staticmethod
    def obtener_excursiones_por_ciudad(ciudad: str) -> List[Excursion]:
        """Obtiene todas las excursiones de una ciudad"""
        lugares_por_categoria = obtener_lugares_por_ciudad(ciudad)
        todas_las_excursiones = []
        for categoria, excursiones in lugares_por_categoria.items():
            todas_las_excursiones.extend(excursiones)
        return todas_las_excursiones
    
    @staticmethod
    def filtrar_por_perfil(
        excursiones: List[Excursion],
        perfil: PerfilUsuario,
        intereses: List[str]
    ) -> List[Excursion]:
        """Filtra excursiones según el perfil del usuario y sus intereses"""
        if not excursiones:
            return []
        
        # Mapeo de intereses a categorías
        mapeo_interes_categoria = {
            "cultura": "cultural"
        }
        
        # Convertir intereses a categorías
        categorias_interes = []
        for interes in intereses:
            categoria = mapeo_interes_categoria.get(interes.lower(), interes.lower())
            categorias_interes.append(categoria)
        
        # Primero filtrar por intereses (categorías)
        excursiones_filtradas = []
        ids_agregados = set()
        
        for exc in excursiones:
            # Si la categoría de la excursión coincide con algún interés
            if exc.categoria.lower() in categorias_interes or any(
                cat in exc.categoria.lower() for cat in categorias_interes
            ):
                # Verificar si coincide con el perfil
                if exc.coincide_con_perfil(perfil):
                    excursiones_filtradas.append(exc)
                    ids_agregados.add(exc.id)
        
        # Si el usuario tiene interés en comercios y seleccionó "tienda_ropa",
        # también incluir lugares de otras categorías que tengan el tag "ropa"
        if "comercios" in intereses and perfil.interes_tipo_comercios == "tienda_ropa":
            for exc in excursiones:
                if exc.id not in ids_agregados and exc.tiene_tag("ropa"):
                    if exc.coincide_con_perfil(perfil):
                        excursiones_filtradas.append(exc)
                        ids_agregados.add(exc.id)
        
        # Si no hay coincidencias exactas, retornar todas las de los intereses
        if not excursiones_filtradas:
            for exc in excursiones:
                if exc.categoria.lower() in categorias_interes or any(
                    cat in exc.categoria.lower() for cat in categorias_interes
                ):
                    excursiones_filtradas.append(exc)
                    ids_agregados.add(exc.id)
            
            # También agregar lugares con tag "ropa" si es tienda_ropa
            if "comercios" in intereses and perfil.interes_tipo_comercios == "tienda_ropa":
                for exc in excursiones:
                    if exc.id not in ids_agregados and exc.tiene_tag("ropa"):
                        excursiones_filtradas.append(exc)
                        ids_agregados.add(exc.id)
        
        return excursiones_filtradas
    
    @staticmethod
    def obtener_excursiones_por_intereses(
        ciudad: str,
        intereses: List[str],
        perfil: Optional[PerfilUsuario] = None
    ) -> List[Excursion]:
        """Obtiene excursiones filtradas por intereses y perfil"""
        todas_las_excursiones = ExcursionService.obtener_excursiones_por_ciudad(ciudad)
        
        # Mapeo de intereses a categorías (algunos intereses tienen nombres diferentes a las categorías)
        mapeo_interes_categoria = {
            "cultura": "cultural"  # El interés "cultura" se mapea a la categoría "cultural"
        }
        
        # Convertir intereses a categorías usando el mapeo
        categorias_interes = []
        for interes in intereses:
            categoria = mapeo_interes_categoria.get(interes.lower(), interes.lower())
            categorias_interes.append(categoria)
        
        if not perfil:
            # Si no hay perfil, solo filtrar por intereses
            return [
                exc for exc in todas_las_excursiones
                if exc.categoria.lower() in categorias_interes or any(
                    cat in exc.categoria.lower() for cat in categorias_interes
                )
            ]
        
        # Para filtrar por perfil, necesitamos usar las categorías mapeadas
        # Crear una lista temporal de intereses con las categorías mapeadas
        intereses_mapeados = [mapeo_interes_categoria.get(i.lower(), i.lower()) for i in intereses]
        return ExcursionService.filtrar_por_perfil(todas_las_excursiones, perfil, intereses_mapeados)
    
    @staticmethod
    def obtener_excursion_por_id(ciudad: str, id_excursion: str) -> Optional[Excursion]:
        """Obtiene una excursión específica por su ID"""
        todas_las_excursiones = ExcursionService.obtener_excursiones_por_ciudad(ciudad)
        for exc in todas_las_excursiones:
            if exc.id == id_excursion:
                return exc
        return None
    
    @staticmethod
    def obtener_categorias_disponibles(ciudad: str) -> List[str]:
        """Obtiene las categorías disponibles para una ciudad"""
        return obtener_todas_las_categorias(ciudad)

