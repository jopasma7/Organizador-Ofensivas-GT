"""
Ejemplo usando el CSV de ofensivas de tribu
"""

from importador import leer_csv_ofensivas, parse_coordenadas_lista
from asignador import asignar_ataques_por_distancia
from exportador import mostrar_resumen_consola, exportar_comandos_texto

print("="*80)
print("🎯 EJEMPLO: Planificar ataque usando CSV de tribu")
print("="*80)

# Paso 1: Cargar OFFs FULL desde CSV
print("\n📍 PASO 1: Cargar OFFs FULL")
print("-"*80)

pueblos = leer_csv_ofensivas("ofensivas_tribu_es95 (1).csv", "FULL")
print(f"✅ {len(pueblos)} OFFs FULL disponibles")

# Paso 2: Definir objetivos (ejemplo)
print("\n🎯 PASO 2: Definir objetivos")
print("-"*80)

# Objetivos de ejemplo
coordenadas_objetivos = "520|600 521|601 522|602"
objetivos_temp = parse_coordenadas_lista(coordenadas_objetivos)

objetivos = []
for obj in objetivos_temp:
    objetivos.append({
        'coordenadas': obj['coordenadas'],
        'nombre': f"Objetivo {obj['coordenadas'][0]}|{obj['coordenadas'][1]}",
        'prioridad': 1,
        'jugador_defensor': 'Enemigo',
        'puntos_defensor': 80000,
        'ataques_asignados': []
    })

print(f"✅ {len(objetivos)} objetivos definidos")

# Paso 3: Generar plan (usando solo 10 pueblos más cercanos para el ejemplo)
print("\n⚙️  PASO 3: Generar plan de ataque")
print("-"*80)

# Limitar a 10 pueblos para el ejemplo
pueblos_ejemplo = pueblos[:20]

plan = asignar_ataques_por_distancia(
    pueblos_ejemplo, 
    objetivos, 
    ataques_por_objetivo=5,
    mundo='es95',
    tipo_tropa='noble'
)

# Paso 4: Mostrar resumen
mostrar_resumen_consola(plan)

# Paso 5: Exportar
print("\n💾 PASO 5: Exportar plan")
print("-"*80)

exportar_comandos_texto(plan, "plan_csv_ejemplo.txt")

print("\n" + "="*80)
print("✅ Ejemplo completado")
print("💡 El plan incluye información de tropas de cada OFF")
print("="*80)
