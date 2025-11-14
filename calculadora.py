"""
Módulo de cálculos para Guerras Tribales
Incluye funciones para calcular distancias, tiempos de viaje, moral, etc.
"""

import math
from config_mundos import obtener_velocidad_tropa, obtener_config

# Velocidades de tropas en minutos por campo (configuración estándar)
# DEPRECATED: Usar obtener_velocidad_tropa() de config_mundos
VELOCIDADES_TROPAS = {
    'lanza': 18,
    'espada': 22,
    'hacha': 18,
    'arquero': 18,
    'explorador': 9,
    'caballeria_ligera': 10,
    'arquero_montado': 10,
    'caballeria_pesada': 11,
    'ariete': 30,
    'catapulta': 30,
    'paladin': 10,
    'noble': 35
}


def calcular_distancia(coord1, coord2):
    """
    Calcula la distancia euclidiana entre dos coordenadas.
    
    Args:
        coord1: tupla (x, y) de la primera coordenada
        coord2: tupla (x, y) de la segunda coordenada
    
    Returns:
        float: distancia en campos
    """
    x1, y1 = coord1
    x2, y2 = coord2
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)


def calcular_tiempo_viaje(distancia, tipo_tropa='noble', mundo='es95'):
    """
    Calcula el tiempo de viaje de una tropa.
    
    Args:
        distancia: distancia en campos
        tipo_tropa: tipo de tropa (por defecto 'noble')
        mundo: identificador del mundo (por defecto 'es95')
    
    Returns:
        float: tiempo en minutos
    """
    velocidad = obtener_velocidad_tropa(tipo_tropa, mundo)
    return distancia * velocidad


def calcular_moral(puntos_atacante, puntos_defensor):
    """
    Calcula la moral del ataque según las reglas de Guerras Tribales.
    
    Fórmula oficial (Moral 1): min((Puntos_Defensor / Puntos_Atacante) * 3 + 0.3, 1.0)
    
    Esta fórmula reduce la moral cuando se atacan jugadores más pequeños.
    Si el defensor tiene puntos similares o más que el atacante, la moral será 100%.
    
    Args:
        puntos_atacante: puntos del jugador atacante
        puntos_defensor: puntos del jugador defensor
    
    Returns:
        int: moral entre 30 y 100
    """
    # Si no hay datos de puntos, asumir 100%
    if puntos_atacante == 0 or puntos_defensor == 0:
        return 100
    
    # Fórmula oficial de Guerras Tribales (Moral 1 - basada solo en puntos)
    ratio = puntos_defensor / puntos_atacante
    moral_decimal = min(ratio * 3 + 0.3, 1.0)
    
    # Convertir a porcentaje (el resultado ya está entre 0.3 y 1.0)
    return int(moral_decimal * 100)


def tiempo_a_string(minutos):
    """
    Convierte minutos a formato legible (hh:mm:ss).
    
    Args:
        minutos: tiempo en minutos
    
    Returns:
        str: tiempo en formato hh:mm:ss
    """
    horas = int(minutos // 60)
    mins = int(minutos % 60)
    segs = int((minutos * 60) % 60)
    return f"{horas:02d}:{mins:02d}:{segs:02d}"


def parse_coordenadas(coord_str):
    """
    Convierte una cadena de coordenadas a tupla.
    
    Args:
        coord_str: string en formato "xxx|yyy"
    
    Returns:
        tuple: (x, y)
    """
    try:
        x, y = coord_str.split('|')
        return (int(x), int(y))
    except:
        raise ValueError(f"Formato de coordenadas inválido: {coord_str}. Use formato xxx|yyy")


def coordenadas_a_string(coord):
    """
    Convierte tupla de coordenadas a string.
    
    Args:
        coord: tupla (x, y)
    
    Returns:
        str: coordenadas en formato "xxx|yyy"
    """
    return f"{coord[0]}|{coord[1]}"


if __name__ == "__main__":
    # Pruebas básicas
    print("=== Pruebas de Calculadora ===\n")
    
    # Test distancia
    coord_a = (500, 500)
    coord_b = (510, 510)
    dist = calcular_distancia(coord_a, coord_b)
    print(f"Distancia entre {coordenadas_a_string(coord_a)} y {coordenadas_a_string(coord_b)}: {dist:.2f} campos")
    
    # Test tiempo de viaje
    tiempo = calcular_tiempo_viaje(dist, 'noble')
    print(f"Tiempo de viaje con noble: {tiempo_a_string(tiempo)}")
    
    # Test moral
    moral = calcular_moral(50000, 100000)
    print(f"Moral con 50k pts atacando 100k pts: {moral}%")
    
    # Test parse coordenadas
    coord_str = "500|500"
    coord_parsed = parse_coordenadas(coord_str)
    print(f"Coordenadas parseadas: {coord_str} -> {coord_parsed}")
