#!/usr/bin/env python3
"""
S&OP Dashboard - Interactive Web Interface
Run with: streamlit run dashboard_sop.py
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
    page_title="S&OP Planning Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Agregar src al path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from utils.config_loader import load_config

def load_results_data():
    """Cargar todos los archivos de resultados."""
    try:
        # Cargar análisis ABC
        abc_df = pd.read_csv("outputs/reports/abc_analysis.csv")
        
        # Cargar resumen de riesgos
        risk_df = pd.read_csv("outputs/reports/risk_summary.csv", index_col=0)
        
        # Cargar métricas DRP
        drp_metrics = pd.read_csv("outputs/reports/drp_metrics.csv")
        
        # Cargar resumen de órdenes
        try:
            orders_df = pd.read_csv("outputs/plans/order_summary.csv")
        except:
            orders_df = pd.DataFrame()
        
        # Cargar proyecciones por SKU
        projections = {}
        for sku_file in Path("outputs/reports").glob("projection_*.csv"):
            sku = sku_file.stem.replace("projection_", "")
            projections[sku] = pd.read_csv(sku_file)
            projections[sku]['Period'] = pd.to_datetime(projections[sku]['Period'])
        
        # Cargar planes DRP por SKU
        drp_plans = {}
        for drp_file in Path("outputs/plans").glob("drp_plan_*.csv"):
            sku = drp_file.stem.replace("drp_plan_", "")
            drp_plans[sku] = pd.read_csv(drp_file)
            drp_plans[sku]['Period'] = pd.to_datetime(drp_plans[sku]['Period'])
        
        return abc_df, risk_df, drp_metrics, orders_df, projections, drp_plans
        
    except Exception as e:
        st.error(f"Error cargando datos: {e}")
        return None, None, None, None, {}, {}

def create_abc_chart(abc_df):
    """Crear gráfico de análisis ABC."""
    fig = px.bar(
        abc_df, 
        x='SKU', 
        y='Total_Demand',
        color='ABC_Class',
        title="Análisis ABC - Clasificación por Demanda",
        color_discrete_map={'A': '#FF6B6B', 'B': '#4ECDC4', 'C': '#45B7D1'}
    )
    fig.update_layout(height=400)
    return fig

def create_inventory_projection_chart(projections, selected_sku):
    """Crear gráfico de proyección de inventarios."""
    if selected_sku not in projections:
        return None
    
    df = projections[selected_sku]
    
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Inventario Proyectado', 'Cobertura en Días'),
        vertical_spacing=0.1
    )
    
    # Gráfico de inventario
    fig.add_trace(
        go.Scatter(
            x=df['Period'], 
            y=df['Projected_Inventory'],
            mode='lines+markers',
            name='Inventario Proyectado',
            line=dict(color='#1f77b4', width=3)
        ),
        row=1, col=1
    )
    
    # Línea de safety stock
    if 'Safety_Stock' in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df['Period'], 
                y=df['Safety_Stock'],
                mode='lines',
                name='Safety Stock',
                line=dict(color='red', dash='dash')
            ),
            row=1, col=1
        )
    
    # Gráfico de cobertura
    fig.add_trace(
        go.Scatter(
            x=df['Period'], 
            y=df['Coverage_Days'],
            mode='lines+markers',
            name='Cobertura (días)',
            line=dict(color='green', width=2)
        ),
        row=2, col=1
    )
    
    fig.update_layout(height=600, title=f"Proyección de Inventario - {selected_sku}")
    return fig

def create_drp_chart(drp_plans, selected_sku):
    """Crear gráfico del plan DRP."""
    if selected_sku not in drp_plans:
        return None
    
    df = drp_plans[selected_sku]
    
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Plan de Inventario y Órdenes', 'Nivel de Servicio'),
        vertical_spacing=0.1
    )
    
    # Inventario final
    fig.add_trace(
        go.Scatter(
            x=df['Period'], 
            y=df['Final_Inventory'],
            mode='lines+markers',
            name='Inventario Final',
            line=dict(color='blue', width=3)
        ),
        row=1, col=1
    )
    
    # Órdenes
    orders = df[df['Order_Needed']]
    if not orders.empty:
        fig.add_trace(
            go.Bar(
                x=orders['Period'], 
                y=orders['Order_Quantity'],
                name='Órdenes Planificadas',
                marker_color='orange',
                opacity=0.7
            ),
            row=1, col=1
        )
    
    # Nivel de servicio
    fig.add_trace(
        go.Scatter(
            x=df['Period'], 
            y=df['Service_Level'],
            mode='lines+markers',
            name='Nivel de Servicio (%)',
            line=dict(color='green', width=2)
        ),
        row=2, col=1
    )
    
    fig.update_layout(height=600, title=f"Plan DRP - {selected_sku}")
    return fig

def create_orders_timeline(orders_df):
    """Crear timeline de órdenes."""
    if orders_df.empty:
        return None
    
    orders_df['Order_Period'] = pd.to_datetime(orders_df['Order_Period'])
    
    fig = px.scatter(
        orders_df, 
        x='Order_Period', 
        y='SKU',
        size='Order_Quantity',
        color='Reason',
        title="Timeline de Órdenes Planificadas",
        hover_data=['Order_Quantity']
    )
    fig.update_layout(height=400)
    return fig

def main():
    """Función principal del dashboard."""
    
    # Título principal
    st.title("📊 S&OP Planning Dashboard")
    st.markdown("---")
    
    # Cargar datos
    with st.spinner("Cargando datos..."):
        abc_df, risk_df, drp_metrics, orders_df, projections, drp_plans = load_results_data()
    
    if abc_df is None:
        st.error("No se pudieron cargar los datos. Ejecuta primero 'python main_sop.py'")
        return
    
    # Sidebar con controles
    st.sidebar.header("🎛️ Controles")
    
    # Selector de SKU
    available_skus = list(projections.keys())
    selected_sku = st.sidebar.selectbox("Seleccionar SKU:", available_skus)
    
    # Métricas principales
    st.header("📈 Métricas Principales")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "SKUs Gestionados", 
            drp_metrics['total_skus'].iloc[0],
            help="Número total de SKUs en el análisis"
        )
    
    with col2:
        st.metric(
            "Órdenes Planificadas", 
            int(drp_metrics['total_orders'].iloc[0]),
            help="Número total de órdenes requeridas"
        )
    
    with col3:
        st.metric(
            "Nivel de Servicio", 
            f"{drp_metrics['avg_service_level'].iloc[0]:.1f}%",
            help="Nivel de servicio promedio"
        )
    
    with col4:
        st.metric(
            "Cobertura Promedio", 
            f"{drp_metrics['avg_coverage_days'].iloc[0]:.1f} días",
            help="Cobertura promedio en días"
        )
    
    # Tabs principales
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Análisis ABC", "📦 Proyecciones", "🔄 Plan DRP", "📅 Órdenes", "⚠️ Riesgos"])
    
    with tab1:
        st.header("Análisis ABC")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig_abc = create_abc_chart(abc_df)
            st.plotly_chart(fig_abc, use_container_width=True)
        
        with col2:
            st.subheader("Clasificación")
            st.dataframe(abc_df, use_container_width=True)
    
    with tab2:
        st.header(f"Proyección de Inventarios - {selected_sku}")
        
        fig_proj = create_inventory_projection_chart(projections, selected_sku)
        if fig_proj:
            st.plotly_chart(fig_proj, use_container_width=True)
            
            # Tabla de datos
            st.subheader("Datos Detallados")
            proj_data = projections[selected_sku]
            st.dataframe(proj_data, use_container_width=True)
    
    with tab3:
        st.header(f"Plan DRP - {selected_sku}")
        
        fig_drp = create_drp_chart(drp_plans, selected_sku)
        if fig_drp:
            st.plotly_chart(fig_drp, use_container_width=True)
            
            # Resumen de órdenes para este SKU
            if not orders_df.empty:
                sku_orders = orders_df[orders_df['SKU'] == selected_sku]
                if not sku_orders.empty:
                    st.subheader("Órdenes Planificadas")
                    st.dataframe(sku_orders, use_container_width=True)
    
    with tab4:
        st.header("Timeline de Órdenes")
        
        if not orders_df.empty:
            fig_orders = create_orders_timeline(orders_df)
            if fig_orders:
                st.plotly_chart(fig_orders, use_container_width=True)
            
            st.subheader("Resumen de Órdenes")
            st.dataframe(orders_df, use_container_width=True)
        else:
            st.info("No hay órdenes planificadas en este período.")
    
    with tab5:
        st.header("Análisis de Riesgos")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Riesgos por SKU")
            st.dataframe(risk_df, use_container_width=True)
        
        with col2:
            st.subheader("Resumen de Riesgos")
            total_stockouts = risk_df['stockouts'].sum()
            total_low_coverage = risk_df['low_coverage'].sum()
            total_below_safety = risk_df['below_safety'].sum()
            
            st.metric("Total Stockouts", total_stockouts)
            st.metric("Períodos Cobertura Baja", total_low_coverage)
            st.metric("Períodos Bajo Safety Stock", total_below_safety)
    
    # Footer
    st.markdown("---")
    st.markdown("💡 **S&OP Planning Tool** - Desarrollado con Python y Streamlit")

if __name__ == "__main__":
    main()
