from typing import Optional
from Models.usuario import Usuario
from Models.perfil_usuario import PerfilUsuario


# Diccionario global para almacenar usuarios en memoria
USUARIOS = {}


class UsuarioService:
    @staticmethod
    def obtener_o_crear_usuario(telefono: str, nombre: Optional[str] = None) -> Usuario:
        """Obtiene un usuario existente o crea uno nuevo"""
        telefono_normalizado = telefono.strip()
        
        if telefono_normalizado in USUARIOS:
            usuario = USUARIOS[telefono_normalizado]
            usuario.actualizar_ultima_interaccion()
            # Asegurar que tenga ciudad asignada
            if not usuario.ciudad:
                usuario.ciudad = "Colonia"
                UsuarioService.actualizar_usuario(usuario)
            return usuario
        
        # Crear nuevo usuario con Colonia por defecto
        usuario = Usuario(
            telefono=telefono_normalizado,
            nombre=nombre,
            ciudad="Colonia",  # Ciudad por defecto
            estado_conversacion="INICIO"
        )
        USUARIOS[telefono_normalizado] = usuario
        return usuario
    
    @staticmethod
    def obtener_usuario_por_telefono(telefono: str) -> Optional[Usuario]:
        """Obtiene un usuario por su teléfono"""
        telefono_normalizado = telefono.strip()
        return USUARIOS.get(telefono_normalizado)
    
    @staticmethod
    def actualizar_usuario(usuario: Usuario):
        """Actualiza un usuario existente"""
        telefono_normalizado = usuario.telefono.strip()
        usuario.actualizar_ultima_interaccion()
        USUARIOS[telefono_normalizado] = usuario
    
    @staticmethod
    def actualizar_nombre(telefono: str, nombre: str):
        """Actualiza el nombre de un usuario"""
        usuario = UsuarioService.obtener_usuario_por_telefono(telefono)
        if usuario:
            usuario.nombre = nombre
            UsuarioService.actualizar_usuario(usuario)
    
    @staticmethod
    def actualizar_ciudad(telefono: str, ciudad: str):
        """Actualiza la ciudad de un usuario"""
        usuario = UsuarioService.obtener_usuario_por_telefono(telefono)
        if usuario:
            usuario.ciudad = ciudad
            UsuarioService.actualizar_usuario(usuario)
    
    @staticmethod
    def agregar_interes(telefono: str, interes: str):
        """Agrega un interés a un usuario"""
        usuario = UsuarioService.obtener_usuario_por_telefono(telefono)
        if usuario:
            usuario.agregar_interes(interes)
            UsuarioService.actualizar_usuario(usuario)
    
    @staticmethod
    def inicializar_perfil(telefono: str):
        """Inicializa el perfil de un usuario si no existe"""
        usuario = UsuarioService.obtener_usuario_por_telefono(telefono)
        if usuario and not usuario.perfil:
            usuario.perfil = PerfilUsuario()
            UsuarioService.actualizar_usuario(usuario)
    
    @staticmethod
    def actualizar_perfil(telefono: str, campo: str, valor):
        """Actualiza un campo específico del perfil de un usuario"""
        usuario = UsuarioService.obtener_usuario_por_telefono(telefono)
        if usuario:
            if not usuario.perfil:
                usuario.perfil = PerfilUsuario()
            usuario.perfil.actualizar_campo(campo, valor)
            UsuarioService.actualizar_usuario(usuario)
    
    @staticmethod
    def actualizar_estado_conversacion(telefono: str, estado: str):
        """Actualiza el estado de conversación de un usuario"""
        usuario = UsuarioService.obtener_usuario_por_telefono(telefono)
        if usuario:
            usuario.estado_conversacion = estado
            UsuarioService.actualizar_usuario(usuario)
    
    @staticmethod
    def agregar_lugar_enviado(telefono: str, lugar_id: str, interes: str):
        """
        Agrega un lugar enviado al usuario.
        
        Args:
            telefono: Teléfono del usuario
            lugar_id: ID del lugar enviado
            interes: Interés al que pertenece el lugar (restaurantes, comercios, compras, cultura)
        """
        usuario = UsuarioService.obtener_usuario_por_telefono(telefono)
        if usuario:
            usuario.agregar_lugar_enviado(lugar_id, interes)
            UsuarioService.actualizar_usuario(usuario)
    
    @staticmethod
    def agregar_lugares_enviados(telefono: str, lugares: list, interes: str):
        """
        Agrega múltiples lugares enviados al usuario.
        
        Args:
            telefono: Teléfono del usuario
            lugares: Lista de IDs de lugares enviados
            interes: Interés al que pertenecen los lugares
        """
        usuario = UsuarioService.obtener_usuario_por_telefono(telefono)
        if usuario:
            for lugar_id in lugares:
                usuario.agregar_lugar_enviado(lugar_id, interes)
            UsuarioService.actualizar_usuario(usuario)
    
    @staticmethod
    def obtener_todos_los_usuarios() -> list:
        """Obtiene todos los usuarios (útil para debugging)"""
        return list(USUARIOS.values())

