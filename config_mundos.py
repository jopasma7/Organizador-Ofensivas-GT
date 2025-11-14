"""
Configuración de mundos de Guerras Tribales
Datos obtenidos de TWStats
"""

# Configuraciones disponibles por mundo
CONFIGURACIONES_MUNDOS = {
    'es95': {
        'nombre': 'Mundo ES95',
        'velocidad': 1,
        'modificador_velocidad_unidad': 1,
        'moral_activada': True,
        'arqueros_activados': True,
        'paladin_activado': True,
        'distancia_maxima_nobles': 70,
        'proteccion_principiantes_dias': 5,
        'destruccion_edificios': True
    },
    'estandar': {
        'nombre': 'Configuración Estándar',
        'velocidad': 1,
        'modificador_velocidad_unidad': 1,
        'moral_activada': True,
        'arqueros_activados': True,
        'paladin_activado': True,
        'distancia_maxima_nobles': 100,
        'proteccion_principiantes_dias': 3,
        'destruccion_edificios': True
    },
    'rapido': {
        'nombre': 'Mundo Rápido',
        'velocidad': 2,
        'modificador_velocidad_unidad': 2,
        'moral_activada': True,
        'arqueros_activados': True,
        'paladin_activado': True,
        'distancia_maxima_nobles': 100,
        'proteccion_principiantes_dias': 3,
        'destruccion_edificios': True
    }
}

# Velocidades de tropas en minutos por campo (configuración estándar)
# Estos valores se multiplican por el modificador del mundo
VELOCIDADES_TROPAS_BASE = {
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

# Configuración actual (se puede cambiar en runtime)
CONFIG_ACTUAL = 'es95'


def obtener_config(mundo='es95'):
    """
    Obtiene la configuración de un mundo específico.
    
    Args:
        mundo: identificador del mundo (por defecto 'es95')
    
    Returns:
        dict: configuración del mundo
    """
    return CONFIGURACIONES_MUNDOS.get(mundo, CONFIGURACIONES_MUNDOS['estandar'])


def obtener_velocidad_tropa(tipo_tropa, mundo='es95'):
    """
    Obtiene la velocidad de una tropa para un mundo específico.
    
    Args:
        tipo_tropa: tipo de tropa
        mundo: identificador del mundo
    
    Returns:
        float: minutos por campo
    """
    config = obtener_config(mundo)
    velocidad_base = VELOCIDADES_TROPAS_BASE.get(tipo_tropa, 30)
    modificador = config['modificador_velocidad_unidad']
    
    return velocidad_base / modificador


def listar_mundos_disponibles():
    """
    Lista todos los mundos configurados.
    
    Returns:
        list: lista de tuplas (id, nombre)
    """
    return [(id_mundo, config['nombre']) for id_mundo, config in CONFIGURACIONES_MUNDOS.items()]


def agregar_mundo(id_mundo, config):
    """
    Agrega o actualiza la configuración de un mundo.
    
    Args:
        id_mundo: identificador del mundo
        config: diccionario con la configuración
    """
    CONFIGURACIONES_MUNDOS[id_mundo] = config
    print(f"✅ Configuración de '{id_mundo}' agregada/actualizada")


if __name__ == "__main__":
    print("="*80)
    print("📋 CONFIGURACIONES DE MUNDOS DISPONIBLES")
    print("="*80)
    
    for id_mundo, nombre in listar_mundos_disponibles():
        config = obtener_config(id_mundo)
        print(f"\n{nombre} ({id_mundo}):")
        print(f"  - Velocidad: {config['velocidad']}x")
        print(f"  - Velocidad unidades: {config['modificador_velocidad_unidad']}x")
        print(f"  - Moral: {'Sí' if config['moral_activada'] else 'No'}")
        print(f"  - Distancia nobles: {config['distancia_maxima_nobles']} campos")
    
    print("\n" + "="*80)
    print("VELOCIDADES DE TROPAS (ES95)")
    print("="*80)
    
    for tropa, velocidad in VELOCIDADES_TROPAS_BASE.items():
        vel_mundo = obtener_velocidad_tropa(tropa, 'es95')
        print(f"  {tropa:20} {vel_mundo:.1f} min/campo")
