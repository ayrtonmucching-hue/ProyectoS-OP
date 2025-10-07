#!/usr/bin/env python3
"""
Generador de Gráficos Estáticos para DRP Simulation Dashboard
Crea visualizaciones PNG de los resultados de simulación
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import sys
import warnings
warnings.filterwarnings('ignore')

# Agregar src al path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from utils.config_loader import load_config
from simulation.drp_simulator import DRPSimulator

# Configurar estilo
plt.style.use('default')
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['axes.facecolor'] = 'white'
plt.rcParams['font.size'] = 10

def create_scenario_comparison_chart(comparison_df):
    """Crear gráfico de comparación de escenarios."""
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    scenarios = comparison_df['scenario_name'].tolist()
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7'][:len(scenarios)]
    
    # 1. Nivel de Servicio
    bars1 = ax1.bar(scenarios, comparison_df['avg_service_level'], color=colors, alpha=0.8)
    ax1.set_title('Nivel de Servicio por Escenario (%)', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Porcentaje (%)')
    ax1.set_ylim(0, 100)
    
    # Añadir valores en las barras
    for bar, value in zip(bars1, comparison_df['avg_service_level']):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{value:.1f}%', ha='center', va='bottom', fontweight='bold')
    
    # 2. Total de Órdenes
    bars2 = ax2.bar(scenarios, comparison_df['total_orders'], color=colors, alpha=0.8)
    ax2.set_title('Total de Órdenes Generadas', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Número de Órdenes')
    
    for bar, value in zip(bars2, comparison_df['total_orders']):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + height*0.02,
                f'{int(value)}', ha='center', va='bottom', fontweight='bold')
    
    # 3. Cantidad Total Ordenada
    bars3 = ax3.bar(scenarios, comparison_df['total_order_quantity'], color=colors, alpha=0.8)
    ax3.set_title('Cantidad Total Ordenada', fontsize=14, fontweight='bold')
    ax3.set_ylabel('Unidades')
    
    for bar, value in zip(bars3, comparison_df['total_order_quantity']):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height + height*0.02,
                f'{int(value):,}', ha='center', va='bottom', fontweight='bold', fontsize=9)
    
    # 4. Stock de Seguridad Total
    bars4 = ax4.bar(scenarios, comparison_df['total_safety_stock'], color=colors, alpha=0.8)
    ax4.set_title('Stock de Seguridad Total', fontsize=14, fontweight='bold')
    ax4.set_ylabel('Unidades')
    
    for bar, value in zip(bars4, comparison_df['total_safety_stock']):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height + height*0.02,
                f'{int(value):,}', ha='center', va='bottom', fontweight='bold', fontsize=9)
    
    # Rotar etiquetas del eje x
    for ax in [ax1, ax2, ax3, ax4]:
        ax.tick_params(axis='x', rotation=45)
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig

def create_metrics_radar_chart(comparison_df):
    """Crear gráfico radar de métricas normalizadas."""
    
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
    
    # Definir categorías para el radar
    categories = ['Nivel Servicio', 'Eficiencia Órdenes', 'Optimización Stock', 'Lead Time']
    
    # Normalizar métricas (0-100)
    normalized_data = []
    
    for _, row in comparison_df.iterrows():
        # Nivel de servicio (ya está en %)
        service_level = row['avg_service_level']
        
        # Eficiencia de órdenes (inverso del número de órdenes, normalizado)
        max_orders = comparison_df['total_orders'].max()
        order_efficiency = 100 - ((row['total_orders'] / max_orders) * 100) if max_orders > 0 else 50
        
        # Optimización de stock (inverso del safety stock, normalizado)
        max_safety = comparison_df['total_safety_stock'].max()
        stock_optimization = 100 - ((row['total_safety_stock'] / max_safety) * 100) if max_safety > 0 else 50
        
        # Lead time (inverso del lead time promedio, normalizado)
        max_lead_time = comparison_df['avg_lead_time'].max()
        lead_time_score = 100 - ((row['avg_lead_time'] / max_lead_time) * 100) if max_lead_time > 0 else 50
        
        normalized_data.append([service_level, order_efficiency, stock_optimization, lead_time_score])
    
    # Colores para cada escenario
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
    
    # Ángulos para cada categoría
    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    angles += angles[:1]  # Cerrar el círculo
    
    # Dibujar cada escenario
    for i, (_, row) in enumerate(comparison_df.iterrows()):
        values = normalized_data[i]
        values += values[:1]  # Cerrar el círculo
        
        ax.plot(angles, values, 'o-', linewidth=2, label=row['scenario_name'], 
                color=colors[i % len(colors)])
        ax.fill(angles, values, alpha=0.25, color=colors[i % len(colors)])
    
    # Configurar el gráfico
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories)
    ax.set_ylim(0, 100)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_yticklabels(['20', '40', '60', '80', '100'])
    ax.grid(True)
    
    plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
    plt.title('Radar de Performance por Escenario', size=16, fontweight='bold', pad=20)
    
    return fig

def create_detailed_metrics_chart(comparison_df):
    """Crear gráfico detallado de métricas."""
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    scenarios = comparison_df['scenario_name'].tolist()
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7'][:len(scenarios)]
    
    # 1. Fill Rate
    bars1 = ax1.bar(scenarios, comparison_df['fill_rate'], color=colors, alpha=0.8)
    ax1.set_title('Fill Rate por Escenario (%)', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Porcentaje (%)')
    ax1.set_ylim(0, 100)
    
    for bar, value in zip(bars1, comparison_df['fill_rate']):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{value:.1f}%', ha='center', va='bottom', fontweight='bold')
    
    # 2. Lead Time Promedio
    bars2 = ax2.bar(scenarios, comparison_df['avg_lead_time'], color=colors, alpha=0.8)
    ax2.set_title('Lead Time Promedio (días)', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Días')
    
    for bar, value in zip(bars2, comparison_df['avg_lead_time']):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + height*0.02,
                f'{value:.1f}', ha='center', va='bottom', fontweight='bold')
    
    # 3. Tamaño Promedio de Orden
    bars3 = ax3.bar(scenarios, comparison_df['avg_order_size'], color=colors, alpha=0.8)
    ax3.set_title('Tamaño Promedio de Orden', fontsize=14, fontweight='bold')
    ax3.set_ylabel('Unidades por Orden')
    
    for bar, value in zip(bars3, comparison_df['avg_order_size']):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height + height*0.02,
                f'{int(value):,}', ha='center', va='bottom', fontweight='bold', fontsize=9)
    
    # 4. Períodos con Stockout
    bars4 = ax4.bar(scenarios, comparison_df['stockout_periods'], color=colors, alpha=0.8)
    ax4.set_title('Períodos con Stockout', fontsize=14, fontweight='bold')
    ax4.set_ylabel('Número de Períodos')
    
    for bar, value in zip(bars4, comparison_df['stockout_periods']):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height + max(height*0.02, 0.5),
                f'{int(value)}', ha='center', va='bottom', fontweight='bold')
    
    # Rotar etiquetas del eje x
    for ax in [ax1, ax2, ax3, ax4]:
        ax.tick_params(axis='x', rotation=45)
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig

def create_scenario_summary_table(comparison_df):
    """Crear tabla resumen de escenarios."""
    
    fig, ax = plt.subplots(figsize=(16, 8))
    ax.axis('tight')
    ax.axis('off')
    
    # Preparar datos para la tabla
    table_data = []
    headers = ['Escenario', 'Nivel Servicio (%)', 'Total Órdenes', 'Cantidad Total', 
               'Fill Rate (%)', 'Lead Time (días)', 'Safety Stock', 'Stockouts']
    
    for _, row in comparison_df.iterrows():
        table_data.append([
            row['scenario_name'],
            f"{row['avg_service_level']:.1f}%",
            f"{int(row['total_orders']):,}",
            f"{int(row['total_order_quantity']):,}",
            f"{row['fill_rate']:.1f}%",
            f"{row['avg_lead_time']:.1f}",
            f"{int(row['total_safety_stock']):,}",
            f"{int(row['stockout_periods'])}"
        ])
    
    # Crear tabla
    table = ax.table(cellText=table_data, colLabels=headers, 
                    cellLoc='center', loc='center')
    
    # Estilizar tabla
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 2)
    
    # Colorear header
    for i in range(len(headers)):
        table[(0, i)].set_facecolor('#4ECDC4')
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    # Colorear filas alternadas
    colors = ['#F8F9FA', '#E9ECEF']
    for i in range(1, len(table_data) + 1):
        for j in range(len(headers)):
            table[(i, j)].set_facecolor(colors[i % 2])
    
    plt.title('Resumen Comparativo de Escenarios DRP', fontsize=16, fontweight='bold', pad=20)
    
    return fig

def generate_drp_simulation_charts():
    """Generar todos los gráficos de simulación DRP."""
    
    print("="*70)
    print("GENERANDO GRAFICOS DRP SIMULATION DASHBOARD")
    print("="*70)
    
    try:
        # 1. Cargar configuración y datos
        print("Cargando datos...")
        config = load_config("config/sop_config.yaml")
        
        inventory_df = pd.read_excel("data/inventory_template.xlsx")
        demand_df = pd.read_excel("data/demand_template.xlsx")
        supply_df = pd.read_excel("data/supply_template.xlsx")
        
        # Convertir fechas
        demand_df['Period'] = pd.to_datetime(demand_df['Period'])
        supply_df['Period'] = pd.to_datetime(supply_df['Period'])
        
        # 2. Ejecutar simulación
        print("Ejecutando simulacion DRP...")
        simulator = DRPSimulator(config)
        
        # Ejecutar todos los escenarios
        simulation_results = simulator.run_multiple_scenarios(
            inventory_df, demand_df, supply_df
        )
        
        # Obtener comparación
        comparison_df = simulator.compare_scenarios(simulation_results)
        
        print(f"Simulacion completada para {len(simulation_results)} escenarios")
        
        # 3. Crear directorio de gráficos
        charts_dir = Path("outputs/dashboards/drp_simulation")
        charts_dir.mkdir(parents=True, exist_ok=True)
        
        # 4. Generar gráficos
        print("Generando graficos...")
        
        # Gráfico 1: Comparación de escenarios
        print("  - Comparacion de escenarios...")
        fig1 = create_scenario_comparison_chart(comparison_df)
        fig1.savefig(charts_dir / "01_scenario_comparison.png", dpi=300, bbox_inches='tight')
        plt.close(fig1)
        
        # Gráfico 2: Radar de métricas
        print("  - Radar de metricas...")
        fig2 = create_metrics_radar_chart(comparison_df)
        fig2.savefig(charts_dir / "02_metrics_radar.png", dpi=300, bbox_inches='tight')
        plt.close(fig2)
        
        # Gráfico 3: Métricas detalladas
        print("  - Metricas detalladas...")
        fig3 = create_detailed_metrics_chart(comparison_df)
        fig3.savefig(charts_dir / "03_detailed_metrics.png", dpi=300, bbox_inches='tight')
        plt.close(fig3)
        
        # Gráfico 4: Tabla resumen
        print("  - Tabla resumen...")
        fig4 = create_scenario_summary_table(comparison_df)
        fig4.savefig(charts_dir / "04_summary_table.png", dpi=300, bbox_inches='tight')
        plt.close(fig4)
        
        # 5. Exportar datos de simulación
        print("Exportando datos de simulacion...")
        simulator.export_simulation_results(simulation_results)
        
        print("\n" + "="*70)
        print("GRAFICOS DRP SIMULATION GENERADOS EXITOSAMENTE")
        print("="*70)
        print("Archivos generados en: outputs/dashboards/drp_simulation/")
        print("  - 01_scenario_comparison.png")
        print("  - 02_metrics_radar.png") 
        print("  - 03_detailed_metrics.png")
        print("  - 04_summary_table.png")
        print(f"\nDatos de simulacion exportados en: outputs/simulation/")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Error generando graficos: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = generate_drp_simulation_charts()
    sys.exit(0 if success else 1)
