"""Análisis de artistas."""

import sys
from pathlib import Path

import plotly.express as px
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from streamlit_app.utils.queries import BigQueryQueries

st.set_page_config(page_title="Artists", page_icon="🎤", layout="wide")

st.title("🎤 Análisis de Artistas")

queries = BigQueryQueries()

# Filtros
limit = st.slider("Número de artistas a mostrar", 10, 50, 20)

try:
    # Top artists
    st.subheader("⭐ Top Artistas")
    top_artists = queries.get_top_artists_by_followers(limit=limit)
    if not top_artists.empty:
        st.dataframe(top_artists, use_container_width=True)

        # Gráfico de seguidores
        fig = px.bar(
            top_artists,
            x="followers",
            y="name",
            orientation="h",
            labels={"followers": "Seguidores", "name": "Artista"},
            title="Top Artistas por Seguidores",
        )
        fig.update_layout(height=600)
        st.plotly_chart(fig, use_container_width=True)

    # Top artists por time range
    st.subheader("📊 Top Artistas por Período")
    time_range = st.selectbox(
        "Período",
        ["short_term", "medium_term", "long_term"],
        format_func=lambda x: {
            "short_term": "Últimas 4 semanas",
            "medium_term": "Últimos 6 meses",
            "long_term": "Todo el tiempo",
        }[x],
    )

    top_artists_range = queries.get_top_artists_by_time_range(time_range)
    if not top_artists_range.empty:
        fig = px.bar(
            top_artists_range,
            x="position",
            y="artist_name",
            orientation="h",
            labels={"position": "Posición", "artist_name": "Artista"},
            title=f"Top Artistas - {time_range}",
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(top_artists_range, use_container_width=True)

    # Distribución de géneros
    st.subheader("🎶 Distribución de Géneros")
    genre_limit = st.slider("Número de géneros", 10, 30, 20, key="genre_limit")
    genre_dist = queries.get_genre_distribution(limit=genre_limit)

    if not genre_dist.empty:
        col1, col2 = st.columns(2)

        with col1:
            fig = px.pie(
                genre_dist,
                values="count",
                names="genre",
                title="Distribución de Géneros (Pie)",
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = px.bar(
                genre_dist,
                x="count",
                y="genre",
                orientation="h",
                labels={"count": "Cantidad", "genre": "Género"},
                title="Distribución de Géneros (Bar)",
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

        st.dataframe(genre_dist, use_container_width=True)

except Exception as e:
    st.error(f"Error al cargar datos: {e}")
    st.info("Asegúrate de que los datos hayan sido cargados en BigQuery ejecutando el pipeline ETL.")

