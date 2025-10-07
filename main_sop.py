#!/usr/bin/env python3
"""
S&OP Planning Tool - Main Execution Script

Este script ejecuta el flujo completo de S&OP Planning:
1. Carga de datos de inventario, demanda y suministro
2. Proyección de inventarios y coberturas
3. Análisis de riesgos (stockout, overstock)
4. Generación de planes de reposición (DRP)
5. Análisis de demanda restringida
6. Reportes y visualizaciones
"""

import sys
import os
from pathlib import Path
import warnings
import pandas as pd
import numpy as np

# Agregar src al path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from utils.config_loader import load_config
from inventory.projections import InventoryProjector
from replenishment.drp import DRPPlanner

# Suprimir warnings no críticos
warnings.filterwarnings('ignore')

def create_output_directories(config):
    """Crear directorios de salida si no existen."""
    output_dirs = [
        config['output']['reports_dir'],
        config['output']['plans_dir'],
        config['output']['dashboards_dir']
    ]

    for dir_path in output_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"[OK] Directorio creado: {dir_path}")

def load_real_data():
    """Cargar datos reales desde archivos Excel."""
    
    try:
        print("Cargando datos desde archivos Excel...")
        
        # Cargar datos de inventario
        print("  - Cargando inventario...")
        inventory_df = pd.read_excel("data/inventory_template.xlsx")
        
        # Cargar datos de demanda
        print("  - Cargando demanda...")
        demand_df = pd.read_excel("data/demand_template.xlsx")
        
        # Cargar datos de suministro
        print("  - Cargando suministro...")
        supply_df = pd.read_excel("data/supply_template.xlsx")
        
        # Validar y convertir fechas
        if 'Period' in demand_df.columns:
            demand_df['Period'] = pd.to_datetime(demand_df['Period'])
        
        if 'Period' in supply_df.columns:
            supply_df['Period'] = pd.to_datetime(supply_df['Period'])
        
        # Validar columnas requeridas
        required_inventory_cols = ['SKU', 'Opening_Inventory', 'Safety_Stock', 'Max_Stock', 
                                 'Lead_Time_Days', 'MOQ', 'Shelf_Life_Days']
        required_demand_cols = ['SKU', 'Period', 'Demand']
        required_supply_cols = ['SKU', 'Period', 'Supply']
        
        # Verificar columnas de inventario
        missing_inv_cols = [col for col in required_inventory_cols if col not in inventory_df.columns]
        if missing_inv_cols:
            raise ValueError(f"Columnas faltantes en inventario: {missing_inv_cols}")
        
        # Verificar columnas de demanda
        missing_dem_cols = [col for col in required_demand_cols if col not in demand_df.columns]
        if missing_dem_cols:
            raise ValueError(f"Columnas faltantes en demanda: {missing_dem_cols}")
        
        # Verificar columnas de suministro
        missing_sup_cols = [col for col in required_supply_cols if col not in supply_df.columns]
        if missing_sup_cols:
            raise ValueError(f"Columnas faltantes en suministro: {missing_sup_cols}")
        
        print(f"[OK] Datos cargados exitosamente:")
        print(f"  - Inventario: {len(inventory_df)} SKUs")
        print(f"  - Demanda: {len(demand_df)} registros")
        print(f"  - Suministro: {len(supply_df)} registros")
        
        return inventory_df, demand_df, supply_df
        
    except FileNotFoundError as e:
        print(f"[ERROR] Archivo no encontrado: {e}")
        print("Asegúrate de que los archivos estén en la carpeta 'data/' con los nombres correctos:")
        print("  - data/inventory_template.xlsx")
        print("  - data/demand_template.xlsx") 
        print("  - data/supply_template.xlsx")
        raise
    
    except Exception as e:
        print(f"[ERROR] Error al cargar datos: {e}")
        raise

def load_sample_data():
    """Cargar datos de ejemplo para demostración."""
    
    # Crear datos de demanda de ejemplo
    periods = pd.date_range(start='2024-01-01', periods=26, freq='W')
    skus = ['SKU001', 'SKU002', 'SKU003', 'SKU004', 'SKU005']
    
    demand_data = []
    for sku in skus:
        base_demand = np.random.randint(20, 100)
        for period in periods:
            # Agregar algo de variabilidad y estacionalidad
            seasonal_factor = 1 + 0.2 * np.sin(2 * np.pi * period.dayofyear / 365)
            noise = np.random.normal(1, 0.1)
            demand = max(0, int(base_demand * seasonal_factor * noise))
            
            demand_data.append({
                'SKU': sku,
                'Period': period,
                'Demand': demand
            })
    
    demand_df = pd.DataFrame(demand_data)
    
    # Datos de inventario (ya creados en sample_inventory.xlsx)
    inventory_data = {
        'SKU': ['SKU001', 'SKU002', 'SKU003', 'SKU004', 'SKU005'],
        'Opening_Inventory': [150, 75, 200, 45, 300],
        'Safety_Stock': [50, 25, 80, 15, 100],
        'Max_Stock': [500, 300, 600, 200, 800],
        'Lead_Time_Days': [7, 5, 10, 3, 14],
        'MOQ': [100, 50, 150, 25, 200],
        'Shelf_Life_Days': [365, 180, 90, 365, 730]
    }
    inventory_df = pd.DataFrame(inventory_data)
    
    # Datos de suministro (plan de reposición inicial)
    supply_data = []
    for sku in skus:
        for i, period in enumerate(periods):
            # Suministro cada 2 semanas aproximadamente
            if i % 2 == 0:
                supply = np.random.randint(50, 200)
                supply_data.append({
                    'SKU': sku,
                    'Period': period,
                    'Supply': supply
                })
    
    supply_df = pd.DataFrame(supply_data) if supply_data else pd.DataFrame(columns=['SKU', 'Period', 'Supply'])
    
    return inventory_df, demand_df, supply_df

def main():
    """Función principal que ejecuta todo el flujo de S&OP."""
    print("="*70)
    print("SUPPLY CHAIN S&OP PLANNING TOOL")
    print("="*70)

    try:
        # 1. Cargar configuración
        print("\nCargando configuracion...")
        config = load_config("config/sop_config.yaml")
        print("[OK] Configuracion cargada exitosamente")

        # 2. Crear directorios de salida
        print("\nCreando directorios de salida...")
        create_output_directories(config)

        # 3. Cargar datos reales
        print("\nCargando datos reales...")
        inventory_df, demand_df, supply_df = load_real_data()
        
        print(f"[OK] Inventario: {len(inventory_df)} SKUs")
        print(f"[OK] Demanda: {len(demand_df)} registros")
        print(f"[OK] Suministro: {len(supply_df)} registros")

        # 4. Inicializar proyector de inventarios
        print("\nInicializando proyector de inventarios...")
        projector = InventoryProjector(config)

        # 5. Realizar proyecciones por SKU
        print("\nCalculando proyecciones de inventario...")
        projections = projector.multi_sku_projection(
            inventory_df, 
            demand_df, 
            supply_df
        )

        # 6. Generar análisis ABC
        print("\nRealizando analisis ABC...")
        abc_analysis = projector.calculate_abc_analysis(demand_df)
        print(f"[OK] Clasificacion ABC completada:")
        print(f"  - Clase A: {len(abc_analysis[abc_analysis['ABC_Class'] == 'A'])} SKUs")
        print(f"  - Clase B: {len(abc_analysis[abc_analysis['ABC_Class'] == 'B'])} SKUs")
        print(f"  - Clase C: {len(abc_analysis[abc_analysis['ABC_Class'] == 'C'])} SKUs")

        # 7. Identificar riesgos
        print("\nAnalizando riesgos...")
        risk_summary = {}
        
        for sku, proj_df in projections.items():
            risks = {
                'stockouts': proj_df['Stockout_Risk'].sum(),
                'low_coverage': proj_df['Low_Coverage'].sum(),
                'below_safety': proj_df['Below_Safety'].sum() if 'Below_Safety' in proj_df.columns else 0
            }
            risk_summary[sku] = risks

        # Mostrar resumen de riesgos
        total_stockouts = sum(r['stockouts'] for r in risk_summary.values())
        total_low_coverage = sum(r['low_coverage'] for r in risk_summary.values())
        
        print(f"[WARNING] Riesgos identificados:")
        print(f"  - Riesgo de stockout: {total_stockouts} períodos")
        print(f"  - Cobertura baja: {total_low_coverage} períodos")

        # 8. Calcular DRP (Distribution Requirement Planning)
        print("\nCalculando planes de reposicion (DRP)...")
        drp_planner = DRPPlanner(config)
        drp_results = drp_planner.calculate_drp(
            inventory_df,
            demand_df,
            supply_df
        )
        
        # Generar resumen de órdenes
        order_summary = drp_planner.calculate_order_summary(drp_results)
        drp_metrics = drp_planner.generate_drp_metrics(drp_results)
        
        print(f"[OK] DRP completado:")
        print(f"  - Ordenes requeridas: {drp_metrics['total_orders']}")
        print(f"  - Nivel de servicio promedio: {drp_metrics['avg_service_level']:.1f}%")
        print(f"  - Periodos con stockout: {drp_metrics['stockout_periods']}")

        # 9. Guardar resultados
        print("\nGuardando resultados...")
        
        # Guardar proyecciones por SKU
        for sku, proj_df in projections.items():
            output_path = f"{config['output']['reports_dir']}/projection_{sku}.csv"
            proj_df.to_csv(output_path, index=False)
        
        # Guardar planes DRP por SKU
        for sku, drp_df in drp_results.items():
            drp_path = f"{config['output']['plans_dir']}/drp_plan_{sku}.csv"
            drp_df.to_csv(drp_path, index=False)
        
        # Guardar resumen de órdenes
        if not order_summary.empty:
            orders_path = f"{config['output']['plans_dir']}/order_summary.csv"
            order_summary.to_csv(orders_path, index=False)
        
        # Guardar métricas DRP
        metrics_df = pd.DataFrame([drp_metrics])
        metrics_path = f"{config['output']['reports_dir']}/drp_metrics.csv"
        metrics_df.to_csv(metrics_path, index=False)
        
        # Guardar análisis ABC
        abc_path = f"{config['output']['reports_dir']}/abc_analysis.csv"
        abc_analysis.to_csv(abc_path, index=False)
        
        # Guardar resumen de riesgos
        risk_df = pd.DataFrame(risk_summary).T
        risk_path = f"{config['output']['reports_dir']}/risk_summary.csv"
        risk_df.to_csv(risk_path)

        print("\n" + "="*70)
        print("EJECUCION S&OP COMPLETADA EXITOSAMENTE")
        print("="*70)
        print("Archivos generados en:")
        print(f"   - Proyecciones: {config['output']['reports_dir']}/projection_*.csv")
        print(f"   - Planes DRP: {config['output']['plans_dir']}/drp_plan_*.csv")
        print(f"   - Resumen ordenes: {config['output']['plans_dir']}/order_summary.csv")
        print(f"   - Metricas DRP: {metrics_path}")
        print(f"   - Analisis ABC: {abc_path}")
        print(f"   - Resumen riesgos: {risk_path}")
        
        # Mostrar ejemplo de DRP
        sample_sku = list(drp_results.keys())[0]
        sample_drp = drp_results[sample_sku]
        
        print(f"\nEjemplo - Plan DRP {sample_sku} (primeras 5 semanas):")
        columns_to_show = ['Period', 'Final_Inventory', 'Order_Needed', 'Order_Quantity', 'Service_Level']
        print(sample_drp.head()[columns_to_show].to_string(index=False))
        
        # Mostrar resumen de órdenes si hay
        if not order_summary.empty:
            print(f"\nResumen de Ordenes (primeras 5):")
            print(order_summary.head()[['SKU', 'Order_Period', 'Order_Quantity', 'Reason']].to_string(index=False))

    except Exception as e:
        print(f"\n[ERROR] Error durante la ejecucion: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
