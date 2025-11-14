"""
Módulo para consultar la API pública de Guerras Tribales
Permite obtener información de pueblos, jugadores y tribus
"""

import requests
import gzip
from io import BytesIO
from urllib.parse import unquote_plus


class APIGuerrasTribales:
    """Cliente para la API de Guerras Tribales"""
    
    def __init__(self, mundo):
        """
        Inicializa el cliente de la API.
        
        Args:
            mundo: código del mundo (ej: 'es95', 'es94', etc.)
        """
        self.mundo = mundo.lower()
        # La URL correcta es con .guerrastribales.es para servidores españoles
        self.base_url = f"https://{self.mundo}.guerrastribales.es/map"
        
        # Cache de datos
        self._villages = None
        self._players = None
        self._tribes = None
    
    def _descargar_archivo(self, archivo):
        """
        Descarga y descomprime un archivo de datos del juego.
        
        Args:
            archivo: nombre del archivo ('village', 'player', 'ally')
        
        Returns:
            str: contenido del archivo
        """
        url = f"{self.base_url}/{archivo}.txt.gz"
        
        try:
            print(f"📡 Descargando {archivo}...")
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Descomprimir gzip
            with gzip.GzipFile(fileobj=BytesIO(response.content)) as f:
                contenido = f.read().decode('utf-8')
            
            return contenido
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error al descargar {archivo}: {e}")
            return None
    
    def cargar_pueblos(self):
        """
        Carga la lista de todos los pueblos del mundo.
        Formato: id,nombre,x,y,player_id,puntos,bonus
        
        Returns:
            dict: {(x, y): {info del pueblo}}
        """
        if self._villages is not None:
            return self._villages
        
        contenido = self._descargar_archivo('village')
        
        if not contenido:
            return {}
        
        self._villages = {}
        
        for linea in contenido.strip().split('\n'):
            partes = linea.split(',')
            
            if len(partes) >= 7:
                try:
                    village_id = int(partes[0])
                    nombre = unquote_plus(partes[1])  # Decodificar URL encoding
                    x = int(partes[2])
                    y = int(partes[3])
                    player_id = int(partes[4])
                    puntos = int(partes[5])
                    bonus = int(partes[6])
                    
                    self._villages[(x, y)] = {
                        'id': village_id,
                        'nombre': nombre,
                        'coordenadas': (x, y),
                        'player_id': player_id,
                        'puntos': puntos,
                        'bonus': bonus
                    }
                except (ValueError, IndexError):
                    continue
        
        print(f"✅ {len(self._villages)} pueblos cargados")
        return self._villages
    
    def cargar_jugadores(self):
        """
        Carga la lista de todos los jugadores del mundo.
        Formato: id,nombre,tribe_id,pueblos,puntos,rank
        
        Returns:
            dict: {player_id: {info del jugador}}
        """
        if self._players is not None:
            return self._players
        
        contenido = self._descargar_archivo('player')
        
        if not contenido:
            return {}
        
        self._players = {}
        
        for linea in contenido.strip().split('\n'):
            partes = linea.split(',')
            
            if len(partes) >= 6:
                try:
                    player_id = int(partes[0])
                    nombre = unquote_plus(partes[1])  # Decodificar URL encoding
                    tribe_id = int(partes[2])
                    pueblos = int(partes[3])
                    puntos = int(partes[4])
                    rank = int(partes[5])
                    
                    self._players[player_id] = {
                        'id': player_id,
                        'nombre': nombre,
                        'tribe_id': tribe_id,
                        'pueblos': pueblos,
                        'puntos': puntos,
                        'rank': rank
                    }
                except (ValueError, IndexError):
                    continue
        
        print(f"✅ {len(self._players)} jugadores cargados")
        return self._players
    
    def cargar_tribus(self):
        """
        Carga la lista de todas las tribus del mundo.
        Formato: id,nombre,tag,miembros,pueblos,puntos,rank
        
        Returns:
            dict: {tribe_id: {info de la tribu}}
        """
        if self._tribes is not None:
            return self._tribes
        
        contenido = self._descargar_archivo('ally')
        
        if not contenido:
            return {}
        
        self._tribes = {}
        
        for linea in contenido.strip().split('\n'):
            partes = linea.split(',')
            
            if len(partes) >= 8:
                try:
                    tribe_id = int(partes[0])
                    nombre = unquote_plus(partes[1])  # Decodificar URL encoding
                    tag = unquote_plus(partes[2])     # Decodificar URL encoding
                    miembros = int(partes[3])
                    pueblos = int(partes[4])
                    puntos = int(partes[5])
                    total_puntos = int(partes[6])
                    rank = int(partes[7])
                    
                    self._tribes[tribe_id] = {
                        'id': tribe_id,
                        'nombre': nombre,
                        'tag': tag,
                        'miembros': miembros,
                        'pueblos': pueblos,
                        'puntos': puntos,
                        'total_puntos': total_puntos,
                        'rank': rank
                    }
                except (ValueError, IndexError):
                    continue
        
        print(f"✅ {len(self._tribes)} tribus cargadas")
        return self._tribes
    
    def obtener_info_pueblo(self, x, y):
        """
        Obtiene información completa de un pueblo por sus coordenadas.
        
        Args:
            x: coordenada X
            y: coordenada Y
        
        Returns:
            dict: información completa del pueblo (con jugador y tribu) o None
        """
        # Asegurar que los datos estén cargados
        if self._villages is None:
            self.cargar_pueblos()
        
        if self._players is None:
            self.cargar_jugadores()
        
        if self._tribes is None:
            self.cargar_tribus()
        
        # Buscar el pueblo
        pueblo = self._villages.get((x, y))
        
        if not pueblo:
            return None
        
        # Enriquecer con información del jugador
        player_id = pueblo['player_id']
        
        if player_id > 0 and player_id in self._players:
            jugador = self._players[player_id]
            pueblo['jugador'] = jugador['nombre']
            pueblo['puntos_jugador'] = jugador['puntos']
            pueblo['rank_jugador'] = jugador['rank']
            
            # Información de la tribu
            tribe_id = jugador['tribe_id']
            
            if tribe_id > 0 and tribe_id in self._tribes:
                tribu = self._tribes[tribe_id]
                pueblo['tribu'] = tribu['tag']
                pueblo['tribu_nombre'] = tribu['nombre']
            else:
                pueblo['tribu'] = None
                pueblo['tribu_nombre'] = None
        else:
            pueblo['jugador'] = 'Bárbaros'
            pueblo['puntos_jugador'] = 0
            pueblo['rank_jugador'] = 0
            pueblo['tribu'] = None
            pueblo['tribu_nombre'] = None
        
        return pueblo
    
    def obtener_info_multiple(self, coordenadas_lista):
        """
        Obtiene información de múltiples pueblos.
        
        Args:
            coordenadas_lista: lista de tuplas (x, y)
        
        Returns:
            list: lista de diccionarios con información de pueblos
        """
        # Cargar todos los datos una sola vez
        self.cargar_pueblos()
        self.cargar_jugadores()
        self.cargar_tribus()
        
        resultados = []
        
        for x, y in coordenadas_lista:
            info = self.obtener_info_pueblo(x, y)
            
            if info:
                resultados.append(info)
            else:
                # Pueblo no encontrado
                resultados.append({
                    'coordenadas': (x, y),
                    'nombre': f'Desconocido {x}|{y}',
                    'jugador': 'No encontrado',
                    'puntos_jugador': 0
                })
        
        return resultados


# Función auxiliar para uso rápido
def enriquecer_coordenadas(coordenadas_lista, mundo):
    """
    Función auxiliar para enriquecer rápidamente una lista de coordenadas.
    
    Args:
        coordenadas_lista: lista de tuplas (x, y)
        mundo: código del mundo (ej: 'es95')
    
    Returns:
        list: lista de diccionarios con información completa
    """
    api = APIGuerrasTribales(mundo)
    return api.obtener_info_multiple(coordenadas_lista)


if __name__ == "__main__":
    # Ejemplo de uso
    print("="*80)
    print("🧪 TEST: API Guerras Tribales")
    print("="*80)
    
    api = APIGuerrasTribales('es95')
    
    # Probar con una coordenada
    print("\n📍 Consultando pueblo 480|571...")
    info = api.obtener_info_pueblo(480, 571)
    
    if info:
        print(f"\n✅ Pueblo encontrado:")
        print(f"   Nombre: {info['nombre']}")
        print(f"   Jugador: {info['jugador']}")
        print(f"   Puntos jugador: {info['puntos_jugador']:,}")
        print(f"   Tribu: {info.get('tribu', 'Sin tribu')}")
        print(f"   Puntos pueblo: {info['puntos']}")
    else:
        print("❌ Pueblo no encontrado")
    
    # Probar con múltiples coordenadas
    print("\n📍 Consultando múltiples pueblos...")
    coordenadas = [(480, 571), (479, 572), (480, 573)]
    
    resultados = api.obtener_info_multiple(coordenadas)
    
    print(f"\n✅ {len(resultados)} pueblos consultados")
    for r in resultados:
        print(f"   {r['coordenadas']}: {r['jugador']} - {r['nombre']}")
