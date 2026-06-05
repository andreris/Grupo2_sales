import streamlit as st
import pandas as pd
import io
import csv
from openpyxl import load_workbook
from streamlit_echarts import st_echarts

st.set_page_config(
    page_title="Dashboard Scopus - Predicción de Ventas",
    page_icon="📊",
    layout="wide"
)

st.markdown("""
<style>
    .metric-card {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 1rem 1.25rem;
        text-align: center;
    }
    .metric-label {
        font-size: 13px;
        color: #666;
        margin-bottom: 4px;
    }
    .metric-value {
        font-size: 26px;
        font-weight: 600;
        color: #1a1a2e;
    }
    .section-title {
        font-size: 15px;
        color: #444;
        font-weight: 500;
        margin-bottom: 0.5rem;
    }
    .year-badge {
        display: inline-block;
        background: #378ADD;
        color: white;
        border-radius: 20px;
        padding: 2px 12px;
        font-size: 13px;
        font-weight: 600;
        margin-left: 8px;
        vertical-align: middle;
    }
</style>
""", unsafe_allow_html=True)


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
    df["Cited by"] = pd.to_numeric(df["Cited by"], errors="coerce").fillna(0)
    df = df.dropna(subset=["Year"])
    df["Year"] = df["Year"].astype(int)
    return df


df = load_data()

# ── Inicializar session_state para año seleccionado por clic ──────────────────
if "selected_year" not in st.session_state:
    st.session_state.selected_year = None

st.title("📊 Análisis bibliométrico — Predicción de ventas con IA")
st.caption("Dataset exportado desde Scopus · Keywords: sales forecasting, artificial intelligence, business intelligence, data mining")

st.markdown("---")

year_min = int(df["Year"].min())
year_max = int(df["Year"].max())

# ── Slider y botón de limpieza ────────────────────────────────────────────────
col_filter, col_clear, _ = st.columns([2, 1, 2])

with col_filter:
    # Si hay un año seleccionado por clic, el slider refleja ese año puntual
    if st.session_state.selected_year is not None:
        sy = st.session_state.selected_year
        year_range = st.slider(
            "Filtrar por rango de años",
            min_value=year_min,
            max_value=year_max,
            value=(sy, sy),
            step=1,
            key="slider_years"
        )
    else:
        year_range = st.slider(
            "Filtrar por rango de años",
            min_value=year_min,
            max_value=year_max,
            value=(year_min, year_max),
            step=1,
            key="slider_years"
        )

with col_clear:
    if st.session_state.selected_year is not None:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("✖ Limpiar año", use_container_width=True):
            st.session_state.selected_year = None
            st.rerun()

# Si el usuario mueve el slider manualmente, desactivar el año seleccionado por clic
if st.session_state.selected_year is not None:
    sy = st.session_state.selected_year
    if year_range != (sy, sy):
        st.session_state.selected_year = None

df_filtered = df[(df["Year"] >= year_range[0]) & (df["Year"] <= year_range[1])]

st.markdown("---")

m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Artículos filtrados</div>
        <div class="metric-value">{len(df_filtered)}</div>
    </div>""", unsafe_allow_html=True)
with m2:
    rango_label = str(year_range[0]) if year_range[0] == year_range[1] else f"{year_range[0]}–{year_range[1]}"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Rango de años</div>
        <div class="metric-value">{rango_label}</div>
    </div>""", unsafe_allow_html=True)
with m3:
    peak_year = df_filtered["Year"].value_counts().idxmax() if len(df_filtered) > 0 else "—"
    peak_count = df_filtered["Year"].value_counts().max() if len(df_filtered) > 0 else 0
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Año pico</div>
        <div class="metric-value">{peak_year} ({peak_count})</div>
    </div>""", unsafe_allow_html=True)
with m4:
    max_cites = int(df_filtered["Cited by"].max()) if len(df_filtered) > 0 else 0
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Máx. citas</div>
        <div class="metric-value">{max_cites}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    # Título con badge de año activo
    if st.session_state.selected_year is not None:
        st.markdown(
            f'<p class="section-title">Publicaciones por año'
            f'<span class="year-badge">📌 {st.session_state.selected_year} — haz clic fuera para quitar</span></p>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<p class="section-title">Publicaciones por año '
            '<span style="font-size:11px;color:#999;">(haz clic en una barra para filtrar ese año)</span></p>',
            unsafe_allow_html=True
        )

    # Siempre mostramos TODAS las barras del rango completo del slider
    # pero resaltamos el año seleccionado si existe
    pub_por_anio_full = df[(df["Year"] >= year_min) & (df["Year"] <= year_max)]["Year"].value_counts().sort_index()
    years_list_full = [str(y) for y in pub_por_anio_full.index.tolist()]
    counts_list_full = pub_por_anio_full.values.tolist()

    selected_y = st.session_state.selected_year

    def bar_color(y, selected):
        y_int = int(y)
        if selected is not None:
            if y_int == selected:
                return "#FF5F00"   # resaltado: naranja vivo
            else:
                return "#9BB8D4"   # resto: gris azulado apagado
        else:
            return "#378ADD" if y_int >= 2020 else "#185FA5"

    bar_data = [
        {
            "value": v,
            "itemStyle": {
                "color": bar_color(y, selected_y),
                "opacity": 1 if (selected_y is None or int(y) == selected_y) else 0.45
            }
        }
        for y, v in zip(years_list_full, counts_list_full)
    ]

    option_anio = {
        "animation": True,
        "animationDuration": 600,
        "animationEasing": "cubicOut",
        "tooltip": {
            "trigger": "axis",
            "formatter": "{b}: {c} publicaciones"
        },
        "xAxis": {
            "type": "category",
            "data": years_list_full,
            "axisLabel": {"rotate": 45, "fontSize": 11}
        },
        "yAxis": {
            "type": "value",
            "minInterval": 1,
            "axisLabel": {"fontSize": 11}
        },
        "series": [{
            "type": "bar",
            "data": bar_data,
            "barMaxWidth": 40,
            "itemStyle": {"borderRadius": [4, 4, 0, 0]},
            "label": {
                "show": True,
                "position": "top",
                "fontSize": 11,
                "color": "#444"
            },
            "emphasis": {
                "itemStyle": {
                    "color": "#FF5F00",
                    "opacity": 1
                }
            },
            "cursor": "pointer"
        }],
        "grid": {"left": "5%", "right": "5%", "bottom": "15%", "containLabel": True}
    }

    # Capturar clic en barra → guarda el año; clic en zona vacía → limpia
    clicked = st_echarts(
        option_anio,
        height="300px",
        key="chart_anio",
        events={
            "click": "function(params) { return params.name; }",
            "globalout": "function() { return '__reset__'; }"
        }
    )

    if clicked is not None:
        if clicked == "__reset__":
            if st.session_state.selected_year is not None:
                st.session_state.selected_year = None
                st.rerun()
        else:
            try:
                year_clicked = int(clicked)
                if st.session_state.selected_year != year_clicked:
                    st.session_state.selected_year = year_clicked
                    st.rerun()
            except (ValueError, TypeError):
                pass

    st.page_link("pages/publicaciones_anio.py", label="Ver más", icon="🔍")

with col2:
    st.markdown('<p class="section-title">Distribución por tipo de documento</p>', unsafe_allow_html=True)
    tipo_counts = df_filtered["Document Type"].value_counts()
    tipo_data = [{"value": int(v), "name": k} for k, v in tipo_counts.items()]

    option_tipo = {
        "animation": True,
        "animationDuration": 800,
        "animationEasing": "cubicOut",
        "tooltip": {
            "trigger": "item",
            "formatter": "{b}: {c} ({d}%)"
        },
        "color": ["#1D9E75", "#378ADD", "#D85A30", "#BA7517", "#533AB7"],
        "legend": {
            "orient": "vertical",
            "right": "5%",
            "top": "center",
            "textStyle": {"fontSize": 11}
        },
        "series": [{
            "type": "pie",
            "radius": ["40%", "70%"],
            "center": ["40%", "50%"],
            "data": tipo_data,
            "label": {
                "show": True,
                "formatter": "{d}%",
                "fontSize": 11
            },
            "emphasis": {
                "itemStyle": {
                    "shadowBlur": 6,
                    "shadowColor": "rgba(0,0,0,0.2)"
                }
            }
        }]
    }
    st_echarts(option_tipo, height="300px", key="chart_tipo")
    st.page_link("pages/tipos_documento.py", label="Ver más", icon="🔍")

st.markdown("<br>", unsafe_allow_html=True)

col3, col4 = st.columns(2)

with col3:
    st.markdown('<p class="section-title">Top 10 artículos más citados</p>', unsafe_allow_html=True)
    top_citados = (
        df_filtered.nlargest(10, "Cited by")[["Title", "Cited by", "Year"]]
        .copy()
    )
    top_citados["Titulo corto"] = top_citados["Title"].str.strip('"').str[:55] + "…"
    top_citados = top_citados.sort_values("Cited by", ascending=True)

    option_citas = {
        "animation": True,
        "animationDuration": 900,
        "animationEasing": "cubicOut",
        "tooltip": {
            "trigger": "axis",
            "formatter": "{b}: {c} citas"
        },
        "xAxis": {
            "type": "value",
            "axisLabel": {"fontSize": 11}
        },
        "yAxis": {
            "type": "category",
            "data": top_citados["Titulo corto"].tolist(),
            "axisLabel": {"fontSize": 10, "width": 200, "overflow": "truncate"}
        },
        "series": [{
            "type": "bar",
            "data": top_citados["Cited by"].astype(int).tolist(),
            "itemStyle": {"color": "#533AB7", "borderRadius": [0, 4, 4, 0]},
            "barMaxWidth": 30,
            "label": {
                "show": True,
                "position": "right",
                "fontSize": 11,
                "color": "#444"
            }
        }],
        "grid": {"left": "2%", "right": "10%", "bottom": "5%", "containLabel": True}
    }
    st_echarts(option_citas, height="340px", key="chart_citas")
    st.page_link("pages/top_citados.py", label="Ver más", icon="🔍")

with col4:
    st.markdown('<p class="section-title">Fuentes científicas más frecuentes</p>', unsafe_allow_html=True)
    top_fuentes = df_filtered["Source title"].value_counts().head(10)
    fuentes_labels = [str(f)[:50] + "…" if len(str(f)) > 50 else str(f) for f in top_fuentes.index]
    fuentes_vals = top_fuentes.values.tolist()

    fuente_data = list(zip(fuentes_labels[::-1], fuentes_vals[::-1]))

    option_fuentes = {
        "animation": True,
        "animationDuration": 900,
        "animationEasing": "cubicOut",
        "tooltip": {
            "trigger": "axis",
            "formatter": "{b}: {c} publicaciones"
        },
        "xAxis": {
            "type": "value",
            "minInterval": 1,
            "axisLabel": {"fontSize": 11}
        },
        "yAxis": {
            "type": "category",
            "data": [f[0] for f in fuente_data],
            "axisLabel": {"fontSize": 10, "width": 200, "overflow": "truncate"}
        },
        "series": [{
            "type": "bar",
            "data": [f[1] for f in fuente_data],
            "itemStyle": {"color": "#0F6E56", "borderRadius": [0, 4, 4, 0]},
            "barMaxWidth": 30,
            "label": {
                "show": True,
                "position": "right",
                "fontSize": 11,
                "color": "#444"
            }
        }],
        "grid": {"left": "2%", "right": "10%", "bottom": "5%", "containLabel": True}
    }
    st_echarts(option_fuentes, height="340px", key="chart_fuentes")
    st.page_link("pages/fuentes.py", label="Ver más", icon="🔍")

st.markdown("---")

col_inf1, col_inf2 = st.columns([2, 1])

with col_inf1:
    st.caption("Grupo 2 · Evaluación Machine Learning · Scopus dataset · Pregunta de investigación: ¿Cómo contribuyen la IA, BI y minería de datos a la predicción de ventas?")

with col_inf2:
    st.markdown('<p style="font-size: 15px; font-weight: 600; color: #666; margin-bottom: 8px;">Archivos</p>', unsafe_allow_html=True)
    st.link_button(
        label="Repository GitHub",
        url="https://github.com/andreris/Grupo2_sales",
        icon="🐈"
    )