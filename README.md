# Supply Chain S&OP Planning Tool

## 📋 Descripción
Herramienta de Python para **Sales & Operations Planning (S&OP)** inspirada en el paquete `planr` de R. 

Este proyecto se enfoca en la **planificación operativa** de la cadena de suministro, complementando los pronósticos de demanda con:

- 📦 **Proyección de Inventarios** y coberturas
- 🔄 **Planes de Reposición** (DRP - Distribution Requirement Planning)  
- ⚖️ **Análisis de Demanda Restringida** por disponibilidad de stock
- 📅 **Conversión Temporal** (mensual ↔ semanal)
- ⏰ **Gestión de Productos de Vida Útil Corta**
- 🚛 **Inventarios en Tránsito**

## 🎯 Diferencias con el Proyecto de Forecasting

| **Proyecto ARIMAX** | **Proyecto S&OP** |
|---------------------|-------------------|
| 🔮 Predice demanda futura | 📊 Planifica operaciones actuales |
| 📈 Series temporales | 📋 Datos operativos |
| 🤖 Machine Learning | 🧮 Cálculos de inventario |
| 🔍 Análisis estadístico | 💼 Decisiones de negocio |

## 🏗️ Estructura del Proyecto

```
supply-chain-sop/
├── src/
│   ├── inventory/          # Proyección de inventarios
│   ├── replenishment/      # Planes de reposición (DRP)
│   ├── allocation/         # Demanda restringida y asignación
│   ├── temporal/           # Conversiones temporales
│   ├── ssl/               # Short Shelf Life management
│   └── utils/             # Utilidades comunes
├── data/
│   ├── sample_inventory.xlsx
│   ├── sample_demand.xlsx
│   └── sample_supply.xlsx
├── config/
│   └── sop_config.yaml
├── outputs/
│   ├── plans/
│   ├── reports/
│   └── dashboards/
├── tests/
├── requirements.txt
└── main_sop.py
```

## 🚀 Instalación

```bash
pip install -r requirements.txt
```

## 🎯 Ejecución

### 1. Ejecutar Análisis S&OP

```bash
python main_sop.py
```

### 2. Visualizar Dashboard Interactivo

```bash
python run_dashboard.py
```

O directamente con Streamlit:

```bash
streamlit run dashboard_sop.py
```

## 📊 Casos de Uso

1. **Planificador de Inventarios**: Calcula inventarios proyectados y coberturas
2. **Analista de Reposición**: Genera planes DRP optimizados
3. **Gerente de S&OP**: Análisis integral de restricciones de suministro
4. **Coordinador de Demanda**: Gestión de asignaciones y prioridades

## 🔗 Integración

Este proyecto se integra perfectamente con sistemas de forecasting (como nuestro proyecto ARIMAX) para convertir predicciones en planes ejecutables.
