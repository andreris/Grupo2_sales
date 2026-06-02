import streamlit as st
import pandas as pd
import io
import csv
from openpyxl import load_workbook
from streamlit_echarts import st_echarts

st.set_page_config(page_title="Top Citados", layout="wide")

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
    df["Cited by"] = pd.to_numeric(df["Cited by"], errors="coerce").fillna(0)
    return df

df = load_data()

st.page_link("pages/dashboard.py", label="⬅️ Volver al Dashboard Principal", icon="🏠")
st.title("🏆 Top 10 Artículos Más Citados")
st.markdown("---")

col1, col2 = st.columns([2, 1])

with col1:
    top_citados = df.nlargest(10, "Cited by")[["Title", "Cited by"]].copy()
    top_citados["Titulo corto"] = top_citados["Title"].str.strip('"').str[:60] + "…"
    top_citados = top_citados.sort_values("Cited by", ascending=True)

    option_citas = {
        "tooltip": {"trigger": "axis", "formatter": "{b}: {c} citas"},
        "xAxis": {"type": "value"},
        "yAxis": {"type": "category", "data": top_citados["Titulo corto"].tolist(), "axisLabel": {"width": 300, "overflow": "truncate"}},
        "series": [{
            "type": "bar",
            "data": top_citados["Cited by"].astype(int).tolist(),
            "itemStyle": {"color": "#533AB7", "borderRadius": [0, 4, 4, 0]},
            "label": {"show": True, "position": "right"}
        }],
        "grid": {"left": "2%", "right": "10%", "bottom": "5%", "containLabel": True}
    }
    st_echarts(option_citas, height="600px")

with col2:
    st.subheader("💡 Interpretación")
    st.write("""
    Este gráfico muestra los 10 artículos con mayor cantidad de citas dentro del dataset de Scopus. Su objetivo es identificar las investigaciones con mayor impacto relacionadas con la predicción de ventas mediante inteligencia artificial, inteligencia de negocios y minería de datos.
    
    **Puntos clave/Insights:**
    * **Fundamentos del campo:** Los artículos en la parte superior representan la literatura base. Las metodologías presentadas en estos papers (ya sean redes neuronales, series temporales o minería de datos) son probablemente el estándar de la industria.
    * **Relevancia:** Un alto número de citas valida la efectividad de las técnicas de Machine Learning y BI propuestas por estos autores para la predicción de ventas.
    """)