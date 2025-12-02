"""Main Streamlit application."""

import streamlit as st

st.set_page_config(
    page_title="Spotify Data Analytics",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🎵 Spotify Data Analytics")
st.markdown("### Análisis de tus datos de Spotify desde BigQuery")

st.sidebar.title("Navegación")
st.sidebar.markdown("""
Usa el menú lateral para navegar entre las diferentes secciones:
- **Dashboard**: Vista general de tus datos
- **Tracks**: Análisis detallado de canciones
- **Artists**: Análisis de artistas
- **Trends**: Tendencias temporales
""")

st.markdown("""
## Bienvenido a tu Dashboard de Spotify

Este dashboard te permite explorar y analizar tus datos de Spotify que han sido 
extraídos y cargados en BigQuery.

### Características:
- 📊 **Dashboard General**: Métricas y estadísticas generales
- 🎵 **Análisis de Tracks**: Explora tus canciones favoritas y sus características
- 🎤 **Análisis de Artistas**: Descubre tus artistas más escuchados
- 📈 **Tendencias**: Observa cómo cambian tus gustos musicales con el tiempo

### Cómo usar:
1. Navega por las diferentes páginas usando el menú lateral
2. Explora los gráficos interactivos
3. Filtra y analiza tus datos según tus intereses

---
*Datos actualizados desde BigQuery*
""")

