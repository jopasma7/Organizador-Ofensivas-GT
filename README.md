# Organizador de Ofensivas - Guerras Tribales

Sistema de planificación y asignación de ataques para Guerras Tribales.

## 🚀 Características

- ✅ Cálculo de distancias entre coordenadas
- ✅ Cálculo de tiempos de viaje según tipo de tropa
- ✅ Cálculo automático de moral
- ✅ Asignación inteligente por distancia mínima
- ✅ Balanceo de ataques entre jugadores
- ✅ Sincronización de ataques con hora de llegada
- ✅ Exportación a múltiples formatos (TXT, BBCode, JSON)

## 📦 Instalación

No requiere dependencias externas, solo Python 3.6+

```bash
python main.py
```

## 📖 Uso

### 1. Preparar datos de entrada

Tienes **dos formas** de cargar tus pueblos y objetivos:

#### **Opción A: Desde archivo de texto**

Crea archivos con tus datos:

**pueblos.txt** (pueblos atacantes):
```
500|500|Pueblo1|Raba|50000
501|500|Pueblo2|Raba|50000
510|510|Castillo|JugadorX|75000
```

Formato: `x|y|nombre_pueblo|jugador|puntos_jugador`

**objetivos.txt** (objetivos a atacar):
```
520|520|Noble enemigo|1|Enemigo1|80000
530|530|Base enemiga|1|Enemigo2|100000
```

Formato: `x|y|nombre|prioridad|jugador_defensor|puntos_defensor`

#### **Opción B: Pegar coordenadas directamente** ⭐ NUEVO

También puedes copiar/pegar coordenadas directamente en la terminal:

```
480|571 479|570 479|572 478|572 478|571
```

O con información completa:
```
500|500|Castillo|Raba|50000 501|501|Fortaleza|Raba|50000
```

Esta opción es ideal cuando copias coordenadas desde el juego.

### 2. Ejecutar el programa

```bash
python main.py
```

### 3. Seleccionar opciones

1. **Crear Plan de Ataque** - Genera un nuevo plan
2. **Cargar Plan Existente** - Carga un plan guardado
3. **Crear Archivos de Ejemplo** - Genera plantillas de ejemplo
4. **Pruebas y Cálculos** - Calculadora rápida

### 4. Métodos de asignación

- **Por distancia mínima**: Asigna los pueblos más cercanos a cada objetivo
- **Balanceado por jugador**: Distribuye ataques equitativamente entre jugadores
- **Sincronizado**: Calcula horarios para que todos lleguen al mismo tiempo

## 📊 Ejemplo de salida

```
================================================================================
📋 RESUMEN DEL PLAN DE ATAQUE
================================================================================

🎯 Objetivos: 2
⚔️  Total de ataques: 10
📍 Pueblos sin asignar: 3

--------------------------------------------------------------------------------

Objetivo 1: Noble enemigo (520|520)
  Ataques: 5
  Distancia promedio: 22.36 campos
  Distancia min/max: 20.00 / 25.00

⚖️  Balance de ataques por jugador:
  Raba: 6 ataques
  JugadorX: 4 ataques
```

## 🗂️ Estructura del proyecto

```
Organizador-Ofensivas/
├── main.py           # Programa principal con menús
├── calculadora.py    # Funciones de cálculo
├── asignador.py      # Lógica de asignación
├── importador.py     # Importación de datos
├── exportador.py     # Exportación de planes
└── data/             # Carpeta para archivos
    ├── pueblos.txt
    ├── objetivos.txt
    └── plan.json
```

## 💡 Tips

- Usa prioridad 1 para objetivos críticos (nobles, capitales)
- El programa optimiza automáticamente las distancias
- Puedes guardar planes y cargarlos después para modificarlos
- Exporta a BBCode para compartir en foros de tu tribu

## 🔧 Funciones adicionales

### Calcular distancia
```python
from calculadora import calcular_distancia
distancia = calcular_distancia((500, 500), (510, 510))
```

### Calcular tiempo de viaje
```python
from calculadora import calcular_tiempo_viaje
tiempo = calcular_tiempo_viaje(distancia, 'noble')
```

### Calcular moral
```python
from calculadora import calcular_moral
moral = calcular_moral(50000, 100000)  # 50k atacando 100k
```
