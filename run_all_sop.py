#!/usr/bin/env python3
"""
Script Maestro S&OP - Ejecuta todo el flujo completo
Ejecuta análisis, genera reportes y dashboards
"""

import subprocess
import sys
from pathlib import Path
import time

def print_header(title):
    """Imprimir encabezado formateado."""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")

def run_script(script_name, description):
    """Ejecutar un script Python y manejar errores."""
    print_header(description)
    print(f"Ejecutando: {script_name}")
    print("-" * 70)
    
    try:
        result = subprocess.run(
            [sys.executable, script_name],
            check=True,
            capture_output=False
        )
        print(f"\n[OK] {description} completado exitosamente")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] Error ejecutando {script_name}: {e}")
        return False

def open_dashboard(dashboard_name):
    """Abrir dashboard de Streamlit en nueva ventana de terminal."""
    import platform
    
    print(f"\nAbriendo dashboard: {dashboard_name}")
    
    try:
        system = platform.system()
        
        if system == "Windows":
            # En Windows, usar start con cmd
            subprocess.Popen(
                f'start cmd /k "streamlit run {dashboard_name}"',
                shell=True
            )
        elif system == "Darwin":  # macOS
            subprocess.Popen(
                ["open", "-a", "Terminal", "-n", "--args", "streamlit", "run", dashboard_name]
            )
        else:  # Linux
            # Intentar con varios emuladores de terminal comunes
            terminals = ["gnome-terminal", "xterm", "konsole", "terminator"]
            for terminal in terminals:
                try:
                    subprocess.Popen([terminal, "-e", f"streamlit run {dashboard_name}"])
                    break
                except FileNotFoundError:
                    continue
        
        print(f"[OK] Dashboard {dashboard_name} abierto en nueva ventana")
        time.sleep(2)  # Dar tiempo para que se abra
        return True
        
    except Exception as e:
        print(f"[WARNING] No se pudo abrir automaticamente: {e}")
        return False

def main():
    """Ejecutar flujo completo S&OP."""
    
    print("\n" + "="*70)
    print("  FLUJO COMPLETO S&OP - SUPPLY CHAIN PLANNING")
    print("="*70)
    print("\nEste script ejecutara:")
    print("  1. Analisis S&OP principal (proyecciones, DRP, ABC)")
    print("  2. Optimizacion Balanceada (Politica ROP)")
    print("  3. Generacion de dashboards PNG (simulacion DRP + optimizacion)")
    print("  4. Apertura de dashboards interactivos (opcional)")
    print("\nPresiona Ctrl+C para cancelar en cualquier momento")
    print("="*70)
    
    input("\nPresiona Enter para comenzar...")
    
    start_time = time.time()
    
    # PASO 1: Ejecutar análisis S&OP principal
    success = run_script(
        "main_sop.py",
        "PASO 1/4: Analisis S&OP Principal"
    )
    
    if not success:
        print("\n[ERROR] El analisis S&OP fallo. Abortando ejecucion.")
        return 1
    
    # PASO 2: Ejecutar optimización balanceada
    success = run_script(
        "run_balanced_optimization.py",
        "PASO 2/4: Optimizacion Balanceada (Politica ROP)"
    )
    
    if not success:
        print("\n[WARNING] Optimizacion fallo, continuando con analisis base.")
    
    # PASO 3: Generar dashboards PNG de simulación DRP
    success = run_script(
        "generate_drp_simulation_charts.py",
        "PASO 3/4: Generacion de Dashboards PNG (Simulacion DRP)"
    )
    
    if not success:
        print("\n[WARNING] Generacion de dashboards DRP fallo.")
    
    # PASO 4: Generar dashboards PNG de optimización
    success = run_script(
        "generate_optimization_charts.py",
        "PASO 4/4: Generacion de Dashboards PNG (Optimizacion)"
    )
    
    if not success:
        print("\n[WARNING] Generacion de dashboards de optimizacion fallo.")
    
    # Resumen final
    elapsed_time = time.time() - start_time
    
    print("\n" + "="*70)
    print("  FLUJO S&OP COMPLETADO")
    print("="*70)
    print(f"\nTiempo total: {elapsed_time:.2f} segundos")
    print("\nARCHIVOS GENERADOS:")
    print("\n1. Reportes CSV:")
    print("   - outputs/reports/abc_analysis.csv")
    print("   - outputs/reports/risk_summary.csv")
    print("   - outputs/reports/drp_metrics.csv")
    print("   - outputs/reports/projection_*.csv (por SKU)")
    print("   - outputs/reports/optimization_summary.csv")
    
    print("\n2. Planes DRP:")
    print("   - outputs/plans/drp_*.csv (por SKU)")
    print("   - outputs/plans/order_summary.csv")
    
    print("\n3. Plan Optimizado:")
    print("   - outputs/plans/sop_balanced_plan.xlsx")
    print("   - outputs/plans/sop_balanced_plan.csv")
    
    print("\n4. Dashboards PNG Simulacion DRP:")
    print("   - outputs/dashboards/drp_simulation/01_scenario_comparison.png")
    print("   - outputs/dashboards/drp_simulation/02_metrics_radar.png")
    print("   - outputs/dashboards/drp_simulation/03_detailed_metrics.png")
    print("   - outputs/dashboards/drp_simulation/04_summary_table.png")
    
    print("\n5. Dashboards PNG Optimizacion:")
    print("   - outputs/dashboards/optimization/01_stockout_comparison.png")
    print("   - outputs/dashboards/optimization/02_inventory_levels.png")
    print("   - outputs/dashboards/optimization/03_inventory_projection_samples.png")
    print("   - outputs/dashboards/optimization/04_improvement_metrics.png")
    print("   - outputs/dashboards/optimization/05_summary_table.png")
    
    print("\n6. Datos de Simulacion:")
    print("   - outputs/simulation/scenario_comparison.csv")
    print("   - outputs/simulation/[escenario]/drp_*.csv")
    
    print("\n" + "="*70)
    print("  DASHBOARDS INTERACTIVOS")
    print("="*70)
    
    # Preguntar si desea abrir dashboards
    print("\n¿Deseas abrir los dashboards interactivos ahora?")
    print("  1. Si - Abrir todos los dashboards (S&OP + DRP + Optimizacion)")
    print("  2. Solo dashboard S&OP principal")
    print("  3. Solo dashboard Simulacion DRP")
    print("  4. Solo dashboard Optimizacion")
    print("  5. No - Salir")
    
    try:
        choice = input("\nSelecciona una opcion (1-5): ").strip()
        
        if choice == "1":
            print_header("Abriendo Todos los Dashboards")
            open_dashboard("dashboard_sop.py")
            open_dashboard("drp_simulation_dashboard.py")
            open_dashboard("optimization_dashboard.py")
            print("\n[INFO] Los dashboards se estan iniciando en nuevas ventanas.")
            print("[INFO] Presiona Ctrl+C en cada ventana para detenerlos.")
            
        elif choice == "2":
            print_header("Abriendo Dashboard S&OP Principal")
            open_dashboard("dashboard_sop.py")
            
        elif choice == "3":
            print_header("Abriendo Dashboard Simulacion DRP")
            open_dashboard("drp_simulation_dashboard.py")
            
        elif choice == "4":
            print_header("Abriendo Dashboard Optimizacion")
            open_dashboard("optimization_dashboard.py")
            
        else:
            print("\n[INFO] Saliendo sin abrir dashboards.")
            print("\nPara abrirlos manualmente mas tarde, ejecuta:")
            print("  streamlit run dashboard_sop.py")
            print("  streamlit run drp_simulation_dashboard.py")
            print("  streamlit run optimization_dashboard.py")
    
    except KeyboardInterrupt:
        print("\n\n[INFO] Operacion cancelada.")
    
    print("\n" + "="*70)
    print("  PROCESO COMPLETO FINALIZADO")
    print("="*70 + "\n")
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n[CANCELADO] Ejecucion interrumpida por el usuario.")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
