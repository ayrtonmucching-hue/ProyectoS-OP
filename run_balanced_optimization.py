#!/usr/bin/env python3
"""
Ejecutar Optimización Balanceada S&OP
Genera plan de suministro optimizado con política ROP
"""

import sys
from pathlib import Path

# Agregar src al path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from optimization.balanced_sop import BalancedSOPOptimizer


def main():
    """Ejecutar optimización balanceada."""
    
    print("\n" + "="*70)
    print("  OPTIMIZACIÓN BALANCEADA S&OP")
    print("  Política ROP: Eliminar stockouts sin sobreinventario")
    print("="*70)
    
    # Inicializar optimizador
    optimizer = BalancedSOPOptimizer()
    
    # Paso 1: Cargar datos
    inventory_df, demand_df, supply_df = optimizer.load_data()
    
    # Paso 2: Generar plan optimizado
    optimized_plan = optimizer.optimize_supply_plan(
        inventory_df=inventory_df,
        demand_df=demand_df,
        supply_df=supply_df
    )
    
    # Paso 3: Generar resumen comparativo
    print("\n" + "="*70)
    print("  GENERANDO RESUMEN COMPARATIVO")
    print("="*70)
    
    summary = optimizer.generate_comparison_summary(optimized_plan)
    
    # Mostrar mejoras totales
    print("\nMEJORAS TOTALES:")
    print(f"  - Stockouts eliminados: {summary['Stockout_Reduction'].sum()}")
    print(f"  - Periodos bajo safety stock reducidos: {summary['Safety_Improvement'].sum()}")
    print(f"  - Ordenes generadas: {summary['Orders_Generated'].sum()}")
    
    # Paso 4: Exportar resultados
    print("\n" + "="*70)
    print("  EXPORTANDO RESULTADOS")
    print("="*70)
    
    # Plan optimizado completo
    optimizer.export_to_excel(
        optimized_plan,
        output_file="outputs/plans/sop_balanced_plan.xlsx"
    )
    
    # Resumen comparativo
    summary.to_csv("outputs/reports/optimization_summary.csv", index=False)
    print("[OK] Resumen comparativo exportado a: outputs/reports/optimization_summary.csv")
    
    # Plan en CSV para fácil análisis
    optimized_plan.to_csv("outputs/plans/sop_balanced_plan.csv", index=False)
    print("[OK] Plan en CSV exportado a: outputs/plans/sop_balanced_plan.csv")
    
    print("\n" + "="*70)
    print("  OPTIMIZACIÓN COMPLETADA")
    print("="*70)
    print("\nArchivos generados:")
    print("  1. outputs/plans/sop_balanced_plan.xlsx - Plan optimizado completo")
    print("  2. outputs/plans/sop_balanced_plan.csv - Plan en CSV")
    print("  3. outputs/reports/optimization_summary.csv - Resumen comparativo")
    print("\nPara visualizar resultados, ejecuta:")
    print("  python generate_optimization_charts.py")
    print("  streamlit run optimization_dashboard.py")
    print("="*70 + "\n")
    
    return 0


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
