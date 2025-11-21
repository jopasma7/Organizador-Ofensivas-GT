"""
Módulo para exportar planes de ataque
Genera archivos listos para copiar/pegar en Guerras Tribales
"""

from calculadora import coordenadas_a_string


def exportar_comandos_texto(plan, ruta_archivo):
    """
    Exporta comandos en formato de texto simple.
    
    Args:
        plan: diccionario con el plan de ataque
        ruta_archivo: ruta donde guardar el archivo
    """
    with open(ruta_archivo, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("PLAN DE ATAQUE - GUERRAS TRIBALES\n")
        f.write("=" * 80 + "\n\n")
        
        if 'mundo' in plan:
            from config_mundos import obtener_config, obtener_velocidad_tropa
            config = obtener_config(plan['mundo'])
            f.write(f"🌍 Mundo: {config['nombre']} (Velocidad: {config['velocidad']}x)\n")
            
            if 'tipo_tropa' in plan:
                velocidad = obtener_velocidad_tropa(plan['tipo_tropa'], plan['mundo'])
                f.write(f"🏃 Tipo de tropa: {plan['tipo_tropa']} ({velocidad:.1f} min/campo)\n")
        
        if 'ventana_llegada' in plan:
            f.write(f"⏰ Ventana de llegada: {plan['ventana_llegada']['inicio']} - {plan['ventana_llegada']['fin']}\n")
            f.write(f"🎯 Objetivo central: {plan['ventana_llegada']['objetivo']}\n")
        elif 'hora_llegada_objetivo' in plan:
            f.write(f"🎯 Hora de llegada objetivo: {plan['hora_llegada_objetivo']}\n")
        
        f.write("\n")
        
        for idx, objetivo in enumerate(plan['objetivos'], 1):
            f.write(f"\n{'='*80}\n")
            f.write(f"OBJETIVO #{idx}: {objetivo['nombre']} ({objetivo['coordenadas']})\n")
            f.write(f"Defensor: {objetivo.get('jugador_defensor', 'Desconocido')}\n")
            f.write(f"Ataques asignados: {len(objetivo['ataques'])}\n")
            f.write(f"{'='*80}\n\n")
            
            for i, ataque in enumerate(objetivo['ataques'], 1):
                f.write(f"  Ataque {i}:\n")
                f.write(f"    Desde: {ataque['pueblo_atacante']} ({ataque['nombre_pueblo']})\n")
                f.write(f"    Jugador: {ataque['jugador']}\n")
                
                # Si tiene tipo de OFF, mostrarlo
                if 'tipo_off' in ataque:
                    f.write(f"    Tipo: {ataque['tipo_off']}\n")
                
                # Si tiene tropas, mostrarlas
                if 'tropas' in ataque:
                    tropas = ataque['tropas']
                    f.write(f"    Tropas: {tropas.get('hachas', 0)} hachas, ")
                    f.write(f"{tropas.get('ligeras', 0)} ligeras, ")
                    f.write(f"{tropas.get('arietes', 0)} arietes\n")
                
                f.write(f"    Distancia: {ataque['distancia']} campos\n")
                f.write(f"    Tiempo: {ataque['tiempo_viaje']}\n")
                f.write(f"    Moral: {ataque['moral']}%\n")
                
                if 'hora_envio' in ataque:
                    f.write(f"    ⏰ Enviar a las: {ataque['hora_envio']}\n")
                
                f.write("\n")
        
        # Resumen por jugador
        resumen_jugadores = {}
        for objetivo in plan['objetivos']:
            for ataque in objetivo['ataques']:
                jugador = ataque['jugador']
                if jugador not in resumen_jugadores:
                    resumen_jugadores[jugador] = {
                        'total_ataques': 0,
                        'total_tropas': 0,
                        'tipo_off': ataque.get('tipo_off', 'N/A')
                    }
                resumen_jugadores[jugador]['total_ataques'] += 1
                
                if 'tropas' in ataque:
                    tropas = ataque['tropas']
                    resumen_jugadores[jugador]['total_tropas'] += (
                        tropas.get('hachas', 0) +
                        tropas.get('ligeras', 0) +
                        tropas.get('arq_caballo', 0) +
                        tropas.get('arietes', 0) +
                        tropas.get('catapultas', 0)
                    )
        
        if resumen_jugadores:
            f.write(f"\n{'='*80}\n")
            f.write(f"📊 RESUMEN POR JUGADOR\n")
            f.write(f"{'='*80}\n\n")
            
            for jugador, datos in sorted(resumen_jugadores.items(), key=lambda x: x[1]['total_ataques'], reverse=True):
                f.write(f"  {jugador}:\n")
                f.write(f"    Ofensivas: {datos['total_ataques']}\n")
                if datos['total_tropas'] > 0:
                    f.write(f"    Total tropas: {datos['total_tropas']:,}\n")
                f.write("\n")
        
        # Pueblos sin asignar
        if plan.get('pueblos_sin_asignar'):
            f.write(f"\n{'='*80}\n")
            f.write(f"PUEBLOS SIN ASIGNAR ({len(plan['pueblos_sin_asignar'])})\n")
            f.write(f"{'='*80}\n\n")
            
            for pueblo in plan['pueblos_sin_asignar']:
                f.write(f"  • {pueblo['coordenadas']} - {pueblo['nombre']} ({pueblo['jugador']})\n")
        
        # Balance de jugadores
        if 'balance_jugadores' in plan:
            f.write(f"\n{'='*80}\n")
            f.write("BALANCE DE ATAQUES POR JUGADOR\n")
            f.write(f"{'='*80}\n\n")
            
            for jugador, ataques in plan['balance_jugadores'].items():
                f.write(f"  {jugador}: {ataques} ataques\n")
    
    print(f"✅ Comandos exportados a: {ruta_archivo}")


def exportar_para_copiar(plan, ruta_archivo):
    """
    Exporta en formato simple para copiar/pegar coordenadas en GT.
    
    Args:
        plan: plan de ataque
        ruta_archivo: archivo de salida
    """
    with open(ruta_archivo, 'w', encoding='utf-8') as f:
        for objetivo in plan['objetivos']:
            f.write(f"\n# {objetivo['nombre']} - {objetivo['coordenadas']}\n")
            
            for ataque in objetivo['ataques']:
                # Formato: coordenadas_origen coordenadas_destino
                f.write(f"{ataque['pueblo_atacante']} -> {objetivo['coordenadas']}\n")
    
    print(f"✅ Coordenadas exportadas a: {ruta_archivo}")


def exportar_bbcode(plan, ruta_archivo):
    """
    Exporta el plan en formato BBCode para foros.
    
    Args:
        plan: plan de ataque
        ruta_archivo: archivo de salida
    """
    with open(ruta_archivo, 'w', encoding='utf-8') as f:
        f.write("[b][size=14]PLAN DE ATAQUE[/size][/b]\n\n")
        
        if 'ventana_llegada' in plan:
            f.write(f"[b]⏰ Ventana de llegada:[/b] {plan['ventana_llegada']['inicio']} - {plan['ventana_llegada']['fin']}\n")
            f.write(f"[b]🎯 Objetivo central:[/b] {plan['ventana_llegada']['objetivo']}\n\n")
        elif 'hora_llegada_objetivo' in plan:
            f.write(f"[b]🎯 Hora de llegada:[/b] {plan['hora_llegada_objetivo']}\n\n")
        
        for idx, objetivo in enumerate(plan['objetivos'], 1):
            f.write(f"[b][size=12]Objetivo #{idx}: {objetivo['nombre']}[/size][/b]\n")
            f.write(f"[b]Coordenadas:[/b] [coord]{objetivo['coordenadas']}[/coord]\n")
            f.write(f"[b]Ataques:[/b] {len(objetivo['ataques'])}\n\n")
            
            f.write("[table]\n")
            f.write("[**]Desde[||]Jugador[||]Tropas[||]Moral")
            
            if objetivo['ataques'] and 'hora_envio' in objetivo['ataques'][0]:
                f.write("[||]Hora Envío")
            
            f.write("[||]Lanzar[/**]\n")
            
            for ataque in objetivo['ataques']:
                f.write(f"[*][coord]{ataque['pueblo_atacante']}[/coord]")
                f.write(f"[|][player]{ataque['jugador']}[/player]")
                
                # Columna de tropas con iconos BBCode
                if 'tropas' in ataque:
                    tropas = ataque['tropas']
                    tropas_texto = []
                    if tropas.get('hachas', 0) > 0:
                        tropas_texto.append(f"{tropas['hachas']}[unit]axe[/unit]")
                    if tropas.get('ligeras', 0) > 0:
                        tropas_texto.append(f"{tropas['ligeras']}[unit]light[/unit]")
                    if tropas.get('arq_caballo', 0) > 0:
                        tropas_texto.append(f"{tropas['arq_caballo']}[unit]marcher[/unit]")
                    if tropas.get('arietes', 0) > 0:
                        tropas_texto.append(f"{tropas['arietes']}[unit]ram[/unit]")
                    if tropas.get('catapultas', 0) > 0:
                        tropas_texto.append(f"{tropas['catapultas']}[unit]catapult[/unit]")
                    f.write(f"[|]{' '.join(tropas_texto)}")
                else:
                    f.write("[|]-")
                
                f.write(f"[|]{ataque['moral']}%")
                
                if 'hora_envio' in ataque:
                    f.write(f"[|]{ataque['hora_envio']}")
                
                # Columna Lanzar con enlace directo
                if 'village_id' in ataque and 'coordenadas_objetivo' in ataque:
                    village_id = ataque['village_id']
                    x_obj, y_obj = ataque['coordenadas_objetivo']
                    mundo = plan.get('mundo', 'es95')
                    url = f"https://{mundo}.guerrastribales.es/game.php?village={village_id}&screen=place&x={x_obj}&y={y_obj}"
                    f.write(f"[|][url={url}]Lanzar[/url]")
                else:
                    f.write("[|]-")
                
                f.write("\n")
            
            f.write("[/table]\n\n")
        
        # Crear resumen por jugador
        resumen_jugadores = {}
        for objetivo in plan['objetivos']:
            for ataque in objetivo['ataques']:
                jugador = ataque['jugador']
                if jugador not in resumen_jugadores:
                    resumen_jugadores[jugador] = {
                        'total_ataques': 0,
                        'total_tropas': 0,
                        'tipo_off': ataque.get('tipo_off', 'N/A')
                    }
                resumen_jugadores[jugador]['total_ataques'] += 1
                
                # Sumar tropas
                if 'tropas' in ataque:
                    tropas = ataque['tropas']
                    resumen_jugadores[jugador]['total_tropas'] += (
                        tropas.get('hachas', 0) +
                        tropas.get('ligeras', 0) +
                        tropas.get('arq_caballo', 0) +
                        tropas.get('arietes', 0) +
                        tropas.get('catapultas', 0)
                    )
        
        # Escribir resumen
        if resumen_jugadores:
            f.write("[b][size=12]📊 RESUMEN POR JUGADOR[/size][/b]\n\n")
            f.write("[table]\n")
            f.write("[**]Jugador[||]Ofensivas[||]Total Tropas[/**]\n")
            
            # Ordenar por número de ofensivas (descendente)
            for jugador, datos in sorted(resumen_jugadores.items(), key=lambda x: x[1]['total_ataques'], reverse=True):
                f.write(f"[*][player]{jugador}[/player]")
                f.write(f"[|]{datos['total_ataques']}")
                if datos['total_tropas'] > 0:
                    f.write(f"[|]{datos['total_tropas']:,}")
                else:
                    f.write("[|]-")
                f.write("\n")
            
            f.write("[/table]\n")
        
        if 'balance_jugadores' in plan:
            f.write("\n[b]Balance de ataques:[/b]\n")
            for jugador, ataques in plan['balance_jugadores'].items():
                f.write(f"• {jugador}: {ataques} ataques\n")
    
    print(f"✅ BBCode exportado a: {ruta_archivo}")


def mostrar_resumen_consola(plan):
    """
    Muestra un resumen del plan en consola.
    
    Args:
        plan: plan de ataque
    """
    print("\n" + "="*80)
    print("📋 RESUMEN DEL PLAN DE ATAQUE")
    print("="*80)
    
    total_ataques = sum(len(obj['ataques']) for obj in plan['objetivos'])
    
    print(f"\n🎯 Objetivos: {len(plan['objetivos'])}")
    print(f"⚔️  Total de ataques: {total_ataques}")
    
    if plan.get('pueblos_sin_asignar'):
        print(f"📍 Pueblos sin asignar: {len(plan['pueblos_sin_asignar'])}")
    
    if 'hora_llegada_objetivo' in plan:
        print(f"⏰ Hora de llegada: {plan['hora_llegada_objetivo']}")
    
    print("\n" + "-"*80)
    
    for idx, objetivo in enumerate(plan['objetivos'], 1):
        print(f"\nObjetivo {idx}: {objetivo['nombre']} ({objetivo['coordenadas']})")
        print(f"  Ataques: {len(objetivo['ataques'])}")
        
        if objetivo['ataques']:
            distancias = [a['distancia'] for a in objetivo['ataques']]
            print(f"  Distancia promedio: {sum(distancias)/len(distancias):.2f} campos")
            print(f"  Distancia min/max: {min(distancias):.2f} / {max(distancias):.2f}")
    
    if 'balance_jugadores' in plan:
        print("\n" + "-"*80)
        print("\n⚖️  Balance de ataques por jugador:")
        for jugador, ataques in sorted(plan['balance_jugadores'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {jugador}: {ataques} ataques")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    print("=== Módulo de Exportación ===")
    print("Importa este módulo desde main.py para exportar planes")
