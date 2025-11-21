"""
Organizador de Ofensivas - Guerras Tribales
Programa para planificar y asignar ataques de manera optimizada
"""

import os
from datetime import datetime, timedelta
from importador import (
    leer_pueblos_desde_archivo, 
    leer_objetivos_desde_archivo,
    leer_categorias_objetivos,
    leer_objetivos_por_categoria,
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
    
    # Usar siempre el mundo ES95
    mundo_seleccionado = 'es95'
    
    # Cargar pueblos atacantes desde CSV
    print("\n📍 Paso 1: Cargar pueblos atacantes desde CSV")
    
    from importador import leer_csv_ofensivas
    
    # Buscar archivo CSV en la carpeta actual
    import os
    archivos_csv = [f for f in os.listdir('.') if f.endswith('.csv')]
    
    if archivos_csv:
        archivo_csv = archivos_csv[0]
        print(f"📄 Usando archivo: {archivo_csv}")
    else:
        print("⚠️  No se encontró ningún archivo CSV en la carpeta")
        archivo_csv = input("Ruta del archivo CSV: ").strip()
        if not archivo_csv:
            print("\n❌ No se especificó archivo CSV")
            input("\nPresiona Enter para continuar...")
            return
    
    # Filtrar por tipo de ofensiva
    print("\n🎯 Filtrar por tipo de OFF:")
    print("  1. SUPER (ofensivas super)")
    print("  2. FULL (ofensivas completas)")
    print("  3. 3/4 (tres cuartos)")
    print("  4. MEDIA (ofensivas medias)")
    print("  5. Todas")
    
    filtro = input("\n👉 Selecciona filtro (Enter para 5): ").strip() or "5"
    
    tipo_filtro = None
    if filtro == "1":
        tipo_filtro = "SUPER"
    elif filtro == "2":
        tipo_filtro = "FULL"
    elif filtro == "3":
        tipo_filtro = "3/4"
    elif filtro == "4":
        tipo_filtro = "MEDIA"
    
    # Guardar el tipo de filtro seleccionado para usar después
    filtro_seleccionado = filtro
    
    # Siempre usar API para obtener puntos (necesario para calcular moral)
    print("\n🌍 Consultando API para obtener puntos de jugadores (necesario para moral)...")
    pueblos = leer_csv_ofensivas(archivo_csv, tipo_filtro, mundo=mundo_seleccionado, usar_api=True)
    
    if not pueblos:
        print("\n❌ No se pudieron cargar los pueblos")
        input("\nPresiona Enter para continuar...")
        return
    
    # Mostrar total de ofensivas disponibles
    total_ofensivas = len(pueblos)
    print(f"\n✅ Total de ofensivas disponibles: {total_ofensivas}")
    
    # Si se seleccionó "Todas", contar por tipo
    if filtro_seleccionado == "5":
        super_count = sum(1 for p in pueblos if p.get('tipo_off') == 'SUPER')
        full_count = sum(1 for p in pueblos if p.get('tipo_off') == 'FULL')
        tres_cuartos_count = sum(1 for p in pueblos if p.get('tipo_off') == '3/4')
        media_count = sum(1 for p in pueblos if p.get('tipo_off') == 'MEDIA')
        print(f"   📊 Desglose: SUPER={super_count}, FULL={full_count}, 3/4={tres_cuartos_count}, MEDIA={media_count}")
    
    # Cargar objetivos desde archivo por defecto
    print("\n🎯 Paso 2: Cargar objetivos")
    archivo_objetivos = "data/objetivos.txt"
    print(f"📄 Usando archivo: {archivo_objetivos}")
    
    # Leer categorías disponibles
    categorias = leer_categorias_objetivos(archivo_objetivos)
    
    objetivos = []
    
    if categorias:
        # Hay categorías, preguntar cuál usar
        print("\n📂 Categorías de objetivos disponibles:")
        categorias_lista = list(categorias.keys())
        for idx, cat in enumerate(categorias_lista, 1):
            num_coords = len(categorias[cat])
            print(f"  {idx}. {cat} ({num_coords} objetivos)")
        
        seleccion = input("\n👉 Selecciona categoría (número o nombre, Enter para usar todas): ").strip()
        
        if seleccion:
            # Usuario seleccionó una categoría específica
            if seleccion.isdigit():
                idx_seleccion = int(seleccion) - 1
                if 0 <= idx_seleccion < len(categorias_lista):
                    categoria_seleccionada = categorias_lista[idx_seleccion]
                else:
                    print("❌ Selección inválida, usando todas")
                    categoria_seleccionada = None
            else:
                # Buscar por nombre
                categoria_seleccionada = seleccion if seleccion in categorias else None
                if not categoria_seleccionada:
                    print(f"❌ Categoría '{seleccion}' no encontrada, usando todas")
            
            if categoria_seleccionada:
                print(f"\n✅ Usando categoría: {categoria_seleccionada}")
                print("🌍 Consultando API para obtener info de objetivos (necesario para moral)...")
                objetivos = leer_objetivos_por_categoria(archivo_objetivos, categoria_seleccionada, mundo=mundo_seleccionado, usar_api=True)
        
        # Si no seleccionó o hubo error, usar todas las categorías
        if not objetivos:
            print("\n📋 Usando todas las categorías")
            print("🌍 Consultando API para obtener info de objetivos (necesario para moral)...")
            for cat in categorias_lista:
                objs_cat = leer_objetivos_por_categoria(archivo_objetivos, cat, mundo=mundo_seleccionado, usar_api=True)
                objetivos.extend(objs_cat)
    else:
        # No hay categorías, usar formato tradicional
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
    # Diccionario para guardar tipo de OFF por objetivo (si se seleccionó "Todas")
    tipo_off_por_objetivo = {}
    
    if modo_ataques == "1":
        # Modo manual: pedir para cada objetivo
        print("\n📋 Asignar ataques manualmente:")
        ofensivas_restantes = total_ofensivas
        
        # Trackear ofensivas ya asignadas por tipo
        asignadas_por_tipo = {'SUPER': 0, 'FULL': 0, '3/4': 0, 'MEDIA': 0}
        
        for i, objetivo in enumerate(objetivos, 1):
            coord_str = f"{objetivo['coordenadas'][0]}|{objetivo['coordenadas'][1]}"
            jugador_def = objetivo.get('jugador_defensor', 'Desconocido')
            print(f"\n  [{i}/{len(objetivos)}] Objetivo: {coord_str} - {objetivo['nombre']} (Jugador: {jugador_def})")
            print(f"  🎯 Ofensivas disponibles: {ofensivas_restantes}")
            
            # Si se seleccionó "Todas", preguntar tipo de OFF
            tipo_off_objetivo = None
            if filtro_seleccionado == "5":
                print("\n  🎯 ¿Qué tipo de OFF usar para este objetivo?")
                # Contar totales de cada tipo
                super_total = sum(1 for p in pueblos if p.get('tipo_off') == 'SUPER')
                full_total = sum(1 for p in pueblos if p.get('tipo_off') == 'FULL')
                tres_total = sum(1 for p in pueblos if p.get('tipo_off') == '3/4')
                media_total = sum(1 for p in pueblos if p.get('tipo_off') == 'MEDIA')
                
                # Calcular disponibles (total - asignadas)
                super_disp = super_total - asignadas_por_tipo['SUPER']
                full_disp = full_total - asignadas_por_tipo['FULL']
                tres_disp = tres_total - asignadas_por_tipo['3/4']
                media_disp = media_total - asignadas_por_tipo['MEDIA']
                
                print(f"    1. SUPER (disponibles: {super_disp})")
                print(f"    2. FULL (disponibles: {full_disp})")
                print(f"    3. 3/4 (disponibles: {tres_disp})")
                print(f"    4. MEDIA (disponibles: {media_disp})")
                print(f"    5. Cualquiera (usar todas las disponibles)")
                
                tipo_input = input("    👉 Selecciona tipo (Enter para 5): ").strip() or "5"
                if tipo_input == "1":
                    tipo_off_objetivo = "SUPER"
                elif tipo_input == "2":
                    tipo_off_objetivo = "FULL"
                elif tipo_input == "3":
                    tipo_off_objetivo = "3/4"
                elif tipo_input == "4":
                    tipo_off_objetivo = "MEDIA"
                
                tipo_off_por_objetivo[coord_str] = tipo_off_objetivo
            
            if ofensivas_restantes == 0:
                print("  ⚠️  ¡No quedan ofensivas disponibles!")
                respuesta = input("  ¿Continuar sin asignar a este objetivo? (s/n, Enter=s): ").strip().lower()
                if respuesta != 'n':
                    ataques_por_objetivo_dict[coord_str] = 0
                    continue
                else:
                    break
            
            try:
                max_sugerido = min(5, ofensivas_restantes)
                num_ataques = int(input(f"    ¿Cuántas ofensivas? (Enter para {max_sugerido}): ").strip() or str(max_sugerido))
                
                if num_ataques > ofensivas_restantes:
                    print(f"  ⚠️  Solo hay {ofensivas_restantes} ofensivas disponibles. Ajustando...")
                    num_ataques = ofensivas_restantes
                
                ataques_por_objetivo_dict[coord_str] = num_ataques
                ofensivas_restantes -= num_ataques
                
                # Actualizar contador de asignadas por tipo (solo si se seleccionó tipo específico)
                if tipo_off_objetivo and tipo_off_objetivo in asignadas_por_tipo:
                    asignadas_por_tipo[tipo_off_objetivo] += num_ataques
                
            except:
                ataques_por_objetivo_dict[coord_str] = min(5, ofensivas_restantes)
                ofensivas_restantes -= ataques_por_objetivo_dict[coord_str]
                # Actualizar contador de asignadas por tipo
                if tipo_off_objetivo and tipo_off_objetivo in asignadas_por_tipo:
                    asignadas_por_tipo[tipo_off_objetivo] += ataques_por_objetivo_dict[coord_str]
        
        if ofensivas_restantes > 0:
            print(f"\n✅ Asignación completa. Ofensivas sin asignar: {ofensivas_restantes}")
        
        # Usar el promedio como valor por defecto para la función
        ataques_por_objetivo = 5
    else:
        # Modo fijo: mismo número para todos
        try:
            ataques_por_objetivo = int(input("\nAtaques por objetivo (Enter para 5): ").strip() or "5")
        except:
            ataques_por_objetivo = 5
        
        # Calcular si hay suficientes ofensivas
        total_necesarias = len(objetivos) * ataques_por_objetivo
        print(f"\n📊 Cálculo de ofensivas:")
        print(f"   • Objetivos: {len(objetivos)}")
        print(f"   • Ofensivas por objetivo: {ataques_por_objetivo}")
        print(f"   • Total necesarias: {total_necesarias}")
        print(f"   • Disponibles: {total_ofensivas}")
        
        if total_necesarias > total_ofensivas:
            print(f"\n⚠️  ADVERTENCIA: No hay suficientes ofensivas!")
            print(f"   Faltan: {total_necesarias - total_ofensivas} ofensivas")
            respuesta = input("\n¿Continuar de todos modos? (s/n, Enter=s): ").strip().lower()
            if respuesta == 'n':
                input("\nPresiona Enter para continuar...")
                return
        else:
            sobrantes = total_ofensivas - total_necesarias
            print(f"   ✅ Sobran: {sobrantes} ofensivas")
        
        # Llenar el diccionario con el mismo valor para todos
        for i, objetivo in enumerate(objetivos, 1):
            coord_str = f"{objetivo['coordenadas'][0]}|{objetivo['coordenadas'][1]}"
            ataques_por_objetivo_dict[coord_str] = ataques_por_objetivo
            
            # Si se seleccionó "Todas", preguntar tipo de OFF para cada objetivo
            if filtro_seleccionado == "5":
                jugador_def = objetivo.get('jugador_defensor', 'Desconocido')
                print(f"\n  [{i}/{len(objetivos)}] Objetivo: {coord_str} - {objetivo['nombre']} (Jugador: {jugador_def})")
                print("  🎯 ¿Qué tipo de OFF usar para este objetivo?")
                super_disp = sum(1 for p in pueblos if p.get('tipo_off') == 'SUPER')
                full_disp = sum(1 for p in pueblos if p.get('tipo_off') == 'FULL')
                tres_disp = sum(1 for p in pueblos if p.get('tipo_off') == '3/4')
                media_disp = sum(1 for p in pueblos if p.get('tipo_off') == 'MEDIA')
                
                print(f"    1. SUPER (disponibles: {super_disp})")
                print(f"    2. FULL (disponibles: {full_disp})")
                print(f"    3. 3/4 (disponibles: {tres_disp})")
                print(f"    4. MEDIA (disponibles: {media_disp})")
                print(f"    5. Cualquiera (usar todas las disponibles)")
                
                tipo_input = input("    👉 Selecciona tipo (Enter para 5): ").strip() or "5"
                tipo_off_objetivo = None
                if tipo_input == "1":
                    tipo_off_objetivo = "SUPER"
                elif tipo_input == "2":
                    tipo_off_objetivo = "FULL"
                elif tipo_input == "3":
                    tipo_off_objetivo = "3/4"
                elif tipo_input == "4":
                    tipo_off_objetivo = "MEDIA"
                
                tipo_off_por_objetivo[coord_str] = tipo_off_objetivo
    
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
        
        # Preguntar por rango de llegada
        print("\n⏰ Configurar ventana de llegada (opcional)")
        print("   Ejemplo: 02:00:00 16/11/2025 a las 06:00:00 16/11/2025")
        print("   (Presiona Enter para omitir sincronización)")
        rango_str = input("\nRango de llegada: ").strip()
        
        hora_inicio = None
        hora_fin = None
        
        if rango_str:
            try:
                # Parsear formato: "HH:MM:SS DD/MM/YYYY a las HH:MM:SS DD/MM/YYYY"
                if " a las " in rango_str.lower():
                    partes = rango_str.lower().split(" a las ")
                    hora_inicio = datetime.strptime(partes[0].strip(), "%H:%M:%S %d/%m/%Y")
                    hora_fin = datetime.strptime(partes[1].strip(), "%H:%M:%S %d/%m/%Y")
                    
                    if hora_fin <= hora_inicio:
                        print("\n⚠️  La hora de fin debe ser posterior a la de inicio. Generando sin sincronización...")
                        hora_inicio = None
                        hora_fin = None
                else:
                    print("\n⚠️  Formato incorrecto. Usa: HH:MM:SS DD/MM/YYYY a las HH:MM:SS DD/MM/YYYY")
                    print("   Generando sin sincronización...")
            except ValueError:
                print("\n❌ Formato de fecha inválido. Generando sin sincronización...")
        
        # Usar el punto medio del rango como hora de llegada objetivo
        hora_llegada = None
        if hora_inicio and hora_fin:
            # Calcular el punto medio del rango
            diferencia = (hora_fin - hora_inicio).total_seconds() / 2
            hora_llegada = hora_inicio + timedelta(seconds=diferencia)
            print(f"\n✅ Ventana configurada: {hora_inicio.strftime('%H:%M:%S %d/%m/%Y')} - {hora_fin.strftime('%H:%M:%S %d/%m/%Y')}")
            print(f"   Objetivo central: {hora_llegada.strftime('%H:%M:%S %d/%m/%Y')}")
        
        print("\n⚙️  Generando plan...")
        # Pasar el filtro de tipo de OFF si se seleccionó "Todas"
        tipo_off_dict = tipo_off_por_objetivo if filtro_seleccionado == "5" else None
        plan = asignar_optimizando_moral(pueblos, objetivos, ataques_por_objetivo_dict, mundo_seleccionado, tipo_tropa, hora_llegada, tipo_off_dict)
        
        # Agregar información de la ventana al plan y calcular rangos de envío
        if hora_inicio and hora_fin:
            plan['ventana_llegada'] = {
                'inicio': hora_inicio.strftime('%H:%M:%S %d/%m/%Y'),
                'fin': hora_fin.strftime('%H:%M:%S %d/%m/%Y'),
                'objetivo': hora_llegada.strftime('%H:%M:%S %d/%m/%Y')
            }
            
            # Calcular rango de envío para cada ataque
            for objetivo in plan['objetivos']:
                for ataque in objetivo['ataques']:
                    tiempo_viaje_mins = ataque['tiempo_viaje_minutos']
                    
                    # Hora de envío para llegar al inicio de la ventana
                    hora_envio_min = hora_inicio - timedelta(minutes=tiempo_viaje_mins)
                    
                    # Hora de envío para llegar al final de la ventana
                    hora_envio_max = hora_fin - timedelta(minutes=tiempo_viaje_mins)
                    
                    # Guardar el rango como string
                    ataque['hora_envio'] = f"{hora_envio_min.strftime('%d/%m/%Y %H:%M:%S')} hasta {hora_envio_max.strftime('%d/%m/%Y %H:%M:%S')}"
                    ataque['hora_llegada'] = f"{hora_inicio.strftime('%d/%m/%Y %H:%M:%S')} - {hora_fin.strftime('%d/%m/%Y %H:%M:%S')}"
        
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
