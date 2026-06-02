import streamlit as st
import pandas as pd
import io
import csv
from openpyxl import load_workbook
from streamlit_echarts import st_echarts

st.set_page_config(page_title="Fuentes Científicas", layout="wide")

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
    return df

df = load_data()

st.page_link("pages/dashboard.py", label="⬅️ Volver al Dashboard Principal", icon="🏠")
st.title("🏛️ Fuentes científicas más frecuentes")
st.markdown("---")

col1, col2 = st.columns([2, 1])

with col1:
    top_fuentes = df["Source title"].value_counts().head(10)
    fuentes_labels = [str(f)[:60] + "…" if len(str(f)) > 60 else str(f) for f in top_fuentes.index]
    fuentes_vals = top_fuentes.values.tolist()
    fuente_data = list(zip(fuentes_labels[::-1], fuentes_vals[::-1]))

    option_fuentes = {
        "tooltip": {"trigger": "axis", "formatter": "{b}: {c} publicaciones"},
        "xAxis": {"type": "value", "minInterval": 1},
        "yAxis": {"type": "category", "data": [f[0] for f in fuente_data], "axisLabel": {"width": 300, "overflow": "truncate"}},
        "series": [{
            "type": "bar",
            "data": [f[1] for f in fuente_data],
            "itemStyle": {"color": "#0F6E56", "borderRadius": [0, 4, 4, 0]},
            "label": {"show": True, "position": "right"}
        }],
        "grid": {"left": "2%", "right": "10%", "bottom": "5%", "containLabel": True}
    }
    st_echarts(option_fuentes, height="600px")

with col2:
    st.subheader("💡 Interpretación")
    st.write("""
    Esta gráfica lista las revistas (Journals) y conferencias que más publican sobre la intersección entre ventas e inteligencia artificial.
    
    **Puntos clave:**
    * **Enfoque de las revistas:** Nos permite ver si la investigación se publica más en revistas de informática/tecnología (enfocadas en el algoritmo) o en revistas de negocios/management (enfocadas en la estrategia y toma de decisiones).
    * **Vigilancia Tecnológica:** Para futuros estudios de predicción de ventas, estas son las principales fuentes bibliográficas que se deben consultar para mantenerse actualizado.
    """)