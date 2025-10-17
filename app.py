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


# Ruta del archivo
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

# ==== SIDEBAR ====
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
