"""
Módulo para importar datos desde Guerras Tribales
Lee archivos de texto con coordenadas y datos de pueblos/jugadores
"""

import json
import csv
from calculadora import parse_coordenadas


def parse_coordenadas_lista(texto):
    """
    Parsea una lista de coordenadas separadas por espacios.
    Formato: "480|571 479|570 479|572"
    
    Args:
        texto: string con coordenadas separadas por espacios
    
    Returns:
        list: lista de diccionarios con info de pueblos
    """
    pueblos = []
    coordenadas_str = texto.strip().split()
    
    for idx, coord_str in enumerate(coordenadas_str, 1):
        try:
            partes = coord_str.split('|')
            if len(partes) >= 2:
                x, y = int(partes[0]), int(partes[1])
                
                pueblo = {
                    'coordenadas': (x, y),
                    'nombre': partes[2] if len(partes) > 2 else f"Pueblo {x}|{y}",
                    'jugador': partes[3] if len(partes) > 3 else "Desconocido",
                    'puntos_jugador': int(partes[4]) if len(partes) > 4 else 0
                }
                
                pueblos.append(pueblo)
        except (ValueError, IndexError) as e:
            print(f"⚠️  Coordenada {idx} ignorada ({coord_str}): formato inválido")
            continue
    
    return pueblos


def leer_csv_ofensivas(ruta_archivo, filtro_tipo=None, mundo=None, usar_api=True):
    """
    Lee un CSV de ofensivas de tribu exportado desde el juego.
    Formato esperado: Jugador,ID,Total Pueblos,OFFs FULL,OFFs MEDIA,...
    
    Args:
        ruta_archivo: ruta al archivo CSV
        filtro_tipo: 'FULL', 'MEDIA' o None para todos
        mundo: código del mundo para consultar API (ej: 'es95')
        usar_api: si True, consulta API para obtener puntos de jugadores
    
    Returns:
        list: lista de pueblos con información completa
    """
    import re
    
    pueblos = []
    jugador_actual = None
    jugadores_unicos = set()
    
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            lineas = f.readlines()
            
            for linea_num, linea in enumerate(lineas, 1):
                # Saltar cabecera
                if linea_num == 1 or not linea.strip():
                    continue
                
                partes = [p.strip() for p in linea.split(',')]
                
                # Si la primera columna tiene nombre, es un jugador
                if partes[0] and not partes[0].startswith(','):
                    jugador_actual = partes[0]
                    jugadores_unicos.add(jugador_actual)
                    continue
                
                # Si no, es un pueblo
                if len(partes) >= 3:
                    tipo_off = partes[1].upper()
                    
                    # Filtrar por tipo si se especifica
                    if filtro_tipo and tipo_off != filtro_tipo.upper():
                        continue
                    
                    nombre_pueblo = partes[2]
                    
                    # Extraer coordenadas del nombre usando regex
                    match = re.search(r'\((\d+)\|(\d+)\)', nombre_pueblo)
                    
                    if match:
                        x, y = int(match.group(1)), int(match.group(2))
                        
                        # Extraer estadísticas si están disponibles
                        try:
                            hachas = int(partes[4]) if len(partes) > 4 and partes[4] else 0
                            ligeras = int(partes[5]) if len(partes) > 5 and partes[5] else 0
                            arq_cab = int(partes[6]) if len(partes) > 6 and partes[6] else 0
                            arietes = int(partes[7]) if len(partes) > 7 and partes[7] else 0
                            catapultas = int(partes[8]) if len(partes) > 8 and partes[8] else 0
                            pob_total = int(partes[9]) if len(partes) > 9 and partes[9] else 0
                        except (ValueError, IndexError):
                            hachas = ligeras = arq_cab = arietes = catapultas = pob_total = 0
                        
                        pueblo = {
                            'coordenadas': (x, y),
                            'nombre': nombre_pueblo,
                            'jugador': jugador_actual or "Desconocido",
                            'puntos_jugador': 0,  # No está en el CSV
                            'tipo_off': tipo_off,
                            'tropas': {
                                'hachas': hachas,
                                'ligeras': ligeras,
                                'arqueros_caballo': arq_cab,
                                'arietes': arietes,
                                'catapultas': catapultas
                            },
                            'poblacion_ofensiva': pob_total
                        }
                        
                        pueblos.append(pueblo)
        
        print(f"✅ {len(pueblos)} pueblos cargados desde CSV de ofensivas")
        
        # Mostrar estadísticas
        full_count = sum(1 for p in pueblos if p.get('tipo_off') == 'FULL')
        media_count = sum(1 for p in pueblos if p.get('tipo_off') == 'MEDIA')
        
        if full_count > 0 or media_count > 0:
            print(f"   📊 FULL: {full_count} | MEDIA: {media_count}")
        
        # Enriquecer con puntos de jugadores desde API
        if mundo and usar_api and jugadores_unicos:
            print(f"\n🌍 Consultando puntos de {len(jugadores_unicos)} jugadores desde API...")
            
            try:
                from api_gt import APIGuerrasTribales
                
                api = APIGuerrasTribales(mundo)
                api.cargar_jugadores()
                
                # Crear un mapa de jugador -> puntos
                puntos_por_jugador = {}
                
                for nombre_jugador in jugadores_unicos:
                    # Buscar el jugador en la API
                    jugador_encontrado = None
                    for player_id, player_data in api._players.items():
                        if player_data['nombre'].lower() == nombre_jugador.lower():
                            jugador_encontrado = player_data
                            break
                    
                    if jugador_encontrado:
                        puntos_por_jugador[nombre_jugador] = jugador_encontrado['puntos']
                    else:
                        puntos_por_jugador[nombre_jugador] = 0
                        print(f"   ⚠️  Jugador '{nombre_jugador}' no encontrado en API")
                
                # Actualizar puntos en todos los pueblos
                actualizados = 0
                for pueblo in pueblos:
                    if pueblo['jugador'] in puntos_por_jugador:
                        pueblo['puntos_jugador'] = puntos_por_jugador[pueblo['jugador']]
                        if pueblo['puntos_jugador'] > 0:
                            actualizados += 1
                
                print(f"✅ Puntos actualizados para {actualizados}/{len(pueblos)} pueblos")
                
            except ImportError:
                print("⚠️  Módulo api_gt no disponible")
            except Exception as e:
                print(f"⚠️  Error al consultar API: {e}")
        
        return pueblos
        
    except FileNotFoundError:
        print(f"❌ Archivo no encontrado: {ruta_archivo}")
        return []
    except Exception as e:
        print(f"❌ Error al leer CSV: {e}")
        return []


def leer_pueblos_desde_archivo(ruta_archivo):
    """
    Lee pueblos desde un archivo de texto.
    Formato esperado: coordenadas|nombre_pueblo|nombre_jugador|puntos_jugador
    Ejemplo: 500|500|Pueblo1|jugador1|50000
    
    Args:
        ruta_archivo: ruta al archivo con los datos
    
    Returns:
        list: lista de diccionarios con info de pueblos
    """
    pueblos = []
    
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            for linea_num, linea in enumerate(f, 1):
                linea = linea.strip()
                
                # Ignorar líneas vacías y comentarios
                if not linea or linea.startswith('#'):
                    continue
                
                partes = linea.split('|')
                
                if len(partes) < 2:
                    print(f"⚠️  Línea {linea_num} ignorada (formato inválido): {linea}")
                    continue
                
                try:
                    # Formato mínimo: x|y
                    x, y = int(partes[0]), int(partes[1])
                    
                    pueblo = {
                        'coordenadas': (x, y),
                        'nombre': partes[2] if len(partes) > 2 else f"Pueblo {x}|{y}",
                        'jugador': partes[3] if len(partes) > 3 else "Desconocido",
                        'puntos_jugador': int(partes[4]) if len(partes) > 4 else 0
                    }
                    
                    pueblos.append(pueblo)
                    
                except ValueError as e:
                    print(f"⚠️  Error en línea {linea_num}: {e}")
                    continue
        
        print(f"✅ {len(pueblos)} pueblos cargados desde {ruta_archivo}")
        return pueblos
        
    except FileNotFoundError:
        print(f"❌ Archivo no encontrado: {ruta_archivo}")
        return []


def leer_objetivos_desde_archivo(ruta_archivo, mundo=None, usar_api=True):
    """
    Lee objetivos desde un archivo de texto.
    Formato: coordenadas|nombre_objetivo|prioridad|jugador_defensor|puntos_defensor
    También acepta formato simple: "480|571 479|572 480|573" (espacios)
    
    Args:
        ruta_archivo: ruta al archivo con objetivos
        mundo: código del mundo para consultar API (ej: 'es95')
        usar_api: si True, enriquece coordenadas simples con datos de la API
    
    Returns:
        list: lista de objetivos
    """
    objetivos = []
    coordenadas_simples = []
    
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            lineas = f.readlines()
            
            # Filtrar comentarios y líneas vacías
            lineas_validas = [l.strip() for l in lineas if l.strip() and not l.strip().startswith('#')]
            
            # Si hay una sola línea con espacios, es formato simple
            if len(lineas_validas) == 1 and ' ' in lineas_validas[0]:
                # Formato: "480|571 479|572 480|573"
                print("📋 Detectado formato simple de coordenadas")
                contenido = lineas_validas[0]
                
                for coord in contenido.split():
                    partes = coord.split('|')
                    if len(partes) >= 2:
                        try:
                            x, y = int(partes[0]), int(partes[1])
                            coordenadas_simples.append((x, y))
                        except ValueError:
                            continue
                
                # Si hay mundo y API habilitada, enriquecer
                if mundo and usar_api and coordenadas_simples:
                    print(f"🌍 Consultando API de {mundo.upper()}...")
                    
                    try:
                        from api_gt import APIGuerrasTribales
                        
                        api = APIGuerrasTribales(mundo)
                        pueblos_info = api.obtener_info_multiple(coordenadas_simples)
                        
                        for info in pueblos_info:
                            objetivo = {
                                'coordenadas': info['coordenadas'],
                                'nombre': info['nombre'],
                                'prioridad': 1,
                                'jugador_defensor': info.get('jugador', 'Desconocido'),
                                'puntos_defensor': info.get('puntos_jugador', 0),  # Puntos del jugador para calcular moral
                                'puntos_aldea': info.get('puntos', 0),  # Puntos de la aldea (para referencia)
                                'ataques_asignados': []
                            }
                            objetivos.append(objetivo)
                        
                        print(f"✅ {len(objetivos)} objetivos enriquecidos con datos de la API")
                        return objetivos
                        
                    except ImportError:
                        print("⚠️  Módulo api_gt no disponible, usando datos básicos")
                    except Exception as e:
                        print(f"⚠️  Error al consultar API: {e}")
                
                # Si no hay API, crear objetivos básicos
                for x, y in coordenadas_simples:
                    objetivo = {
                        'coordenadas': (x, y),
                        'nombre': f"Objetivo {x}|{y}",
                        'prioridad': 1,
                        'jugador_defensor': "Desconocido",
                        'puntos_defensor': 0,
                        'ataques_asignados': []
                    }
                    objetivos.append(objetivo)
                
                print(f"✅ {len(objetivos)} objetivos cargados (formato simple)")
                return objetivos
            
            # Formato detallado (línea por línea)
            for linea_num, linea in enumerate(lineas_validas, 1):
                linea = linea.strip()
                
                if not linea or linea.startswith('#'):
                    continue
                
                partes = linea.split('|')
                
                if len(partes) < 2:
                    print(f"⚠️  Línea {linea_num} ignorada: {linea}")
                    continue
                
                try:
                    x, y = int(partes[0]), int(partes[1])
                    
                    objetivo = {
                        'coordenadas': (x, y),
                        'nombre': partes[2] if len(partes) > 2 else f"Objetivo {x}|{y}",
                        'prioridad': int(partes[3]) if len(partes) > 3 else 1,
                        'jugador_defensor': partes[4] if len(partes) > 4 else "Desconocido",
                        'puntos_defensor': int(partes[5]) if len(partes) > 5 else 0,
                        'ataques_asignados': []
                    }
                    
                    objetivos.append(objetivo)
                    
                except ValueError as e:
                    print(f"⚠️  Error en línea {linea_num}: {e}")
                    continue
        
        print(f"✅ {len(objetivos)} objetivos cargados desde {ruta_archivo}")
        return objetivos
        
    except FileNotFoundError:
        print(f"❌ Archivo no encontrado: {ruta_archivo}")
        return []


def crear_archivo_ejemplo_pueblos(ruta_archivo):
    """
    Crea un archivo de ejemplo con formato de pueblos atacantes.
    """
    contenido = """# Formato: x|y|nombre_pueblo|jugador|puntos_jugador
# Las líneas que empiezan con # son comentarios
# Puedes omitir nombre_pueblo, jugador y puntos_jugador si no los tienes

500|500|Pueblo Principal|Raba|50000
501|500|Pueblo 2|Raba|50000
502|500|Pueblo 3|Raba|50000
510|510|Castillo|JugadorX|75000
511|510|Fortaleza|JugadorX|75000
"""
    
    with open(ruta_archivo, 'w', encoding='utf-8') as f:
        f.write(contenido)
    
    print(f"✅ Archivo de ejemplo creado: {ruta_archivo}")


def crear_archivo_ejemplo_objetivos(ruta_archivo):
    """
    Crea un archivo de ejemplo con formato de objetivos.
    """
    contenido = """# Formato: x|y|nombre|prioridad|jugador_defensor|puntos_defensor
# Prioridad: 1=alta, 2=media, 3=baja
# Puedes omitir nombre, prioridad, jugador y puntos si no los tienes

520|520|Noble enemigo|1|Enemigo1|80000
521|520|Objetivo secundario|2|Enemigo1|80000
530|530|Base enemiga|1|Enemigo2|100000
"""
    
    with open(ruta_archivo, 'w', encoding='utf-8') as f:
        f.write(contenido)
    
    print(f"✅ Archivo de ejemplo creado: {ruta_archivo}")


def guardar_plan_json(plan, ruta_archivo):
    """
    Guarda un plan de ataque en formato JSON.
    
    Args:
        plan: diccionario con el plan de ataque
        ruta_archivo: ruta donde guardar el archivo
    """
    with open(ruta_archivo, 'w', encoding='utf-8') as f:
        json.dump(plan, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Plan guardado en: {ruta_archivo}")


def cargar_plan_json(ruta_archivo):
    """
    Carga un plan de ataque desde JSON.
    
    Args:
        ruta_archivo: ruta al archivo JSON
    
    Returns:
        dict: plan de ataque
    """
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            plan = json.load(f)
        print(f"✅ Plan cargado desde: {ruta_archivo}")
        return plan
    except FileNotFoundError:
        print(f"❌ Archivo no encontrado: {ruta_archivo}")
        return None


if __name__ == "__main__":
    # Crear archivos de ejemplo
    print("=== Creando archivos de ejemplo ===\n")
    crear_archivo_ejemplo_pueblos("data/pueblos_ejemplo.txt")
    crear_archivo_ejemplo_objetivos("data/objetivos_ejemplo.txt")
    
    # Probar lectura
    print("\n=== Probando lectura de archivos ===\n")
    pueblos = leer_pueblos_desde_archivo("data/pueblos_ejemplo.txt")
    objetivos = leer_objetivos_desde_archivo("data/objetivos_ejemplo.txt")
    
    print(f"\nPueblos cargados: {len(pueblos)}")
    print(f"Objetivos cargados: {len(objetivos)}")
