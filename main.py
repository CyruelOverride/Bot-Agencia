from Models.chat import Chat


def crear_bot_instancia():
    """
    Crea una instancia del bot de viaje para testing.
    """
    bot = Chat()
    return bot  


bot = crear_bot_instancia()


if __name__ == "__main__":
    print("Bot Asistente de Viaje iniciado")
    print(f"Estado del bot: {bot}")
