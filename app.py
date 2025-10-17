# -*- coding: utf-8 -*-
import os
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Vehículos US - Dashboard", layout="wide")


@st.cache_data
def load_data(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    df['date_posted'] = pd.to_datetime(df['date_posted'], errors='coerce')
    df['posting_year'] = df['date_posted'].dt.year
    for col in ['model_year', 'cylinders', 'odometer', 'is_4wd']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    return df


# Ruta/Path del archivo
CSV_NAME = "vehicles_us.csv"
csv_path = CSV_NAME if os.path.exists(CSV_NAME) else os.path.join(
    os.path.dirname(__file__), CSV_NAME)

if not os.path.exists(csv_path):
    st.error(f"No se encontró {CSV_NAME}. Coloca el CSV junto a app.py.")
    st.stop()

df = load_data(csv_path)

# ===== Encabezado =====
st.title("🚗 Análisis de Anuncios de Vehículos (US)")
st.markdown("Explora los precios, kilometrajes, años y publicaciones por tipo de vehículo usando gráficos interactivos con **Plotly Express**.")

# ==== BARRA LATERAL ====
st.sidebar.header("Filtros")
fuel_sel = st.sidebar.multiselect(
    "Combustible", sorted(df['fuel'].dropna().unique().tolist()))
trans_sel = st.sidebar.multiselect("Transmisión", sorted(
    df['transmission'].dropna().unique().tolist()))
type_sel = st.sidebar.multiselect(
    "Tipo de vehículo", sorted(df['type'].dropna().unique().tolist()))
cond_sel = st.sidebar.multiselect("Condición", sorted(
    df['condition'].dropna().unique().tolist()))
year_min, year_max = int(np.nanmin(df['model_year'])), int(
    np.nanmax(df['model_year']))
year_rng = st.sidebar.slider(
    "Año del modelo", min_value=year_min, max_value=year_max, value=(year_min, year_max))

df_f = df.copy()
if fuel_sel:
    df_f = df_f[df_f['fuel'].isin(fuel_sel)]
if trans_sel:
    df_f = df_f[df_f['transmission'].isin(trans_sel)]
if type_sel:
    df_f = df_f[df_f['type'].isin(type_sel)]
if cond_sel:
    df_f = df_f[df_f['condition'].isin(cond_sel)]
df_f = df_f[(df_f['model_year'].fillna(year_min) >= year_rng[0]) &
            (df_f['model_year'].fillna(year_max) <= year_rng[1])]

# ==== KPIs ====
st.markdown("### 📊 Resumen General")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Publicaciones", f"{len(df_f):,}")
col2.metric("Precio Promedio (USD)", f"${np.nanmedian(df_f['price']):,.0f}")
col3.metric("Odómetro Promedio (mi)", f"{np.nanmedian(df_f['odometer']):,.0f}")
col4.metric("Año Promedio",
            f"{int(np.nanmedian(df_f['model_year'])) if not np.isnan(np.nanmedian(df_f['model_year'])) else 'NA'}")

st.divider()

# ==== 1️⃣ Histograma ====
st.subheader("Distribución de precios")
fig_hist = px.histogram(
    df_f, x="price", nbins=50,
    title="Distribución de precios de vehículos",
    labels={"price": "Precio (USD)"},
    color_discrete_sequence=["#636EFA"]
)
st.plotly_chart(fig_hist, use_container_width=True)

# ==== 2️⃣ Dispersión ====
st.subheader("Relación entre Precio y Odómetro")
mostrar_tendencia = st.checkbox("Mostrar línea de tendencia")

fig_scatter = px.scatter(
    df_f, x="odometer", y="price",
    color="type",
    title="Precio vs. Odómetro por tipo de vehículo",
    labels={"odometer": "Odómetro (millas)",
            "price": "Precio (USD)", "type": "Tipo"},
    hover_data=["model", "model_year", "condition"]
)

if mostrar_tendencia:
    fig_scatter.add_traces(px.scatter(
        df_f, x="odometer", y="price", trendline="ols").data[1])

st.plotly_chart(fig_scatter, use_container_width=True)

# ==== 3️⃣ Publicaciones por año ====
st.subheader("Número de publicaciones por año")
year_counts = df_f.dropna(subset=['posting_year']).groupby(
    'posting_year').size().reset_index(name='Publicaciones')

fig_years = px.bar(
    year_counts, x="posting_year", y="Publicaciones",
    title="Publicaciones por año",
    labels={"posting_year": "Año de publicación"},
    color_discrete_sequence=["#EF553B"]
)
st.plotly_chart(fig_years, use_container_width=True)

st.info("Usa los filtros de la barra lateral y activa la casilla para ver la tendencia en el gráfico de dispersión.")
