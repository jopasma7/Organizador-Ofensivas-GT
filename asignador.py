"""
Módulo de asignación de ataques
Asigna pueblos atacantes a objetivos de manera optimizada
"""

from calculadora import calcular_distancia, calcular_tiempo_viaje, calcular_moral, coordenadas_a_string, tiempo_a_string
from datetime import datetime, timedelta


def asignar_ataques_por_distancia(pueblos_atacantes, objetivos, ataques_por_objetivo=5, mundo='es95', tipo_tropa='noble'):
    """
    Asigna ataques a objetivos priorizando la menor distancia.
    
    Args:
        pueblos_atacantes: lista de pueblos disponibles para atacar
        objetivos: lista de objetivos a atacar
        ataques_por_objetivo: número de ataques a asignar por objetivo
        mundo: identificador del mundo para calcular tiempos
        tipo_tropa: tipo de tropa para calcular tiempos de viaje
    
    Returns:
        dict: plan de ataque con asignaciones
    """
    plan = {
        'fecha_creacion': datetime.now().isoformat(),
        'mundo': mundo,
        'tipo_tropa': tipo_tropa,
        'objetivos': [],
        'pueblos_sin_asignar': []
    }
    
    pueblos_disponibles = pueblos_atacantes.copy()
    
    # Ordenar objetivos por prioridad
    objetivos_ordenados = sorted(objetivos, key=lambda x: x.get('prioridad', 1))
    
    for objetivo in objetivos_ordenados:
        coord_objetivo = objetivo['coordenadas']
        ataques_asignados = []
        
        # Calcular distancias de todos los pueblos disponibles a este objetivo
        distancias = []
        for pueblo in pueblos_disponibles:
            distancia = calcular_distancia(pueblo['coordenadas'], coord_objetivo)
            distancias.append((pueblo, distancia))
        
        # Ordenar por distancia
        distancias.sort(key=lambda x: x[1])
        
        # Asignar los N pueblos más cercanos
        for i in range(min(ataques_por_objetivo, len(distancias))):
            pueblo, distancia = distancias[i]
            
            tiempo_viaje_mins = calcular_tiempo_viaje(distancia, tipo_tropa, mundo)
            
            ataque = {
                'pueblo_atacante': coordenadas_a_string(pueblo['coordenadas']),
                'nombre_pueblo': pueblo['nombre'],
                'jugador': pueblo['jugador'],
                'distancia': round(distancia, 2),
                'tiempo_viaje': tiempo_a_string(tiempo_viaje_mins),
                'tiempo_viaje_minutos': round(tiempo_viaje_mins, 2),
                'moral': calcular_moral(pueblo['puntos_jugador'], objetivo['puntos_defensor'])
            }
            
            # Preservar información adicional si existe
            if 'tipo_off' in pueblo:
                ataque['tipo_off'] = pueblo['tipo_off']
            if 'tropas' in pueblo:
                ataque['tropas'] = pueblo['tropas']
            if 'poblacion_ofensiva' in pueblo:
                ataque['poblacion_ofensiva'] = pueblo['poblacion_ofensiva']
            
            ataques_asignados.append(ataque)
            pueblos_disponibles.remove(pueblo)
        
        plan['objetivos'].append({
            'coordenadas': coordenadas_a_string(coord_objetivo),
            'nombre': objetivo['nombre'],
            'prioridad': objetivo.get('prioridad', 1),
            'jugador_defensor': objetivo.get('jugador_defensor', 'Desconocido'),
            'ataques': ataques_asignados,
            'ataques_asignados': len(ataques_asignados)
        })
    
    # Pueblos que no fueron asignados
    plan['pueblos_sin_asignar'] = [
        {
            'coordenadas': coordenadas_a_string(p['coordenadas']),
            'nombre': p['nombre'],
            'jugador': p['jugador']
        }
        for p in pueblos_disponibles
    ]
    
    return plan


def asignar_con_sincronizacion(pueblos_atacantes, objetivos, hora_llegada, ataques_por_objetivo=5, mundo='es95', tipo_tropa='noble'):
    """
    Asigna ataques sincronizados para llegar a una hora específica.
    
    Args:
        pueblos_atacantes: lista de pueblos disponibles
        objetivos: lista de objetivos
        hora_llegada: datetime con la hora de llegada deseada
        ataques_por_objetivo: número de ataques por objetivo
        mundo: identificador del mundo
        tipo_tropa: tipo de tropa para calcular tiempos
    
    Returns:
        dict: plan de ataque con horarios de envío
    """
    plan_base = asignar_ataques_por_distancia(pueblos_atacantes, objetivos, ataques_por_objetivo, mundo, tipo_tropa)
    
    # Calcular hora de envío para cada ataque
    for objetivo in plan_base['objetivos']:
        for ataque in objetivo['ataques']:
            tiempo_viaje_minutos = ataque['tiempo_viaje_minutos']
            hora_envio = hora_llegada - timedelta(minutes=tiempo_viaje_minutos)
            
            ataque['hora_llegada'] = hora_llegada.strftime('%Y-%m-%d %H:%M:%S')
            ataque['hora_envio'] = hora_envio.strftime('%Y-%m-%d %H:%M:%S')
    
    plan_base['hora_llegada_objetivo'] = hora_llegada.strftime('%Y-%m-%d %H:%M:%S')
    
    return plan_base


def balancear_por_jugador(pueblos_atacantes, objetivos, ataques_por_objetivo=5, mundo='es95', tipo_tropa='noble'):
    """
    Asigna ataques balanceando la carga entre jugadores.
    
    Args:
        pueblos_atacantes: lista de pueblos disponibles
        objetivos: lista de objetivos
        ataques_por_objetivo: ataques por objetivo
        mundo: identificador del mundo
        tipo_tropa: tipo de tropa para calcular tiempos
    
    Returns:
        dict: plan balanceado
    """
    # Contar pueblos por jugador
    pueblos_por_jugador = {}
    for pueblo in pueblos_atacantes:
        jugador = pueblo['jugador']
        if jugador not in pueblos_por_jugador:
            pueblos_por_jugador[jugador] = []
        pueblos_por_jugador[jugador].append(pueblo)
    
    # Contador de ataques asignados por jugador
    ataques_por_jugador = {jugador: 0 for jugador in pueblos_por_jugador.keys()}
    
    plan = {
        'fecha_creacion': datetime.now().isoformat(),
        'mundo': mundo,
        'tipo_tropa': tipo_tropa,
        'objetivos': [],
        'pueblos_sin_asignar': [],
        'balance_jugadores': {}
    }
    
    for objetivo in objetivos:
        coord_objetivo = objetivo['coordenadas']
        ataques_asignados = []
        
        # Asignar ataques priorizando jugadores con menos ataques
        for _ in range(ataques_por_objetivo):
            mejor_ataque = None
            mejor_distancia = float('inf')
            mejor_jugador = None
            mejor_pueblo = None
            
            # Buscar el mejor pueblo de cada jugador
            for jugador, pueblos in pueblos_por_jugador.items():
                if not pueblos:
                    continue
                
                # Bonus para jugadores con menos ataques asignados
                peso_jugador = 1 + (ataques_por_jugador[jugador] * 0.1)
                
                for pueblo in pueblos:
                    distancia = calcular_distancia(pueblo['coordenadas'], coord_objetivo) * peso_jugador
                    
                    if distancia < mejor_distancia:
                        mejor_distancia = distancia
                        mejor_jugador = jugador
                        mejor_pueblo = pueblo
            
            if mejor_pueblo:
                distancia_real = calcular_distancia(mejor_pueblo['coordenadas'], coord_objetivo)
                tiempo_viaje_mins = calcular_tiempo_viaje(distancia_real, tipo_tropa, mundo)
                
                ataque = {
                    'pueblo_atacante': coordenadas_a_string(mejor_pueblo['coordenadas']),
                    'nombre_pueblo': mejor_pueblo['nombre'],
                    'jugador': mejor_pueblo['jugador'],
                    'distancia': round(distancia_real, 2),
                    'tiempo_viaje': tiempo_a_string(tiempo_viaje_mins),
                    'moral': calcular_moral(mejor_pueblo['puntos_jugador'], objetivo['puntos_defensor'])
                }
                
                # Preservar información adicional si existe
                if 'tipo_off' in mejor_pueblo:
                    ataque['tipo_off'] = mejor_pueblo['tipo_off']
                if 'tropas' in mejor_pueblo:
                    ataque['tropas'] = mejor_pueblo['tropas']
                if 'poblacion_ofensiva' in mejor_pueblo:
                    ataque['poblacion_ofensiva'] = mejor_pueblo['poblacion_ofensiva']
                
                ataques_asignados.append(ataque)
                pueblos_por_jugador[mejor_jugador].remove(mejor_pueblo)
                ataques_por_jugador[mejor_jugador] += 1
        
        plan['objetivos'].append({
            'coordenadas': coordenadas_a_string(coord_objetivo),
            'nombre': objetivo['nombre'],
            'prioridad': objetivo.get('prioridad', 1),
            'ataques': ataques_asignados
        })
    
    plan['balance_jugadores'] = ataques_por_jugador
    
    return plan


def asignar_optimizando_moral(pueblos_atacantes, objetivos, ataques_por_objetivo=5, mundo='es95', tipo_tropa='noble', hora_llegada=None):
    """
    Asigna ataques optimizando la moral del plan.
    
    ESTRATEGIA CORRECTA:
    - Jugadores PEQUEÑOS → Objetivos PEQUEÑOS (moral alta 90-100%)
    - Jugadores GRANDES → Objetivos GRANDES (moral alta 100%)
    - EVITAR: Jugadores grandes contra objetivos pequeños (moral baja 30-40%)
    
    El algoritmo asigna cada ofensiva al objetivo donde tendrá la MEJOR moral posible,
    priorizando las asignaciones donde la moral sea más alta.
    
    Args:
        pueblos_atacantes: lista de pueblos disponibles para atacar
        objetivos: lista de objetivos a atacar
        ataques_por_objetivo: número de ataques por objetivo (puede ser int o dict)
            - Si es int: mismo número para todos los objetivos
            - Si es dict: {coord_string: numero} para personalizar por objetivo
        mundo: identificador del mundo para calcular tiempos
        tipo_tropa: tipo de tropa para calcular tiempos de viaje
        hora_llegada: (opcional) datetime para sincronizar llegadas
    
    Returns:
        dict: plan de ataque optimizado por moral
    """
    plan = {
        'fecha_creacion': datetime.now().isoformat(),
        'mundo': mundo,
        'tipo_tropa': tipo_tropa,
        'objetivos': [],
        'pueblos_sin_asignar': [],
        'estadisticas_moral': {
            'moral_promedio': 0,
            'ataques_100_moral': 0,
            'ataques_baja_moral': 0  # < 50%
        }
    }
    
    # Si hay hora de llegada, agregarla al plan
    if hora_llegada:
        plan['hora_llegada_objetivo'] = hora_llegada.strftime('%d/%m/%Y %H:%M:%S')
    
    # Crear estructura para trackear cuántos ataques necesita cada objetivo
    objetivos_info = []
    for objetivo in objetivos:
        # Determinar cuántos ataques necesita este objetivo
        if isinstance(ataques_por_objetivo, dict):
            coord_str = coordenadas_a_string(objetivo['coordenadas'])
            num_ataques = ataques_por_objetivo.get(coord_str, 5)
        else:
            num_ataques = ataques_por_objetivo
        
        objetivos_info.append({
            'objetivo': objetivo,
            'ataques_necesarios': num_ataques,
            'ataques_asignados': []
        })
    
    pueblos_disponibles = pueblos_atacantes.copy()
    
    # Mientras haya pueblos disponibles y objetivos que necesiten ataques
    while pueblos_disponibles:
        # Verificar si quedan objetivos por completar
        objetivos_incompletos = [obj for obj in objetivos_info if obj['ataques_necesarios'] > 0]
        if not objetivos_incompletos:
            break
        
        # Para cada pueblo disponible, encontrar su MEJOR asignación
        mejor_asignacion = None
        mejor_moral = -1
        mejor_poblacion = -1
        mejor_pueblo = None
        mejor_objetivo_idx = None
        
        for pueblo in pueblos_disponibles:
            puntos_atacante = pueblo.get('puntos_jugador', 0)
            
            # Calcular población total de este pueblo (si tiene tropas)
            poblacion_total = pueblo.get('poblacion_ofensiva', 0)
            if poblacion_total == 0 and 'tropas' in pueblo:
                # Calcular población desde tropas
                tropas = pueblo['tropas']
                poblacion_total = (
                    tropas.get('hachas', 0) +
                    tropas.get('ligeras', 0) +
                    tropas.get('arq_caballo', 0) +
                    tropas.get('arietes', 0) +
                    tropas.get('catapultas', 0)
                )
            
            # Evaluar este pueblo contra todos los objetivos incompletos
            for idx, obj_info in enumerate(objetivos_info):
                if obj_info['ataques_necesarios'] <= 0:
                    continue
                
                objetivo = obj_info['objetivo']
                puntos_defensor = objetivo.get('puntos_defensor', 0)
                
                # Calcular moral para esta combinación
                moral = calcular_moral(puntos_atacante, puntos_defensor)
                
                # PRIORIDAD 1: Moral (usar >= 90% como "buena moral")
                # PRIORIDAD 2: Población de tropas (más grande = mejor)
                
                # Determinar si esta combinación es mejor que la actual
                es_mejor = False
                
                if moral > mejor_moral:
                    # Moral claramente mejor
                    es_mejor = True
                elif moral == mejor_moral and poblacion_total > mejor_poblacion:
                    # Misma moral, pero más tropas
                    es_mejor = True
                
                if es_mejor:
                    mejor_moral = moral
                    mejor_poblacion = poblacion_total
                    mejor_pueblo = pueblo
                    mejor_objetivo_idx = idx
                    
                    # Calcular datos del ataque
                    coord_objetivo = objetivo['coordenadas']
                    distancia = calcular_distancia(pueblo['coordenadas'], coord_objetivo)
                    tiempo_viaje_mins = calcular_tiempo_viaje(distancia, tipo_tropa, mundo)
                    
                    mejor_asignacion = {
                        'pueblo_atacante': coordenadas_a_string(pueblo['coordenadas']),
                        'nombre_pueblo': pueblo['nombre'],
                        'jugador': pueblo['jugador'],
                        'distancia': round(distancia, 2),
                        'tiempo_viaje': tiempo_a_string(tiempo_viaje_mins),
                        'tiempo_viaje_minutos': round(tiempo_viaje_mins, 2),
                        'moral': moral
                    }
                    
                    # Si hay hora de llegada, calcular hora de envío
                    if hora_llegada:
                        hora_envio = hora_llegada - timedelta(minutes=tiempo_viaje_mins)
                        mejor_asignacion['hora_llegada'] = hora_llegada.strftime('%d/%m/%Y %H:%M:%S')
                        mejor_asignacion['hora_envio'] = hora_envio.strftime('%d/%m/%Y %H:%M:%S')
                    
                    # Preservar información adicional si existe
                    if 'tipo_off' in pueblo:
                        mejor_asignacion['tipo_off'] = pueblo['tipo_off']
                    if 'tropas' in pueblo:
                        mejor_asignacion['tropas'] = pueblo['tropas']
                    if 'poblacion_ofensiva' in pueblo:
                        mejor_asignacion['poblacion_ofensiva'] = pueblo['poblacion_ofensiva']
        
        # Asignar la mejor combinación encontrada
        if mejor_asignacion:
            objetivos_info[mejor_objetivo_idx]['ataques_asignados'].append(mejor_asignacion)
            objetivos_info[mejor_objetivo_idx]['ataques_necesarios'] -= 1
            pueblos_disponibles.remove(mejor_pueblo)
            
            # Actualizar estadísticas
            plan['estadisticas_moral']['moral_promedio'] += mejor_moral
            if mejor_moral == 100:
                plan['estadisticas_moral']['ataques_100_moral'] += 1
            elif mejor_moral < 50:
                plan['estadisticas_moral']['ataques_baja_moral'] += 1
        else:
            break
    
    # Construir el plan final
    total_ataques = 0
    for obj_info in objetivos_info:
        objetivo = obj_info['objetivo']
        ataques = obj_info['ataques_asignados']
        
        plan['objetivos'].append({
            'coordenadas': coordenadas_a_string(objetivo['coordenadas']),
            'nombre': objetivo['nombre'],
            'prioridad': objetivo.get('prioridad', 1),
            'jugador_defensor': objetivo.get('jugador_defensor', 'Desconocido'),
            'ataques': ataques,
            'ataques_asignados': len(ataques)
        })
        
        total_ataques += len(ataques)
    
    # Calcular moral promedio
    if total_ataques > 0:
        plan['estadisticas_moral']['moral_promedio'] = round(
            plan['estadisticas_moral']['moral_promedio'] / total_ataques, 1
        )
    
    # Pueblos no asignados
    plan['pueblos_sin_asignar'] = [
        {
            'coordenadas': coordenadas_a_string(p['coordenadas']),
            'nombre': p['nombre'],
            'jugador': p['jugador']
        }
        for p in pueblos_disponibles
    ]
    
    return plan


if __name__ == "__main__":
    print("=== Módulo de Asignación ===")
    print("Importa este módulo desde main.py para usar las funciones de asignación")
