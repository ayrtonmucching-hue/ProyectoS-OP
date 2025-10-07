#!/usr/bin/env python3
"""
Test del DRP Simulation Module
"""

import sys
from pathlib import Path

# Agregar src al path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from utils.config_loader import load_config
from simulation.drp_simulator import DRPSimulator
import pandas as pd

def test_drp_simulation():
    """Probar el simulador DRP."""
    
    print("="*60)
    print("TEST DRP SIMULATION MODULE")
    print("="*60)
    
    try:
        # 1. Cargar configuración
        print("Cargando configuración...")
        config = load_config("config/sop_config.yaml")
        
        # 2. Cargar datos base
        print("Cargando datos base...")
        inventory_df = pd.read_excel("data/inventory_template.xlsx")
        demand_df = pd.read_excel("data/demand_template.xlsx")
        supply_df = pd.read_excel("data/supply_template.xlsx")
        
        # Convertir fechas
        demand_df['Period'] = pd.to_datetime(demand_df['Period'])
        supply_df['Period'] = pd.to_datetime(supply_df['Period'])
        
        print(f"  - Inventario: {len(inventory_df)} SKUs")
        print(f"  - Demanda: {len(demand_df)} registros")
        print(f"  - Suministro: {len(supply_df)} registros")
        
        # 3. Inicializar simulador
        print("Inicializando simulador...")
        simulator = DRPSimulator(config)
        
        # 4. Ejecutar simulación con 2 escenarios
        print("Ejecutando simulación...")
        simulation_results = simulator.run_multiple_scenarios(
            inventory_df, demand_df, supply_df, 
            scenarios_to_run=['Conservative', 'Aggressive']
        )
        
        # 5. Mostrar resultados
        print("\n" + "="*60)
        print("RESULTADOS DE SIMULACIÓN")
        print("="*60)
        
        comparison_df = simulator.compare_scenarios(simulation_results)
        print("\nComparación de Escenarios:")
        print(comparison_df[['scenario_name', 'avg_service_level', 'total_orders', 
                           'total_order_quantity', 'stockout_periods']].to_string(index=False))
        
        # 6. Exportar resultados
        print("\nExportando resultados...")
        output_path = simulator.export_simulation_results(simulation_results)
        print(f"Resultados exportados en: {output_path}")
        
        print("\n" + "="*60)
        print("TEST COMPLETADO EXITOSAMENTE")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Error durante el test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_drp_simulation()
    sys.exit(0 if success else 1)
