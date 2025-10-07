#!/usr/bin/env python3
"""
Dashboard Interactivo de Optimización S&OP
Visualización limpia de comparación Original vs Optimizado
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path

# Configuración de página
st.set_page_config(
    page_title="Optimización S&OP - Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2c3e50;
        text-align: center;
        padding: 1rem 0;
        border-bottom: 3px solid #3498db;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #ecf0f1;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #3498db;
    }
    .improvement {
        color: #27ae60;
        font-weight: bold;
    }
    .warning {
        color: #e74c3c;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    """Cargar datos de optimización."""
    try:
        plan = pd.read_csv("outputs/plans/sop_balanced_plan.csv")
        summary = pd.read_csv("outputs/reports/optimization_summary.csv")
        
        plan['Period'] = pd.to_datetime(plan['Period'])
        
        return plan, summary
    except FileNotFoundError:
        st.error("⚠️ Archivos no encontrados. Ejecuta primero: python run_balanced_optimization.py")
        st.stop()


def main():
    """Dashboard principal."""
    
    # Header
    st.markdown('<div class="main-header">📊 OPTIMIZACIÓN S&OP - PLAN BALANCEADO</div>', 
                unsafe_allow_html=True)
    
    st.markdown("""
    <div style='background-color: #d5f4e6; padding: 1rem; border-radius: 5px; margin-bottom: 2rem;'>
        <strong>🎯 Objetivo:</strong> Eliminar quiebres de stock manteniendo inventario balanceado usando política ROP
        <br><strong>📐 Política:</strong> ROP = (Demanda Promedio Semanal × Lead Time / 7) + Safety Stock
    </div>
    """, unsafe_allow_html=True)
    
    # Cargar datos
    plan, summary = load_data()
    
    # ========================================================================
    # SECCIÓN 1: MÉTRICAS GLOBALES
    # ========================================================================
    st.markdown("---")
    st.header("📈 Métricas Globales de Mejora")
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_stockouts_before = summary['Stockouts_Original'].sum()
    total_stockouts_after = summary['Stockouts_Optimized'].sum()
    stockout_reduction = total_stockouts_before - total_stockouts_after
    
    total_below_before = summary['Below_Safety_Original'].sum()
    total_below_after = summary['Below_Safety_Optimized'].sum()
    safety_improvement = total_below_before - total_below_after
    
    total_orders = summary['Orders_Generated'].sum()
    
    avg_inv_before = summary['Avg_Inventory_Original'].mean()
    avg_inv_after = summary['Avg_Inventory_Optimized'].mean()
    inv_change_pct = ((avg_inv_after - avg_inv_before) / avg_inv_before) * 100
    
    with col1:
        st.metric(
            label="Stockouts Eliminados",
            value=f"{int(stockout_reduction)}",
            delta=f"{int(total_stockouts_after)} restantes",
            delta_color="inverse"
        )
    
    with col2:
        st.metric(
            label="Mejora Safety Stock",
            value=f"{int(safety_improvement)}",
            delta=f"-{int(safety_improvement)} períodos"
        )
    
    with col3:
        st.metric(
            label="Órdenes Generadas",
            value=f"{int(total_orders)}",
            delta="Nuevas órdenes"
        )
    
    with col4:
        st.metric(
            label="Cambio Inv. Promedio",
            value=f"{inv_change_pct:+.1f}%",
            delta=f"{avg_inv_after:.0f} unidades"
        )
    
    # ========================================================================
    # SECCIÓN 2: COMPARACIÓN POR SKU
    # ========================================================================
    st.markdown("---")
    st.header("🔍 Análisis por SKU")
    
    # Selector de SKU
    selected_sku = st.selectbox(
        "Seleccionar SKU para análisis detallado:",
        options=plan['SKU'].unique(),
        index=0
    )
    
    sku_plan = plan[plan['SKU'] == selected_sku].sort_values('Period')
    sku_summary = summary[summary['SKU'] == selected_sku].iloc[0]
    
    # Métricas del SKU
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Stockouts**")
        st.write(f"Original: {int(sku_summary['Stockouts_Original'])}")
        st.write(f"Optimizado: {int(sku_summary['Stockouts_Optimized'])}")
        reduction = int(sku_summary['Stockout_Reduction'])
        if reduction > 0:
            st.markdown(f"<span class='improvement'>✅ Mejora: {reduction}</span>", 
                       unsafe_allow_html=True)
    
    with col2:
        st.markdown("**Inventario Promedio**")
        st.write(f"Original: {sku_summary['Avg_Inventory_Original']:.0f}")
        st.write(f"Optimizado: {sku_summary['Avg_Inventory_Optimized']:.0f}")
    
    with col3:
        st.markdown("**Órdenes Generadas**")
        st.write(f"Total: {int(sku_summary['Orders_Generated'])}")
        st.write(f"Supply Total: {sku_summary['Total_Supply_Optimized']:.0f}")
    
    # ========================================================================
    # SECCIÓN 3: GRÁFICO DE PROYECCIÓN DE INVENTARIO
    # ========================================================================
    st.markdown("---")
    st.subheader(f"📊 Proyección de Inventario - {selected_sku}")
    
    fig = go.Figure()
    
    # Línea Original
    fig.add_trace(go.Scatter(
        x=sku_plan['Period'],
        y=sku_plan['Projected_Inventory_Original'],
        mode='lines+markers',
        name='Original',
        line=dict(color='#e74c3c', width=2),
        marker=dict(size=6)
    ))
    
    # Línea Optimizada
    fig.add_trace(go.Scatter(
        x=sku_plan['Period'],
        y=sku_plan['Projected_Inventory_Optimized'],
        mode='lines+markers',
        name='Optimizado',
        line=dict(color='#27ae60', width=2),
        marker=dict(size=6, symbol='square')
    ))
    
    # Línea Safety Stock
    fig.add_trace(go.Scatter(
        x=sku_plan['Period'],
        y=sku_plan['Safety_Stock'],
        mode='lines',
        name='Safety Stock',
        line=dict(color='orange', width=2, dash='dash')
    ))
    
    # Línea Max Stock
    fig.add_trace(go.Scatter(
        x=sku_plan['Period'],
        y=sku_plan['Max_Stock'],
        mode='lines',
        name='Max Stock',
        line=dict(color='blue', width=2, dash='dash')
    ))
    
    # Línea ROP
    fig.add_trace(go.Scatter(
        x=sku_plan['Period'],
        y=sku_plan['ROP'],
        mode='lines',
        name='ROP (Reorder Point)',
        line=dict(color='purple', width=2, dash='dot')
    ))
    
    # Línea cero
    fig.add_hline(y=0, line_dash="solid", line_color="red", opacity=0.5)
    
    fig.update_layout(
        title=f"Inventario Proyectado - {selected_sku}",
        xaxis_title="Período",
        yaxis_title="Inventario",
        hovermode='x unified',
        height=500,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # ========================================================================
    # SECCIÓN 4: TABLA DE ÓRDENES GENERADAS
    # ========================================================================
    st.markdown("---")
    st.subheader(f"📦 Órdenes de Reposición Generadas - {selected_sku}")
    
    orders_generated = sku_plan[sku_plan['Order_Generated'] == True][
        ['Period', 'Projected_Inventory_Original', 'Supply_Optimized', 
         'Order_Reason', 'Projected_Inventory_Optimized']
    ].copy()
    
    if len(orders_generated) > 0:
        orders_generated.columns = [
            'Período', 'Inv. Proyectado Original', 'Cantidad Ordenada',
            'Razón de Orden', 'Inv. Resultante'
        ]
        
        st.dataframe(
            orders_generated.style.format({
                'Inv. Proyectado Original': '{:.0f}',
                'Cantidad Ordenada': '{:.0f}',
                'Inv. Resultante': '{:.0f}'
            }),
            use_container_width=True
        )
    else:
        st.info("✅ No se generaron órdenes para este SKU (inventario suficiente)")
    
    # ========================================================================
    # SECCIÓN 5: COMPARACIÓN TODOS LOS SKUs
    # ========================================================================
    st.markdown("---")
    st.header("📊 Comparación Global - Todos los SKUs")
    
    tab1, tab2 = st.tabs(["Gráfico de Stockouts", "Tabla Resumen"])
    
    with tab1:
        fig_comparison = go.Figure()
        
        fig_comparison.add_trace(go.Bar(
            x=summary['SKU'],
            y=summary['Stockouts_Original'],
            name='Original',
            marker_color='#e74c3c'
        ))
        
        fig_comparison.add_trace(go.Bar(
            x=summary['SKU'],
            y=summary['Stockouts_Optimized'],
            name='Optimizado',
            marker_color='#27ae60'
        ))
        
        fig_comparison.update_layout(
            title="Comparación de Stockouts por SKU",
            xaxis_title="SKU",
            yaxis_title="Períodos con Stockout",
            barmode='group',
            height=500
        )
        
        st.plotly_chart(fig_comparison, use_container_width=True)
    
    with tab2:
        display_summary = summary[[
            'SKU', 'Stockouts_Original', 'Stockouts_Optimized', 
            'Stockout_Reduction', 'Orders_Generated',
            'Avg_Inventory_Original', 'Avg_Inventory_Optimized'
        ]].copy()
        
        display_summary.columns = [
            'SKU', 'Stockouts Original', 'Stockouts Optimizado',
            'Reducción', 'Órdenes', 'Inv. Prom. Original', 'Inv. Prom. Optimizado'
        ]
        
        st.dataframe(
            display_summary.style.format({
                'Inv. Prom. Original': '{:.0f}',
                'Inv. Prom. Optimizado': '{:.0f}'
            }).background_gradient(
                subset=['Reducción'],
                cmap='Greens'
            ),
            use_container_width=True
        )
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #7f8c8d; padding: 1rem;'>
        📊 Dashboard de Optimización S&OP | Política ROP Balanceada
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
