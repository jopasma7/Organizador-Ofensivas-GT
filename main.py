"""
Organizador de Ofensivas - Guerras Tribales
Programa para planificar y asignar ataques de manera optimizada
"""

import os
from datetime import datetime, timedelta
from importador import (
    leer_pueblos_desde_archivo, 
    leer_objetivos_desde_archivo,
    crear_archivo_ejemplo_pueblos,
    crear_archivo_ejemplo_objetivos,
    guardar_plan_json,
    cargar_plan_json
)
from asignador import (
    asignar_ataques_por_distancia,
    asignar_con_sincronizacion,
    balancear_por_jugador,
    asignar_optimizando_moral
)
from exportador import (
    exportar_comandos_texto,
    exportar_para_copiar,
    exportar_bbcode,
    mostrar_resumen_consola
)


def limpiar_pantalla():
    """Limpia la consola"""
    os.system('cls' if os.name == 'nt' else 'clear')


def menu_principal():
    """Menú principal del programa"""
    while True:
        limpiar_pantalla()
        print("="*80)
        print("🏰 ORGANIZADOR DE OFENSIVAS - GUERRAS TRIBALES")
        print("="*80)
        print("\n📋 MENÚ PRINCIPAL\n")
        print("  1️⃣  Crear Plan de Ataque")
        print("  2️⃣  Cargar Plan Existente")
        print("  3️⃣  Crear Archivos de Ejemplo")
        print("  4️⃣  Pruebas y Cálculos")
        print("  0️⃣  Salir")
        print("\n" + "="*80)
        
        opcion = input("\n👉 Selecciona una opción: ").strip()
        
        if opcion == "1":
            menu_crear_plan()
        elif opcion == "2":
            menu_cargar_plan()
        elif opcion == "3":
            menu_crear_ejemplos()
        elif opcion == "4":
            menu_pruebas()
        elif opcion == "0":
            print("\n👋 ¡Hasta luego!")
            break
        else:
            print("\n❌ Opción inválida")
            input("\nPresiona Enter para continuar...")


def menu_crear_plan():
    """Menú para crear un nuevo plan de ataque"""
    limpiar_pantalla()
    print("="*80)
    print("📝 CREAR PLAN DE ATAQUE")
    print("="*80)
    
    # Seleccionar mundo
    from config_mundos import listar_mundos_disponibles, obtener_config
    
    print("\n🌍 Paso 0: Seleccionar mundo")
    print("-"*80)
    mundos = listar_mundos_disponibles()
    
    for idx, (id_mundo, nombre) in enumerate(mundos, 1):
        config = obtener_config(id_mundo)
        print(f"  {idx}. {nombre} (Velocidad: {config['velocidad']}x)")
    
    try:
        seleccion = input(f"\n👉 Selecciona mundo (Enter para 1): ").strip() or "1"
        idx_mundo = int(seleccion) - 1
        if 0 <= idx_mundo < len(mundos):
            mundo_seleccionado = mundos[idx_mundo][0]
            config_mundo = obtener_config(mundo_seleccionado)
            print(f"✅ Mundo seleccionado: {config_mundo['nombre']}")
        else:
            mundo_seleccionado = 'es95'
            print(f"⚠️  Selección inválida, usando ES95")
    except:
        mundo_seleccionado = 'es95'
        print(f"⚠️  Selección inválida, usando ES95")
    
    # Cargar pueblos atacantes
    print("\n📍 Paso 1: Cargar pueblos atacantes")
    print("  1. Desde archivo de texto")
    print("  2. Desde CSV de ofensivas de tribu")
    print("  3. Pegar coordenadas directamente")
    
    opcion_pueblos = input("\n👉 Selecciona una opción (Enter para 1): ").strip() or "1"
    
    pueblos = []
    
    if opcion_pueblos == "1":
        archivo_pueblos = input("\nRuta del archivo (Enter para 'data/pueblos.txt'): ").strip()
        if not archivo_pueblos:
            archivo_pueblos = "data/pueblos.txt"
        pueblos = leer_pueblos_desde_archivo(archivo_pueblos)
    
    elif opcion_pueblos == "2":
        from importador import leer_csv_ofensivas
        archivo_csv = input("\nRuta del archivo CSV (Enter para buscar en carpeta actual): ").strip()
        if not archivo_csv:
            archivo_csv = "ofensivas_tribu_es95 (1).csv"
        
        print("\n🎯 Filtrar por tipo de OFF:")
        print("  1. FULL (ofensivas completas)")
        print("  2. MEDIA (ofensivas medias)")
        print("  3. Todas")
        
        filtro = input("\n👉 Selecciona filtro (Enter para 3): ").strip() or "3"
        
        tipo_filtro = None
        if filtro == "1":
            tipo_filtro = "FULL"
        elif filtro == "2":
            tipo_filtro = "MEDIA"
        
        # Siempre usar API para obtener puntos (necesario para calcular moral)
        print("\n🌍 Consultando API para obtener puntos de jugadores (necesario para moral)...")
        pueblos = leer_csv_ofensivas(archivo_csv, tipo_filtro, mundo=mundo_seleccionado, usar_api=True)
    
    elif opcion_pueblos == "3":
        print("\n📋 Pega las coordenadas separadas por espacios")
        print("Formato: 480|571 479|570 479|572 ...")
        print("También puedes incluir más datos: 480|571|NombrePueblo|Jugador|50000")
        coordenadas_texto = input("\n👉 Coordenadas: ").strip()
        
        if coordenadas_texto:
            from importador import parse_coordenadas_lista
            pueblos = parse_coordenadas_lista(coordenadas_texto)
            if pueblos:
                print(f"✅ {len(pueblos)} pueblos cargados desde coordenadas")
        else:
            print("\n❌ No se ingresaron coordenadas")
    
    if not pueblos:
        print("\n❌ No se pudieron cargar los pueblos")
        input("\nPresiona Enter para continuar...")
        return
    
    # Cargar objetivos (siempre desde archivo)
    print("\n🎯 Paso 2: Cargar objetivos")
    archivo_objetivos = input("Ruta del archivo (Enter para 'data/objetivos.txt'): ").strip()
    if not archivo_objetivos:
        archivo_objetivos = "data/objetivos.txt"
    
    # Siempre usar API para obtener puntos (necesario para calcular moral)
    print("🌍 Consultando API para obtener info de objetivos (necesario para moral)...")
    objetivos = leer_objetivos_desde_archivo(archivo_objetivos, mundo=mundo_seleccionado, usar_api=True)
    
    if not objetivos:
        print("\n❌ No se pudieron cargar los objetivos")
        input("\nPresiona Enter para continuar...")
        return
    
    # Configurar ataques por objetivo
    print("\n⚔️  Paso 3: Configuración de ataques por objetivo")
    print("  1. Manual (asignar por cada objetivo)")
    print("  2. Fijo (mismo número para todos)")
    
    modo_ataques = input("\n👉 Modo (Enter para 2): ").strip() or "2"
    
    # Diccionario para guardar ataques por objetivo
    ataques_por_objetivo_dict = {}
    
    if modo_ataques == "1":
        # Modo manual: pedir para cada objetivo
        print("\n📋 Asignar ataques manualmente:")
        for objetivo in objetivos:
            coord_str = f"{objetivo['coordenadas'][0]}|{objetivo['coordenadas'][1]}"
            print(f"\n  Objetivo: {coord_str} - {objetivo['nombre']}")
            try:
                num_ataques = int(input(f"    ¿Cuántas ofensivas? (Enter para 5): ").strip() or "5")
                ataques_por_objetivo_dict[coord_str] = num_ataques
            except:
                ataques_por_objetivo_dict[coord_str] = 5
        
        # Usar el promedio como valor por defecto para la función
        ataques_por_objetivo = 5
    else:
        # Modo fijo: mismo número para todos
        try:
            ataques_por_objetivo = int(input("\nAtaques por objetivo (Enter para 5): ").strip() or "5")
        except:
            ataques_por_objetivo = 5
        
        # Llenar el diccionario con el mismo valor para todos
        for objetivo in objetivos:
            coord_str = f"{objetivo['coordenadas'][0]}|{objetivo['coordenadas'][1]}"
            ataques_por_objetivo_dict[coord_str] = ataques_por_objetivo
    
    # Seleccionar tipo de tropa para cálculo de tiempos
    print("\n🏃 Paso 3.5: Tipo de tropa para calcular tiempos")
    print("  1. Noble (35 min/campo) - Recomendado")
    print("  2. Ariete/Catapulta (30 min/campo)")
    print("  3. Espada (22 min/campo)")
    print("  4. Lanza/Hacha/Arquero (18 min/campo)")
    print("  5. Caballería Pesada (11 min/campo)")
    print("  6. Caballería Ligera/Arquero Montado/Paladín (10 min/campo)")
    print("  7. Explorador (9 min/campo)")
    
    tipo_tropa_map = {
        "1": "noble",
        "2": "ariete",
        "3": "espada",
        "4": "lanza",
        "5": "caballeria_pesada",
        "6": "caballeria_ligera",
        "7": "explorador"
    }
    
    seleccion_tropa = input("\n👉 Selecciona tipo de tropa (Enter para 1-Noble): ").strip() or "1"
    tipo_tropa = tipo_tropa_map.get(seleccion_tropa, "noble")
    
    from config_mundos import obtener_velocidad_tropa
    velocidad = obtener_velocidad_tropa(tipo_tropa, mundo_seleccionado)
    print(f"✅ Usando {tipo_tropa} ({velocidad:.1f} min/campo)")
    
    # Seleccionar método de asignación
    print("\n🎲 Paso 4: Método de asignación")
    print("  1. Por distancia mínima")
    print("  2. Balanceado por jugador")
    print("  3. Sincronizado (con hora de llegada)")
    print("  4. 🎯 Optimizado por MORAL (Recomendado)")
    
    metodo = input("\nMétodo (Enter para 4): ").strip() or "4"
    
    plan = None
    
    if metodo == "1":
        print("\n⚙️  Generando plan por distancia mínima...")
        plan = asignar_ataques_por_distancia(pueblos, objetivos, ataques_por_objetivo, mundo_seleccionado, tipo_tropa)
    
    elif metodo == "2":
        print("\n⚙️  Generando plan balanceado...")
        plan = balancear_por_jugador(pueblos, objetivos, ataques_por_objetivo, mundo_seleccionado, tipo_tropa)
    
    elif metodo == "3":
        print("\n⏰ Configurar hora de llegada")
        fecha_str = input("Fecha y hora (formato: YYYY-MM-DD HH:MM:SS): ").strip()
        try:
            hora_llegada = datetime.strptime(fecha_str, "%Y-%m-%d %H:%M:%S")
            print("\n⚙️  Generando plan sincronizado...")
            plan = asignar_con_sincronizacion(pueblos, objetivos, hora_llegada, ataques_por_objetivo, mundo_seleccionado, tipo_tropa)
        except ValueError:
            print("\n❌ Formato de fecha inválido")
            input("\nPresiona Enter para continuar...")
            return
    
    elif metodo == "4":
        print("\n🎯 Plan optimizado por MORAL")
        print("   (Jugadores pequeños → Objetivos pequeños)")
        print("   (Jugadores grandes → Objetivos grandes)")
        
        # Preguntar por hora de llegada
        print("\n⏰ Configurar hora de llegada sincronizada")
        fecha_str = input("Fecha y hora (formato: HH:MM:SS DD/MM/YYYY): ").strip()
        
        hora_llegada = None
        if fecha_str:
            try:
                # Parsear formato HH:MM:SS DD/MM/YYYY
                hora_llegada = datetime.strptime(fecha_str, "%H:%M:%S %d/%m/%Y")
            except ValueError:
                print("\n❌ Formato de fecha inválido. Generando sin sincronización...")
        
        print("\n⚙️  Generando plan...")
        plan = asignar_optimizando_moral(pueblos, objetivos, ataques_por_objetivo_dict, mundo_seleccionado, tipo_tropa, hora_llegada)
        
        # Mostrar estadísticas de moral
        if 'estadisticas_moral' in plan:
            stats = plan['estadisticas_moral']
            print(f"\n📊 Estadísticas de Moral:")
            print(f"   Moral promedio: {stats['moral_promedio']}%")
            print(f"   Ataques con 100% moral: {stats['ataques_100_moral']}")
            print(f"   Ataques con moral < 50%: {stats['ataques_baja_moral']}")
        
        if hora_llegada:
            print(f"\n⏰ Hora de llegada configurada: {hora_llegada.strftime('%d/%m/%Y %H:%M:%S')}")
    
    else:
        print("\n❌ Método inválido")
        input("\nPresiona Enter para continuar...")
        return
    
    if plan:
        # Mostrar resumen
        mostrar_resumen_consola(plan)
        
        # Menú de exportación
        menu_exportar_plan(plan)


def menu_exportar_plan(plan):
    """Menú para exportar el plan generado"""
    while True:
        print("\n" + "="*80)
        print("💾 EXPORTAR PLAN")
        print("="*80)
        print("\n  1️⃣  Exportar a texto")
        print("  2️⃣  Exportar coordenadas (copiar/pegar)")
        print("  3️⃣  Exportar BBCode (foros)")
        print("  4️⃣  Guardar plan (JSON)")
        print("  5️⃣  Ver resumen de nuevo")
        print("  0️⃣  Volver al menú principal")
        
        opcion = input("\n👉 Selecciona una opción: ").strip()
        
        if opcion == "1":
            archivo = input("Nombre del archivo (Enter para 'plan_ataque.txt'): ").strip() or "plan_ataque.txt"
            exportar_comandos_texto(plan, archivo)
            input("\nPresiona Enter para continuar...")
        
        elif opcion == "2":
            archivo = input("Nombre del archivo (Enter para 'coordenadas.txt'): ").strip() or "coordenadas.txt"
            exportar_para_copiar(plan, archivo)
            input("\nPresiona Enter para continuar...")
        
        elif opcion == "3":
            archivo = input("Nombre del archivo (Enter para 'plan_bbcode.txt'): ").strip() or "plan_bbcode.txt"
            exportar_bbcode(plan, archivo)
            input("\nPresiona Enter para continuar...")
        
        elif opcion == "4":
            archivo = input("Nombre del archivo (Enter para 'data/plan.json'): ").strip() or "data/plan.json"
            guardar_plan_json(plan, archivo)
            input("\nPresiona Enter para continuar...")
        
        elif opcion == "5":
            mostrar_resumen_consola(plan)
        
        elif opcion == "0":
            break
        
        else:
            print("\n❌ Opción inválida")
            input("\nPresiona Enter para continuar...")


def menu_cargar_plan():
    """Menú para cargar un plan existente"""
    limpiar_pantalla()
    print("="*80)
    print("📂 CARGAR PLAN EXISTENTE")
    print("="*80)
    
    archivo = input("\nRuta del archivo JSON (Enter para 'data/plan.json'): ").strip() or "data/plan.json"
    
    plan = cargar_plan_json(archivo)
    if plan:
        mostrar_resumen_consola(plan)
        menu_exportar_plan(plan)
    else:
        input("\nPresiona Enter para continuar...")


def menu_crear_ejemplos():
    """Menú para crear archivos de ejemplo"""
    limpiar_pantalla()
    print("="*80)
    print("📄 CREAR ARCHIVOS DE EJEMPLO")
    print("="*80)
    
    print("\n🔨 Creando archivos de ejemplo en la carpeta 'data/'...\n")
    
    crear_archivo_ejemplo_pueblos("data/pueblos_ejemplo.txt")
    crear_archivo_ejemplo_objetivos("data/objetivos_ejemplo.txt")
    
    print("\n✅ ¡Archivos de ejemplo creados!")
    print("\n💡 Puedes editar estos archivos y usarlos como plantilla")
    print("   para tus propios pueblos y objetivos.")
    
    input("\nPresiona Enter para continuar...")


def menu_pruebas():
    """Menú para pruebas y cálculos rápidos"""
    from calculadora import (
        calcular_distancia, 
        calcular_tiempo_viaje, 
        calcular_moral,
        parse_coordenadas,
        tiempo_a_string
    )
    
    while True:
        limpiar_pantalla()
        print("="*80)
        print("🧮 PRUEBAS Y CÁLCULOS")
        print("="*80)
        print("\n  1️⃣  Calcular distancia entre coordenadas")
        print("  2️⃣  Calcular tiempo de viaje")
        print("  3️⃣  Calcular moral")
        print("  0️⃣  Volver")
        
        opcion = input("\n👉 Selecciona una opción: ").strip()
        
        if opcion == "1":
            try:
                coord1_str = input("\nCoordenadas origen (formato xxx|yyy): ").strip()
                coord2_str = input("Coordenadas destino (formato xxx|yyy): ").strip()
                
                coord1 = parse_coordenadas(coord1_str)
                coord2 = parse_coordenadas(coord2_str)
                
                distancia = calcular_distancia(coord1, coord2)
                print(f"\n📏 Distancia: {distancia:.2f} campos")
                
                input("\nPresiona Enter para continuar...")
            except Exception as e:
                print(f"\n❌ Error: {e}")
                input("\nPresiona Enter para continuar...")
        
        elif opcion == "2":
            try:
                distancia = float(input("\nDistancia en campos: ").strip())
                print("\nTipo de tropa:")
                print("  1. Lanza (18 min/campo)")
                print("  2. Noble (35 min/campo)")
                print("  3. Otro")
                
                tipo = input("\nSelecciona: ").strip()
                
                if tipo == "1":
                    tiempo = calcular_tiempo_viaje(distancia, 'lanza')
                elif tipo == "2":
                    tiempo = calcular_tiempo_viaje(distancia, 'noble')
                else:
                    mins = float(input("Minutos por campo: ").strip())
                    tiempo = distancia * mins
                
                print(f"\n⏱️  Tiempo de viaje: {tiempo_a_string(tiempo)}")
                
                input("\nPresiona Enter para continuar...")
            except Exception as e:
                print(f"\n❌ Error: {e}")
                input("\nPresiona Enter para continuar...")
        
        elif opcion == "3":
            try:
                pts_atk = int(input("\nPuntos del atacante: ").strip())
                pts_def = int(input("Puntos del defensor: ").strip())
                
                moral = calcular_moral(pts_atk, pts_def)
                print(f"\n💪 Moral: {moral}%")
                
                input("\nPresiona Enter para continuar...")
            except Exception as e:
                print(f"\n❌ Error: {e}")
                input("\nPresiona Enter para continuar...")
        
        elif opcion == "0":
            break
        
        else:
            print("\n❌ Opción inválida")
            input("\nPresiona Enter para continuar...")


if __name__ == "__main__":
    try:
        menu_principal()
    except KeyboardInterrupt:
        print("\n\n👋 Programa interrumpido. ¡Hasta luego!")
    except Exception as e:
        print(f"\n\n❌ Error inesperado: {e}")
        input("\nPresiona Enter para salir...")
