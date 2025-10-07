#!/usr/bin/env python3
"""
Generador de plantilla Excel para DRP Simulation Dashboard
"""

import pandas as pd
import numpy as np
from pathlib import Path

def create_drp_simulation_template():
    """Crear plantilla Excel para parámetros de simulación DRP."""
    
    print("Creando plantilla DRP Simulation...")
    
    # Usar los mismos SKUs que ya tienes
    skus = [f"SKU{i:03d}" for i in range(1, 19)]  # SKU001 a SKU018
    
    # Crear datos de parámetros de simulación
    simulation_params = []
    
    for sku in skus:
        # Generar rangos realistas para simulación
        base_safety = np.random.randint(20, 100)
        base_frequency = np.random.choice([7, 14, 21, 28])  # Weekly, Bi-weekly, etc.
        
        params = {
            'SKU': sku,
            'Safety_Stock_Min': base_safety,
            'Safety_Stock_Max': base_safety * 2,
            'Supply_Frequency_Min': max(1, base_frequency - 7),
            'Supply_Frequency_Max': base_frequency + 14,
            'Frozen_Horizon_Weeks': np.random.choice([1, 2, 3, 4]),
            'MOQ_Min': np.random.randint(50, 200),
            'MOQ_Max': np.random.randint(200, 500),
            'Lead_Time_Min': np.random.randint(1, 7),
            'Lead_Time_Max': np.random.randint(7, 21),
            'Service_Level_Target': np.random.choice([90, 95, 98, 99])
        }
        simulation_params.append(params)
    
    simulation_df = pd.DataFrame(simulation_params)
    
    # Crear escenarios predefinidos
    scenarios = [
        {
            'Scenario_Name': 'Conservative',
            'Safety_Stock_Multiplier': 1.5,
            'Supply_Frequency_Multiplier': 0.8,
            'Service_Level_Target': 98,
            'Description': 'Escenario conservador con más stock de seguridad'
        },
        {
            'Scenario_Name': 'Aggressive',
            'Safety_Stock_Multiplier': 0.7,
            'Supply_Frequency_Multiplier': 1.2,
            'Service_Level_Target': 92,
            'Description': 'Escenario agresivo para reducir inventarios'
        },
        {
            'Scenario_Name': 'Balanced',
            'Safety_Stock_Multiplier': 1.0,
            'Supply_Frequency_Multiplier': 1.0,
            'Service_Level_Target': 95,
            'Description': 'Escenario balanceado estándar'
        },
        {
            'Scenario_Name': 'High_Service',
            'Safety_Stock_Multiplier': 2.0,
            'Supply_Frequency_Multiplier': 0.6,
            'Service_Level_Target': 99,
            'Description': 'Máximo nivel de servicio'
        }
    ]
    
    scenarios_df = pd.DataFrame(scenarios)
    
    # Crear archivo Excel con múltiples hojas
    output_path = Path("data/drp_simulation_params.xlsx")
    
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        # Hoja 1: Parámetros por SKU
        simulation_df.to_excel(writer, sheet_name='SKU_Parameters', index=False)
        
        # Hoja 2: Escenarios predefinidos
        scenarios_df.to_excel(writer, sheet_name='Scenarios', index=False)
        
        # Hoja 3: Instrucciones
        instructions = pd.DataFrame([
            {'Campo': 'SKU', 'Descripción': 'Código del producto'},
            {'Campo': 'Safety_Stock_Min', 'Descripción': 'Stock de seguridad mínimo para simulación'},
            {'Campo': 'Safety_Stock_Max', 'Descripción': 'Stock de seguridad máximo para simulación'},
            {'Campo': 'Supply_Frequency_Min', 'Descripción': 'Frecuencia mínima de suministro (días)'},
            {'Campo': 'Supply_Frequency_Max', 'Descripción': 'Frecuencia máxima de suministro (días)'},
            {'Campo': 'Frozen_Horizon_Weeks', 'Descripción': 'Horizonte congelado en semanas'},
            {'Campo': 'MOQ_Min', 'Descripción': 'Cantidad mínima de orden - mínimo'},
            {'Campo': 'MOQ_Max', 'Descripción': 'Cantidad mínima de orden - máximo'},
            {'Campo': 'Lead_Time_Min', 'Descripción': 'Tiempo de entrega mínimo (días)'},
            {'Campo': 'Lead_Time_Max', 'Descripción': 'Tiempo de entrega máximo (días)'},
            {'Campo': 'Service_Level_Target', 'Descripción': 'Nivel de servicio objetivo (%)'}
        ])
        instructions.to_excel(writer, sheet_name='Instructions', index=False)
    
    print(f"[OK] Plantilla creada: {output_path}")
    print(f"   - {len(simulation_df)} SKUs con parametros de simulacion")
    print(f"   - {len(scenarios_df)} escenarios predefinidos")
    print("   - Hoja de instrucciones incluida")
    
    return output_path

if __name__ == "__main__":
    create_drp_simulation_template()
