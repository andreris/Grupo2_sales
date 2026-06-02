import streamlit as st

# 1. Configuración global de la aplicación
st.set_page_config(
    page_title="Dashboard Scopus - Predicción de Ventas",
    page_icon="📊",
    layout="wide"
)

# 2. Definir cada página con su nombre en Mayúscula y su Icono personalizado
inicio_page = st.Page("pages/dashboard.py", title="Inicio / Dashboard", icon="🏠", default=True)
fuentes_page = st.Page("pages/fuentes.py", title="Fuentes Científicas", icon="🏛️")
anio_page = st.Page("pages/publicaciones_anio.py", title="Publicaciones por Año", icon="📈")
tipo_page = st.Page("pages/tipos_documento.py", title="Tipos de Documento", icon="📊")
citados_page = st.Page("pages/top_citados.py", title="Top 10 Más Citados", icon="🏆")

# 3. Inicializar la navegación estructurada
pg = st.navigation([inicio_page, fuentes_page, anio_page, tipo_page, citados_page])

# 4. Diseñar los elementos personalizados debajo de los botones de la barra lateral
with st.sidebar:
    st.markdown("---")  # Línea divisoria elegante
    st.markdown('<p style="font-size: 15px; font-weight: 600; color: #666; margin-bottom: 8px;">Fuente:</p>', unsafe_allow_html=True)
    st.link_button(
        label="Repository GitHub", 
        url="https://github.com/andreris/Grupo2_sales", 
        icon="🐈"
    )

# 5. Ejecutar la página seleccionada
pg.run()