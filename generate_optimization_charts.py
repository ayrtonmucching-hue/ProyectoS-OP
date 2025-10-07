#!/usr/bin/env python3
"""
Generador de Graficos de Optimizacion S&OP
Crea visualizaciones SEPARADAS y LIMPIAS para analisis antes/despues
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import warnings
import sys

warnings.filterwarnings('ignore')

# Configuracion de estilo basico
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['axes.facecolor'] = '#f5f5f5'
plt.rcParams['axes.grid'] = True
plt.rcParams['grid.alpha'] = 0.3

# Crear directorio de salida
OUTPUT_DIR = Path("outputs/dashboards/optimization")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_optimization_data():
    """Cargar datos de optimizacion."""
    print("Cargando datos de optimizacion...")
    
    plan = pd.read_csv("outputs/plans/sop_balanced_plan.csv")
    summary = pd.read_csv("outputs/reports/optimization_summary.csv")
    
    plan['Period'] = pd.to_datetime(plan['Period'])
    
    print(f"  [OK] Plan: {len(plan)} registros")
    print(f"  [OK] Resumen: {len(summary)} SKUs")
    
    return plan, summary


def chart_01_stockout_comparison(summary):
    """Grafico 1: Comparacion de Stockouts Original vs Optimizado."""
    print("\n[GRAFICO 1] Generando: Comparacion de Stockouts")
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    x = np.arange(len(summary))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, summary['Stockouts_Original'], width, 
                   label='Original', color='#e74c3c', alpha=0.8)
    bars2 = ax.bar(x + width/2, summary['Stockouts_Optimized'], width,
                   label='Optimizado', color='#27ae60', alpha=0.8)
    
    ax.set_xlabel('SKU', fontsize=12, fontweight='bold')
    ax.set_ylabel('Periodos con Stockout', fontsize=12, fontweight='bold')
    ax.set_title('Comparacion de Stockouts: Original vs Optimizado', 
                 fontsize=14, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(summary['SKU'], rotation=45, ha='right')
    ax.legend(fontsize=11)
    ax.grid(axis='y', alpha=0.3)
    
    # Anadir valores en las barras
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{int(height)}',
                       ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    output_file = OUTPUT_DIR / "01_stockout_comparison.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"  [OK] Guardado: {output_file}")


def chart_02_inventory_levels(summary):
    """Grafico 2: Comparacion de Niveles de Inventario Promedio."""
    print("\n[GRAFICO 2] Generando: Niveles de Inventario Promedio")
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    x = np.arange(len(summary))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, summary['Avg_Inventory_Original'], width,
                   label='Original', color='#3498db', alpha=0.8)
    bars2 = ax.bar(x + width/2, summary['Avg_Inventory_Optimized'], width,
                   label='Optimizado', color='#9b59b6', alpha=0.8)
    
    ax.set_xlabel('SKU', fontsize=12, fontweight='bold')
    ax.set_ylabel('Inventario Promedio', fontsize=12, fontweight='bold')
    ax.set_title('Comparacion de Inventario Promedio: Original vs Optimizado',
                 fontsize=14, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(summary['SKU'], rotation=45, ha='right')
    ax.legend(fontsize=11)
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    output_file = OUTPUT_DIR / "02_inventory_levels.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"  [OK] Guardado: {output_file}")


def chart_03_inventory_projection_samples(plan, num_skus=4):
    """Grafico 3: Proyeccion de Inventario para SKUs de muestra (LIMPIO, uno por uno)."""
    print(f"\n[GRAFICO 3] Generando: Proyeccion de Inventario ({num_skus} SKUs)")
    
    # Seleccionar SKUs para mostrar (primeros N)
    skus_to_plot = plan['SKU'].unique()[:num_skus]
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 10))
    axes = axes.flatten()
    
    for idx, sku in enumerate(skus_to_plot):
        ax = axes[idx]
        sku_data = plan[plan['SKU'] == sku].sort_values('Period')
        
        # Lineas de inventario
        ax.plot(sku_data['Period'], sku_data['Projected_Inventory_Original'],
               label='Original', color='#e74c3c', linewidth=2, marker='o', markersize=4)
        ax.plot(sku_data['Period'], sku_data['Projected_Inventory_Optimized'],
               label='Optimizado', color='#27ae60', linewidth=2, marker='s', markersize=4)
        
        # Lineas de referencia
        safety_stock = sku_data['Safety_Stock'].iloc[0]
        max_stock = sku_data['Max_Stock'].iloc[0]
        
        ax.axhline(y=safety_stock, color='orange', linestyle='--', 
                  linewidth=1.5, label='Safety Stock', alpha=0.7)
        ax.axhline(y=max_stock, color='blue', linestyle='--',
                  linewidth=1.5, label='Max Stock', alpha=0.7)
        ax.axhline(y=0, color='red', linestyle='-', linewidth=1, alpha=0.5)
        
        ax.set_title(f'{sku}', fontsize=12, fontweight='bold')
        ax.set_xlabel('Periodo', fontsize=10)
        ax.set_ylabel('Inventario', fontsize=10)
        ax.legend(fontsize=8, loc='best')
        ax.grid(True, alpha=0.3)
        ax.tick_params(axis='x', rotation=45)
        
        # Formatear fechas en el eje x
        ax.tick_params(axis='x', labelsize=8)
    
    plt.suptitle('Proyeccion de Inventario: Original vs Optimizado',
                fontsize=16, fontweight='bold', y=0.995)
    plt.tight_layout()
    
    output_file = OUTPUT_DIR / "03_inventory_projection_samples.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"  [OK] Guardado: {output_file}")


def chart_04_improvement_metrics(summary):
    """Grafico 4: Metricas de Mejora Consolidadas."""
    print("\n[GRAFICO 4] Generando: Metricas de Mejora")
    
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    
    # Metrica 1: Reduccion de Stockouts
    total_stockouts_before = summary['Stockouts_Original'].sum()
    total_stockouts_after = summary['Stockouts_Optimized'].sum()
    stockout_reduction = total_stockouts_before - total_stockouts_after
    
    axes[0].bar(['Original', 'Optimizado'], 
               [total_stockouts_before, total_stockouts_after],
               color=['#e74c3c', '#27ae60'], alpha=0.8)
    axes[0].set_title('Total Stockouts', fontsize=12, fontweight='bold')
    axes[0].set_ylabel('Periodos', fontsize=10)
    axes[0].grid(axis='y', alpha=0.3)
    
    for i, v in enumerate([total_stockouts_before, total_stockouts_after]):
        axes[0].text(i, v, f'{int(v)}', ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    # Metrica 2: Periodos bajo Safety Stock
    total_below_before = summary['Below_Safety_Original'].sum()
    total_below_after = summary['Below_Safety_Optimized'].sum()
    
    axes[1].bar(['Original', 'Optimizado'],
               [total_below_before, total_below_after],
               color=['#f39c12', '#3498db'], alpha=0.8)
    axes[1].set_title('Periodos Bajo Safety Stock', fontsize=12, fontweight='bold')
    axes[1].set_ylabel('Periodos', fontsize=10)
    axes[1].grid(axis='y', alpha=0.3)
    
    for i, v in enumerate([total_below_before, total_below_after]):
        axes[1].text(i, v, f'{int(v)}', ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    # Metrica 3: Ordenes Generadas
    total_orders = summary['Orders_Generated'].sum()
    
    axes[2].bar(['Ordenes\nGeneradas'], [total_orders], 
               color='#9b59b6', alpha=0.8)
    axes[2].set_title('Ordenes de Reposicion Generadas', fontsize=12, fontweight='bold')
    axes[2].set_ylabel('Ordenes', fontsize=10)
    axes[2].grid(axis='y', alpha=0.3)
    axes[2].text(0, total_orders, f'{int(total_orders)}', 
                ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    plt.suptitle('Metricas de Mejora del Plan Optimizado', 
                fontsize=16, fontweight='bold', y=1.02)
    plt.tight_layout()
    
    output_file = OUTPUT_DIR / "04_improvement_metrics.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"  [OK] Guardado: {output_file}")


def chart_05_summary_table(summary):
    """Grafico 5: Tabla de Resumen por SKU."""
    print("\n[GRAFICO 5] Generando: Tabla de Resumen")
    
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.axis('tight')
    ax.axis('off')
    
    # Preparar datos para tabla
    table_data = summary[[
        'SKU',
        'Stockouts_Original',
        'Stockouts_Optimized',
        'Stockout_Reduction',
        'Orders_Generated'
    ]].copy()
    
    table_data.columns = [
        'SKU',
        'Stockouts\nOriginal',
        'Stockouts\nOptimizado',
        'Reduccion\nStockouts',
        'Ordenes\nGeneradas'
    ]
    
    # Crear tabla
    table = ax.table(cellText=table_data.values,
                    colLabels=table_data.columns,
                    cellLoc='center',
                    loc='center',
                    bbox=[0, 0, 1, 1])
    
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2)
    
    # Estilo de encabezados
    for i in range(len(table_data.columns)):
        cell = table[(0, i)]
        cell.set_facecolor('#34495e')
        cell.set_text_props(weight='bold', color='white', fontsize=11)
    
    # Colorear filas alternas
    for i in range(1, len(table_data) + 1):
        for j in range(len(table_data.columns)):
            cell = table[(i, j)]
            if i % 2 == 0:
                cell.set_facecolor('#ecf0f1')
            
            # Resaltar mejoras
            if j == 3:  # Columna de reduccion
                value = table_data.iloc[i-1, j]
                if value > 0:
                    cell.set_facecolor('#d5f4e6')  # Verde claro
                    cell.set_text_props(weight='bold', color='#27ae60')
    
    plt.title('Resumen de Optimizacion por SKU', 
             fontsize=16, fontweight='bold', pad=20)
    
    output_file = OUTPUT_DIR / "05_summary_table.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"  [OK] Guardado: {output_file}")


def main():
    """Generar todos los graficos de optimizacion."""
    
    print("\n" + "="*70)
    print("  GENERADOR DE GRAFICOS DE OPTIMIZACION S&OP")
    print("  Visualizaciones separadas y limpias")
    print("="*70)
    
    # Cargar datos
    plan, summary = load_optimization_data()
    
    # Generar graficos
    chart_01_stockout_comparison(summary)
    chart_02_inventory_levels(summary)
    chart_03_inventory_projection_samples(plan, num_skus=4)
    chart_04_improvement_metrics(summary)
    chart_05_summary_table(summary)
    
    print("\n" + "="*70)
    print("  GRAFICOS GENERADOS EXITOSAMENTE")
    print("="*70)
    print(f"\nArchivos generados en: {OUTPUT_DIR}")
    print("  1. 01_stockout_comparison.png")
    print("  2. 02_inventory_levels.png")
    print("  3. 03_inventory_projection_samples.png")
    print("  4. 04_improvement_metrics.png")
    print("  5. 05_summary_table.png")
    print("\n[OK] Todos los graficos estan listos para presentacion")
    print("="*70 + "\n")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
