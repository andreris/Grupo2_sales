import streamlit as st
import pandas as pd
import io
import csv
from openpyxl import load_workbook
from streamlit_echarts import st_echarts

st.set_page_config(page_title="Publicaciones por año", layout="wide")

@st.cache_data
def load_data():
    wb = load_workbook("scopus_g2_ventas.xlsx", read_only=True)
    ws = wb.active
    lines = []
    for row in ws.iter_rows(values_only=True):
        cells = [str(c) for c in row if c is not None]
        if cells:
            lines.append(",".join(cells))
    csv_content = "\n".join(lines[1:])
    reader = csv.DictReader(io.StringIO(csv_content))
    rows = list(reader)
    df = pd.DataFrame(rows)
    df.columns = [c.strip('"').strip() for c in df.columns]
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
    df = df.dropna(subset=["Year"])
    df["Year"] = df["Year"].astype(int)
    return df

df = load_data()

st.page_link("pages/dashboard.py", label="⬅️ Volver al Dashboard Principal", icon="🏠")
st.title("📅 Análisis de Publicaciones por Año")
st.markdown("---")

col1, col2 = st.columns([2, 1])

with col1:
    pub_por_anio = df["Year"].value_counts().sort_index()
    years_list = [str(y) for y in pub_por_anio.index.tolist()]
    counts_list = pub_por_anio.values.tolist()
    bar_colors = ["#378ADD" if int(y) >= 2020 else "#185FA5" for y in years_list]

    option_anio = {
        "tooltip": {"trigger": "axis", "formatter": "{b}: {c} publicaciones"},
        "xAxis": {"type": "category", "data": years_list, "axisLabel": {"rotate": 45}},
        "yAxis": {"type": "value", "minInterval": 1},
        "series": [{
            "type": "bar",
            "data": [{"value": v, "itemStyle": {"color": c}} for v, c in zip(counts_list, bar_colors)],
            "itemStyle": {"borderRadius": [4, 4, 0, 0]},
            "label": {"show": True, "position": "top"}
        }],
        "grid": {"left": "5%", "right": "5%", "bottom": "15%", "containLabel": True}
    }
    st_echarts(option_anio, height="500px")

with col2:
    st.subheader("💡 Interpretación")
    st.write("""
    En este gráfico podemos observar la evolución temporal del interés científico en la predicción de ventas utilizando Inteligencia Artificial y Business Intelligence.
    
    **Puntos clave:**
    * **Tendencia:** Se evidencia un crecimiento significativo en los últimos años (barras claras), lo que demuestra que es un área de investigación en pleno auge.
    * **Adopción tecnológica:** El aumento reciente coincide con la democratización de los algoritmos de Machine Learning y la mayor disponibilidad de datos históricos de ventas en las empresas.
    """)