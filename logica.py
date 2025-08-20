# logica.py

def actualizar_estadisticas_jugador(jugador, calificaciones):
    """
    Calcula y actualiza las estadísticas de un jugador basándose en nuevas calificaciones.

    :param jugador: El objeto Jugador a actualizar.
    :param calificaciones: Un diccionario con las nuevas calificaciones de 'ataque', 'defensa', etc.
    """
    partidos_anteriores = jugador.partidos_jugados

    # Actualizar cada estadística usando el promedio ponderado
    # Si es el primer partido (partidos_anteriores == 0), el nuevo puntaje es simplemente la calificación.
    jugador.puntaje_ataque = ((jugador.puntaje_ataque * partidos_anteriores) + calificaciones['ataque']) / (partidos_anteriores + 1)
    jugador.puntaje_defensa = ((jugador.puntaje_defensa * partidos_anteriores) + calificaciones['defensa']) / (partidos_anteriores + 1)
    jugador.puntaje_fisico = ((jugador.puntaje_fisico * partidos_anteriores) + calificaciones['fisico']) / (partidos_anteriores + 1)
    jugador.puntaje_pases = ((jugador.puntaje_pases * partidos_anteriores) + calificaciones['pases']) / (partidos_anteriores + 1)
    jugador.puntaje_vision = ((jugador.puntaje_vision * partidos_anteriores) + calificaciones['vision']) / (partidos_anteriores + 1)

    # Incrementar el contador de partidos
    jugador.partidos_jugados += 1

    # Recalcular el puntaje global como el promedio de las demás estadísticas
    jugador.puntaje_global = (
        jugador.puntaje_ataque +
        jugador.puntaje_defensa +
        jugador.puntaje_fisico +
        jugador.puntaje_pases +
        jugador.puntaje_vision
    ) / 5

    # No es necesario devolver el jugador, ya que el objeto se modifica directamente.