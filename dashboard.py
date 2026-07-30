import streamlit as st
import httpx
import pandas as pd
import json
import os

st.set_page_config(page_title="PricePulse AI", page_icon="", layout="wide")

API_URL = os.getenv("API_URL", "http://localhost:8000")


def cargar_historial() -> list:
    try:
        resp = httpx.get(f"{API_URL}/historial", timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        st.error(f"Error al conectar con la API: {e}")
        return []


def formatear_precio(p) -> str:
    try:
        return f"${float(p):,.2f}"
    except (ValueError, TypeError):
        return str(p)


st.title("PricePulse AI")
st.markdown("Sistema de monitoreo de precios e-commerce con IA generativa")

data = cargar_historial()

if not data:
    st.warning("No hay datos en el historial. Ejecuta primero el flujo de n8n o haz un POST a /analizar-precios.")
    st.stop()

filas = []
for analisis in data:
    fecha = analisis.get("fecha", "")
    producto = analisis.get("producto", "N/A")
    for p in analisis.get("precios", []):
        filas.append({
            "Fecha": fecha,
            "Producto": producto,
            "Plataforma": p.get("plataforma", "N/A"),
            "Titulo": p.get("titulo", ""),
            "Precio": p.get("precio", 0),
            "Link": p.get("link", ""),
        })

df = pd.DataFrame(filas)
if df.empty:
    st.warning("No hay precios registrados.")
    st.stop()

df["Precio"] = pd.to_numeric(df["Precio"], errors="coerce")
df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
df = df.sort_values("Fecha", ascending=False)

st.sidebar.header("Filtros")

productos = df["Producto"].unique().tolist()
producto_sel = st.sidebar.selectbox("Producto", ["Todos"] + productos)
if producto_sel != "Todos":
    df = df[df["Producto"] == producto_sel]

plataformas = df["Plataforma"].unique().tolist()
plat_sel = st.sidebar.multiselect("Plataforma", plataformas, default=plataformas)
df = df[df["Plataforma"].isin(plat_sel)]

if df["Fecha"].notna().any():
    fecha_min = df["Fecha"].min().date()
    fecha_max = df["Fecha"].max().date()
    rango = st.sidebar.date_input("Rango", [fecha_min, fecha_max])
    if len(rango) == 2:
        df = df[(df["Fecha"].dt.date >= rango[0]) & (df["Fecha"].dt.date <= rango[1])]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Precios registrados", len(df))
col2.metric("Productos", df["Producto"].nunique())
col3.metric("Plataformas", df["Plataforma"].nunique())
ultima = df["Fecha"].max()
col4.metric("Ultimo registro", ultima.strftime("%d/%m/%Y %H:%M") if pd.notna(ultima) else "N/A")

st.markdown("---")
st.subheader("Precio promedio por plataforma")
promedios = df.groupby("Plataforma")["Precio"].mean().reset_index()
if not promedios.empty:
    st.bar_chart(promedios.set_index("Plataforma"))

st.markdown("---")
st.subheader("Precios historicos")
historico = df[["Fecha", "Plataforma", "Precio"]].dropna()
if not historico.empty:
    precios_ts = historico.groupby(["Fecha", "Plataforma"])["Precio"].mean().unstack()
    precios_ts.index.name = None
    precios_ts.columns = [c.replace(".", "_").replace(" ", "_").replace("-", "_") for c in precios_ts.columns]
    if not precios_ts.empty:
        try:
            st.line_chart(precios_ts)
        except Exception:
            st.caption("Grafico historico no disponible para esta version")

st.markdown("---")
st.subheader("Detalle de precios")
df_display = df.copy()
df_display["Precio"] = df_display["Precio"].apply(lambda x: formatear_precio(x) if pd.notna(x) else "N/A")
st.table(df_display)
