import streamlit as st
import pandas as pd
import sqlite3
import mysql.connector
import plotly.express as px # Para gráficos interactivos
from database_manager import DatabaseManager

# Configuración de la página
st.set_page_config(page_title="Sopnet Network Monitor", layout="wide")

def get_data_from_db():
    """Conecta a SQLite de forma segura y trae las alertas."""
    db_path = 'sopnet_monitoring.db'
    try:
        # El uso de 'with' asegura que la conexión se cierre sola
        with sqlite3.connect(db_path) as conn:
            query = "SELECT * FROM network_alerts ORDER BY timestamp DESC"
            df = pd.read_sql(query, conn)
        return df
    except Exception as e:
        # Si el archivo no existe aún, mostramos un mensaje amigable
        st.info("Esperando datos de red... Asegúrate de haber ejecutado main.py")
        return pd.DataFrame()

# TÍTULO E INDICADORES
st.title("🌐 Centro de Monitoreo - Sopnet SRL")
st.markdown("### Estado de Salud de la Infraestructura en Tiempo Real")

data = get_data_from_db()

if not data.empty:
    # FILTROS LATERALES
    st.sidebar.header("Filtros de Red")
    severity_filter = st.sidebar.multiselect(
        "Filtrar por Severidad:",
        options=data["severity"].unique(),
        default=data["severity"].unique()
    )
    
    filtered_data = data[data["severity"].isin(severity_filter)]

    # MÉTRICAS RÁPIDAS (KPIs)
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Alertas", len(filtered_data))
    col2.metric("Alertas Críticas", len(filtered_data[filtered_data["severity"] == "Critical"]))
    col3.metric("Latencia Media (ms)", round(filtered_data["latency_ms"].mean(), 2))

    # GRÁFICOS INTERACTIVOS
    st.markdown("---")
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Histórico de Latencia")
        fig_lat = px.line(filtered_data, x="timestamp", y="latency_ms", 
                          color="severity", title="Latencia por Evento")
        st.plotly_chart(fig_lat, use_container_width=True)

    with c2:
        st.subheader("Distribución de Severidad")
        fig_pie = px.pie(filtered_data, names="severity", hole=0.4,
                         color_discrete_map={'Critical':'red', 'Medium':'orange', 'Low':'blue'})
        st.plotly_chart(fig_pie, use_container_width=True)

    # TABLA DE DATOS CRUDOS
    st.subheader("Registro de Incidencias (Logs)")
    st.dataframe(filtered_data.style.highlight_max(axis=0, subset=['latency_ms'], color='lightcoral'), 
                 use_container_width=True)

else:
    st.warning("No se encontraron datos en la base de datos. Ejecutá main.py para generar alertas.")