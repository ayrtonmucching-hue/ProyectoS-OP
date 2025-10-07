#!/usr/bin/env python3
"""
DRP Simulation Dashboard - Interactive Web Interface
Run with: streamlit run drp_simulation_dashboard.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
import sys

# Configuración de la página
st.set_page_config(
    page_title="DRP Simulation Dashboard",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Agregar src al path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from utils.config_loader import load_config
from simulation.drp_simulator import DRPSimulator

@st.cache_data
def load_base_data():
    """Cargar datos base para simulación."""
    try:
        # Cargar datos reales
        inventory_df = pd.read_excel("data/inventory_template.xlsx")
        demand_df = pd.read_excel("data/demand_template.xlsx")
        supply_df = pd.read_excel("data/supply_template.xlsx")
        
        # Convertir fechas
        demand_df['Period'] = pd.to_datetime(demand_df['Period'])
        supply_df['Period'] = pd.to_datetime(supply_df['Period'])
        
        return inventory_df, demand_df, supply_df
    except Exception as e:
        st.error(f"Error cargando datos base: {e}")
        return None, None, None

@st.cache_data
def load_simulation_params():
    """Cargar parámetros de simulación."""
    try:
        sku_params = pd.read_excel("data/drp_simulation_params.xlsx", sheet_name='SKU_Parameters')
        scenarios = pd.read_excel("data/drp_simulation_params.xlsx", sheet_name='Scenarios')
        return sku_params, scenarios
    except Exception as e:
        st.error(f"Error cargando parámetros de simulación: {e}")
        return None, None

def create_scenario_comparison_chart(comparison_df):
    """Crear gráfico de comparación de escenarios."""
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Nivel de Servicio (%)', 'Total de Órdenes', 
                       'Stock de Seguridad Total', 'Períodos con Stockout'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    scenarios = comparison_df['scenario_name'].tolist()
    colors = px.colors.qualitative.Set3[:len(scenarios)]
    
    # Nivel de servicio
    fig.add_trace(
        go.Bar(x=scenarios, y=comparison_df['avg_service_level'], 
               name='Nivel Servicio', marker_color=colors[0]),
        row=1, col=1
    )
    
    # Total órdenes
    fig.add_trace(
        go.Bar(x=scenarios, y=comparison_df['total_orders'], 
               name='Total Órdenes', marker_color=colors[1]),
        row=1, col=2
    )
    
    # Stock de seguridad
    fig.add_trace(
        go.Bar(x=scenarios, y=comparison_df['total_safety_stock'], 
               name='Safety Stock', marker_color=colors[2]),
        row=2, col=1
    )
    
    # Stockouts
    fig.add_trace(
        go.Bar(x=scenarios, y=comparison_df['stockout_periods'], 
               name='Stockouts', marker_color=colors[3]),
        row=2, col=2
    )
    
    fig.update_layout(height=600, showlegend=False, title_text="Comparación de Escenarios DRP")
    return fig

def create_metrics_radar_chart(comparison_df):
    """Crear gráfico radar de métricas."""
    
    # Normalizar métricas para el radar (0-100)
    metrics_normalized = comparison_df.copy()
    
    # Normalizar cada métrica
    metrics_to_normalize = ['avg_service_level', 'fill_rate']
    for metric in metrics_to_normalize:
        if metric in metrics_normalized.columns:
            max_val = metrics_normalized[metric].max()
            if max_val > 0:
                metrics_normalized[f'{metric}_norm'] = (metrics_normalized[metric] / max_val) * 100
    
    # Invertir métricas donde menor es mejor
    inverse_metrics = ['stockout_periods', 'avg_lead_time']
    for metric in inverse_metrics:
        if metric in metrics_normalized.columns:
            max_val = metrics_normalized[metric].max()
            if max_val > 0:
                metrics_normalized[f'{metric}_norm'] = 100 - ((metrics_normalized[metric] / max_val) * 100)
    
    fig = go.Figure()
    
    categories = ['Nivel Servicio', 'Fill Rate', 'Bajo Stockout', 'Lead Time Corto']
    
    for idx, row in metrics_normalized.iterrows():
        values = [
            row.get('avg_service_level_norm', row.get('avg_service_level', 0)),
            row.get('fill_rate_norm', row.get('fill_rate', 0)),
            row.get('stockout_periods_norm', 50),
            row.get('avg_lead_time_norm', 50)
        ]
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name=row['scenario_name']
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )),
        showlegend=True,
        title="Radar de Performance por Escenario"
    )
    
    return fig

def main():
    """Función principal del dashboard."""
    
    st.title("🎯 DRP Simulation Dashboard")
    st.markdown("Simulación interactiva de escenarios DRP con diferentes parámetros")
    
    # Sidebar para controles
    st.sidebar.header("Configuración de Simulación")
    
    # Cargar datos base
    with st.spinner("Cargando datos base..."):
        inventory_df, demand_df, supply_df = load_base_data()
        sku_params, scenarios_df = load_simulation_params()
    
    if inventory_df is None or sku_params is None:
        st.error("No se pudieron cargar los datos necesarios. Asegúrate de que existan los archivos de datos.")
        return
    
    # Mostrar información de datos cargados
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("SKUs", len(inventory_df))
    with col2:
        st.metric("Períodos de Demanda", len(demand_df))
    with col3:
        st.metric("Escenarios Disponibles", len(scenarios_df))
    
    # Selección de escenarios
    st.sidebar.subheader("Seleccionar Escenarios")
    available_scenarios = scenarios_df['Scenario_Name'].tolist()
    selected_scenarios = st.sidebar.multiselect(
        "Escenarios a simular:",
        available_scenarios,
        default=available_scenarios[:2]  # Seleccionar los primeros 2 por defecto
    )
    
    if not selected_scenarios:
        st.warning("Selecciona al menos un escenario para simular.")
        return
    
    # Botón para ejecutar simulación
    if st.sidebar.button("🚀 Ejecutar Simulación", type="primary"):
        
        try:
            # Cargar configuración
            config = load_config("config/sop_config.yaml")
            
            # Inicializar simulador
            simulator = DRPSimulator(config)
            
            # Ejecutar simulación
            with st.spinner(f"Ejecutando simulación para {len(selected_scenarios)} escenarios..."):
                simulation_results = simulator.run_multiple_scenarios(
                    inventory_df, demand_df, supply_df, selected_scenarios
                )
            
            # Guardar resultados en session state
            st.session_state.simulation_results = simulation_results
            st.session_state.comparison_df = simulator.compare_scenarios(simulation_results)
            
            st.success(f"✅ Simulación completada para {len(simulation_results)} escenarios")
            
        except Exception as e:
            st.error(f"Error durante la simulación: {e}")
            return
    
    # Mostrar resultados si existen
    if 'simulation_results' in st.session_state:
        
        st.header("📊 Resultados de Simulación")
        
        # Tabs para diferentes vistas
        tab1, tab2, tab3, tab4 = st.tabs(["Comparación", "Métricas Detalladas", "Análisis Radar", "Datos por Escenario"])
        
        with tab1:
            st.subheader("Comparación de Escenarios")
            
            # Mostrar tabla de comparación
            comparison_df = st.session_state.comparison_df
            st.dataframe(comparison_df.round(2), use_container_width=True)
            
            # Gráfico de comparación
            comparison_chart = create_scenario_comparison_chart(comparison_df)
            st.plotly_chart(comparison_chart, use_container_width=True)
        
        with tab2:
            st.subheader("Métricas Detalladas por Escenario")
            
            for scenario_name, result in st.session_state.simulation_results.items():
                with st.expander(f"📋 {scenario_name} - {result['scenario_description']}"):
                    
                    metrics = result['metrics']
                    
                    # Mostrar métricas en columnas
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Nivel de Servicio", f"{metrics['avg_service_level']:.1f}%")
                        st.metric("Total Órdenes", f"{metrics['total_orders']:,}")
                    
                    with col2:
                        st.metric("Cantidad Total", f"{metrics['total_order_quantity']:,}")
                        st.metric("Tamaño Promedio Orden", f"{metrics['avg_order_size']:.0f}")
                    
                    with col3:
                        st.metric("Períodos Stockout", f"{metrics['stockout_periods']:,}")
                        st.metric("Lead Time Promedio", f"{metrics['avg_lead_time']:.1f} días")
                    
                    with col4:
                        st.metric("Fill Rate", f"{metrics['fill_rate']:.1f}%")
                        st.metric("Safety Stock Total", f"{metrics['total_safety_stock']:,}")
        
        with tab3:
            st.subheader("Análisis Radar de Performance")
            
            radar_chart = create_metrics_radar_chart(comparison_df)
            st.plotly_chart(radar_chart, use_container_width=True)
            
            st.info("El gráfico radar muestra la performance relativa de cada escenario. Valores más altos indican mejor performance.")
        
        with tab4:
            st.subheader("Datos Detallados por Escenario")
            
            selected_scenario = st.selectbox(
                "Seleccionar escenario para ver detalles:",
                list(st.session_state.simulation_results.keys())
            )
            
            if selected_scenario:
                result = st.session_state.simulation_results[selected_scenario]
                
                # Mostrar inventario del escenario
                st.write("**Parámetros de Inventario del Escenario:**")
                st.dataframe(result['scenario_inventory'], use_container_width=True)
                
                # Mostrar algunos resultados DRP
                st.write("**Ejemplo de Resultados DRP (primeros 3 SKUs):**")
                for i, (sku, drp_df) in enumerate(list(result['drp_results'].items())[:3]):
                    st.write(f"**{sku}:**")
                    st.dataframe(drp_df.head(10), use_container_width=True)
        
        # Botón para exportar resultados
        if st.button("💾 Exportar Resultados"):
            try:
                simulator = DRPSimulator(load_config("config/sop_config.yaml"))
                output_path = simulator.export_simulation_results(st.session_state.simulation_results)
                st.success(f"✅ Resultados exportados en: {output_path}")
            except Exception as e:
                st.error(f"Error exportando resultados: {e}")
    
    else:
        st.info("👆 Selecciona escenarios y ejecuta la simulación para ver resultados.")
        
        # Mostrar información de escenarios disponibles
        st.subheader("📋 Escenarios Disponibles")
        for _, scenario in scenarios_df.iterrows():
            with st.expander(f"🎯 {scenario['Scenario_Name']}"):
                st.write(f"**Descripción:** {scenario['Description']}")
                st.write(f"**Multiplicador Safety Stock:** {scenario['Safety_Stock_Multiplier']}")
                st.write(f"**Multiplicador Frecuencia:** {scenario['Supply_Frequency_Multiplier']}")
                st.write(f"**Nivel Servicio Objetivo:** {scenario['Service_Level_Target']}%")

if __name__ == "__main__":
    main()
