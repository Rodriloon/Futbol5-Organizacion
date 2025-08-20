def actualizar_estadisticas_jugador(jugador, calificaciones_promedio_partido):
    """
    Calcula y actualiza las estadísticas de un jugador basándose en el promedio
    de calificaciones de su último partido.

    :param jugador: El objeto Jugador a actualizar.
    :param calificaciones_promedio_partido: Un diccionario con los promedios de 'ataque', 'defensa', etc.
    """
    partidos_anteriores = jugador.partidos_jugados

    # Actualizar cada estadística usando el promedio ponderado
    jugador.puntaje_ataque = ((jugador.puntaje_ataque * partidos_anteriores) + calificaciones_promedio_partido['ataque']) / (partidos_anteriores + 1)
    jugador.puntaje_defensa = ((jugador.puntaje_defensa * partidos_anteriores) + calificaciones_promedio_partido['defensa']) / (partidos_anteriores + 1)
    jugador.puntaje_fisico = ((jugador.puntaje_fisico * partidos_anteriores) + calificaciones_promedio_partido['fisico']) / (partidos_anteriores + 1)
    jugador.puntaje_pases = ((jugador.puntaje_pases * partidos_anteriores) + calificaciones_promedio_partido['pases']) / (partidos_anteriores + 1)
    jugador.puntaje_vision = ((jugador.puntaje_vision * partidos_anteriores) + calificaciones_promedio_partido['vision']) / (partidos_anteriores + 1)

    # Incrementar el contador de partidos JUGADOS. Esto podría necesitar un ajuste.
    # Lo ideal sería marcar un partido como "finalizado" y que esto se incremente una sola vez.
    # Por ahora, lo dejamos así para simplicidad.
    jugador.partidos_jugados += 1

    # Recalcular el puntaje global
    jugador.puntaje_global = (
        jugador.puntaje_ataque +
        jugador.puntaje_defensa +
        jugador.puntaje_fisico +
        jugador.puntaje_pases +
        jugador.puntaje_vision
    ) / 5

def crear_equipos_balanceados(jugadores_seleccionados):
    """
    Divide una lista de jugadores en dos equipos balanceados por puntaje global.

    :param jugadores_seleccionados: Una lista de objetos Jugador.
    :return: Un diccionario con 'equipo_a' y 'equipo_b'.
    """
    # Ordenar jugadores de mayor a menor puntaje global
    jugadores_ordenados = sorted(jugadores_seleccionados, key=lambda j: j.puntaje_global, reverse=True)

    equipo_a = []
    equipo_b = []

    # Distribuir jugadores usando el método de serpiente
    for i, jugador in enumerate(jugadores_ordenados):
        if i % 4 == 0 or i % 4 == 3:
            equipo_a.append(jugador)  # Jugadores 1, 4, 5, 8...
        else:
            equipo_b.append(jugador)  # Jugadores 2, 3, 6, 7...

    return {'equipo_a': equipo_a, 'equipo_b': equipo_b}