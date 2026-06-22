"""
app.py
-------
Dashboard Interactivo - Hito 4 del TPI
Análisis de Puntualidad y Factores de Riesgo en Vuelos Domésticos (2024)

Este archivo se mantiene enfocado en la INTERFAZ, siguiendo la
recomendación arquitectónica del apunte teórico: la limpieza pesada de
datos vive en data_loader.py, y aquí solo se filtra, visualiza y se
muestra la información de forma clara para un usuario que no programa.
"""

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

from data_loader import cargar_datos

# --------------------------------------------------------------------------
# CONFIGURACIÓN GENERAL DE LA PÁGINA
# --------------------------------------------------------------------------
st.set_page_config(
    page_title="Dashboard de Puntualidad de Vuelos 2024",
    page_icon="✈️",
    layout="wide",
)

sns.set_theme(style="whitegrid")

# --------------------------------------------------------------------------
# CARGA DE DATOS (con manejo de errores)
# --------------------------------------------------------------------------
try:
    df, origen_datos = cargar_datos()
except Exception as e:
    st.error(
        "Ocurrió un error inesperado al cargar los datos. "
        "Verifique la conexión a la base o la presencia del archivo CSV de respaldo."
    )
    st.exception(e)
    st.stop()

if df.empty:
    st.warning("No hay datos disponibles para mostrar.")
    st.stop()

# --------------------------------------------------------------------------
# ENCABEZADO
# --------------------------------------------------------------------------
st.title("✈️ Dashboard de Puntualidad de Vuelos Domésticos (2024)")
st.markdown(
    "Informe de gestión interactivo para el análisis de demoras, "
    "cancelaciones y factores de riesgo operativo en vuelos comerciales."
)
st.caption(f"Fuente de datos activa: **{origen_datos}** &nbsp;|&nbsp; Registros totales: **{len(df):,}**")
st.divider()

# --------------------------------------------------------------------------
# SIDEBAR - FILTROS
# --------------------------------------------------------------------------
st.sidebar.header("🔎 Filtros")
st.sidebar.markdown("Ajustá los filtros para actualizar todo el dashboard en tiempo real.")

# Filtro 1: Aerolínea (equivalente a "comisión" en la consigna original)
aerolineas_disponibles = sorted(df["op_unique_carrier"].dropna().unique().tolist())
aerolineas_seleccionadas = st.sidebar.multiselect(
    "Aerolínea",
    options=aerolineas_disponibles,
    default=aerolineas_disponibles,
    help="Filtrá por una o más aerolíneas (código IATA del operador).",
)

# Filtro 2: Estado de origen (equivalente a "estado/situación" en la consigna)
estados_disponibles = sorted(df["origin_state_nm"].dropna().unique().tolist())
estados_seleccionados = st.sidebar.multiselect(
    "Estado de origen",
    options=estados_disponibles,
    default=[],
    help="Dejá vacío para incluir todos los estados, o seleccioná uno o más.",
)

# Filtro 3: Franja horaria de salida (equivalente a "fecha" en la consigna;
# se usa horario porque todos los vuelos del dataset son del mismo día)
franjas_disponibles = ["Madrugada (0-5hs)", "Mañana (5-12hs)", "Tarde (12-18hs)", "Noche (18-24hs)"]
franjas_presentes = [f for f in franjas_disponibles if f in df["franja_horaria"].unique()]
franjas_seleccionadas = st.sidebar.multiselect(
    "Franja horaria de salida",
    options=franjas_presentes,
    default=franjas_presentes,
)

st.sidebar.divider()
solo_retrasados = st.sidebar.checkbox(
    "Mostrar solo vuelos con retraso significativo (>15 min)",
    value=False,
)

st.sidebar.divider()
st.sidebar.caption(
    "💡 Un vuelo se considera con **retraso significativo** cuando llega "
    "más de 15 minutos después de lo programado (estándar de la industria)."
)

# --------------------------------------------------------------------------
# APLICACIÓN DE FILTROS
# --------------------------------------------------------------------------
df_filtrado = df.copy()

try:
    if aerolineas_seleccionadas:
        df_filtrado = df_filtrado[df_filtrado["op_unique_carrier"].isin(aerolineas_seleccionadas)]
    if estados_seleccionados:
        df_filtrado = df_filtrado[df_filtrado["origin_state_nm"].isin(estados_seleccionados)]
    if franjas_seleccionadas:
        df_filtrado = df_filtrado[df_filtrado["franja_horaria"].isin(franjas_seleccionadas)]
    if solo_retrasados:
        df_filtrado = df_filtrado[df_filtrado["retraso_significativo"] == True]
except Exception as e:
    st.error("Ocurrió un error al aplicar los filtros seleccionados.")
    st.exception(e)
    st.stop()

if df_filtrado.empty:
    st.warning(
        "⚠️ No hay vuelos que coincidan con la combinación de filtros seleccionada. "
        "Probá ampliar los criterios en la barra lateral."
    )
    st.stop()

# --------------------------------------------------------------------------
# KPIs PRINCIPALES
# --------------------------------------------------------------------------
st.subheader("📊 Indicadores Clave (KPIs)")

col1, col2, col3, col4 = st.columns(4)

total_vuelos = len(df_filtrado)
demora_promedio = df_filtrado["arr_delay"].mean()
pct_retrasados = (df_filtrado["retraso_significativo"].mean()) * 100
pct_cancelados = (df_filtrado["cancelled"].mean()) * 100

col1.metric("Vuelos analizados", f"{total_vuelos:,}")
col2.metric(
    "Demora promedio de llegada",
    f"{demora_promedio:,.1f} min",
    help="Negativo significa que, en promedio, los vuelos llegan antes de lo programado.",
)
col3.metric("% con retraso significativo (>15 min)", f"{pct_retrasados:.1f}%")
col4.metric("% de vuelos cancelados", f"{pct_cancelados:.1f}%")

st.divider()

# --------------------------------------------------------------------------
# GRÁFICOS (mínimo 4, profesionales, con título/leyenda/análisis)
# --------------------------------------------------------------------------
st.subheader("📈 Visualizaciones y Análisis")

fila1_col1, fila1_col2 = st.columns(2)

# Gráfico 1: Demora promedio por aerolínea
with fila1_col1:
    st.markdown("**Demora promedio de llegada por aerolínea**")
    try:
        datos_g1 = (
            df_filtrado.groupby("op_unique_carrier")["arr_delay"]
            .mean()
            .sort_values(ascending=False)
        )
        fig1, ax1 = plt.subplots(figsize=(6, 4))
        colores = ["#d62728" if v > 0 else "#2ca02c" for v in datos_g1.values]
        ax1.bar(datos_g1.index, datos_g1.values, color=colores)
        ax1.axhline(0, color="black", linewidth=0.8)
        ax1.set_xlabel("Aerolínea")
        ax1.set_ylabel("Demora promedio (minutos)")
        ax1.set_title("Demora promedio de llegada por aerolínea")
        plt.tight_layout()
        st.pyplot(fig1)
        plt.close(fig1)

        peor = datos_g1.index[0]
        mejor = datos_g1.index[-1]
        st.caption(
            f"📌 **Lectura del gráfico:** {peor} presenta la mayor demora promedio "
            f"({datos_g1.iloc[0]:.1f} min), mientras que {mejor} es la más puntual "
            f"({datos_g1.iloc[-1]:.1f} min, llegando en promedio antes de lo previsto)."
        )
    except Exception as e:
        st.error("No se pudo generar este gráfico con los filtros actuales.")

# Gráfico 2: % de vuelos retrasados por franja horaria
with fila1_col2:
    st.markdown("**% de vuelos con retraso significativo por franja horaria**")
    try:
        datos_g2 = (
            df_filtrado.groupby("franja_horaria")["retraso_significativo"]
            .mean()
            .mul(100)
            .reindex(franjas_disponibles)
            .dropna()
        )
        fig2, ax2 = plt.subplots(figsize=(6, 4))
        ax2.bar(datos_g2.index, datos_g2.values, color="#ff7f0e")
        ax2.set_xlabel("Franja horaria de salida")
        ax2.set_ylabel("% de vuelos con retraso > 15 min")
        ax2.set_title("Retrasos significativos por franja horaria")
        ax2.tick_params(axis="x", rotation=15)
        plt.tight_layout()
        st.pyplot(fig2)
        plt.close(fig2)

        peor_franja = datos_g2.idxmax()
        st.caption(
            f"📌 **Lectura del gráfico:** la franja **{peor_franja}** concentra la mayor "
            f"proporción de retrasos ({datos_g2.max():.1f}%), lo que sugiere congestión "
            "operativa en ese horario."
        )
    except Exception as e:
        st.error("No se pudo generar este gráfico con los filtros actuales.")

fila2_col1, fila2_col2 = st.columns(2)

# Gráfico 3: Distribución de causas de demora
with fila2_col1:
    st.markdown("**Distribución de causas principales de demora**")
    try:
        datos_g3 = (
            df_filtrado[df_filtrado["causa_principal_demora"] != "Sin demora atribuible"]
            ["causa_principal_demora"]
            .value_counts()
        )
        if datos_g3.empty:
            st.info("No hay vuelos con demoras atribuibles en la selección actual.")
        else:
            fig3, ax3 = plt.subplots(figsize=(6, 4))
            sns.barplot(
                x=datos_g3.values, y=datos_g3.index, hue=datos_g3.index,
                ax=ax3, palette="rocket", legend=False,
            )
            ax3.set_xlabel("Cantidad de vuelos")
            ax3.set_ylabel("Causa principal")
            ax3.set_title("¿Qué causa más demoras?")
            plt.tight_layout()
            st.pyplot(fig3)
            plt.close(fig3)

            causa_top = datos_g3.idxmax()
            st.caption(
                f"📌 **Lectura del gráfico:** la causa más frecuente de demora es "
                f"**{causa_top}**, presente en {datos_g3.max()} vuelos de la selección."
            )
    except Exception as e:
        st.error("No se pudo generar este gráfico con los filtros actuales.")

# Gráfico 4: Relación entre distancia y demora (dispersión)
with fila2_col2:
    st.markdown("**Relación entre distancia del vuelo y demora de llegada**")
    try:
        muestra = df_filtrado.dropna(subset=["distance", "arr_delay"])
        fig4, ax4 = plt.subplots(figsize=(6, 4))
        sns.scatterplot(
            data=muestra,
            x="distance",
            y="arr_delay",
            alpha=0.4,
            ax=ax4,
            color="#1f77b4",
        )
        ax4.axhline(15, color="red", linestyle="--", linewidth=1, label="Umbral de retraso (15 min)")
        ax4.set_xlabel("Distancia del vuelo (millas)")
        ax4.set_ylabel("Demora de llegada (minutos)")
        ax4.set_title("Distancia vs. Demora de llegada")
        ax4.legend()
        plt.tight_layout()
        st.pyplot(fig4)
        plt.close(fig4)

        corr = muestra["distance"].corr(muestra["arr_delay"])
        st.caption(
            f"📌 **Lectura del gráfico:** la correlación entre distancia y demora es "
            f"de {corr:.2f}, lo que indica una relación "
            f"{'prácticamente nula' if abs(corr) < 0.1 else 'débil' if abs(corr) < 0.3 else 'moderada'} "
            "entre la longitud del vuelo y el tiempo de retraso."
        )
    except Exception as e:
        st.error("No se pudo generar este gráfico con los filtros actuales.")

st.divider()

# --------------------------------------------------------------------------
# TABLA DE DETALLE (para auditoría de registros)
# --------------------------------------------------------------------------
st.subheader("🔍 Detalle de Vuelos")
st.markdown("Tabla con el detalle de cada vuelo según los filtros aplicados (ordenable y navegable).")

columnas_a_mostrar = [
    "fl_date", "op_unique_carrier", "origin", "dest",
    "crs_dep_time", "dep_delay", "arr_delay",
    "cancelled", "causa_principal_demora",
]
columnas_presentes = [c for c in columnas_a_mostrar if c in df_filtrado.columns]

st.dataframe(
    df_filtrado[columnas_presentes].sort_values("arr_delay", ascending=False),
    width="stretch",
    height=350,
)

st.caption(
    f"Mostrando {len(df_filtrado):,} de {len(df):,} registros totales según los filtros aplicados."
)