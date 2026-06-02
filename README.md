# Dashboard Scopus — Predicción de Ventas con IA

Dashboard interactivo con Streamlit + ECharts para analizar artículos científicos exportados desde Scopus.

## Requisitos

- Python 3.9+
- El archivo `scopus_g2_ventas.xlsx` debe estar en la misma carpeta que `app.py`

## Instalación

```bash
pip install -r requirements.txt
```

## Ejecutar

```bash
streamlit run app.py
```

Se abrirá automáticamente en el navegador en `http://localhost:8501`

## Gráficos incluidos

- **Publicaciones por año** — barras con color diferenciado antes/después de 2020
- **Distribución por tipo de documento** — dona interactiva
- **Top 10 artículos más citados** — barras horizontales
- **Fuentes científicas más frecuentes** — barras horizontales

## Filtro

El slider de años en la parte superior filtra todos los gráficos a la vez.
