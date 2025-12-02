"""Tendencias temporales."""

import sys
from pathlib import Path

import plotly.express as px
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from streamlit_app.utils.queries import BigQueryQueries

st.set_page_config(page_title="Trends", page_icon="📈", layout="wide")

st.title("📈 Tendencias Temporales")

queries = BigQueryQueries()

# Filtros
days = st.slider("Período de análisis (días)", 7, 90, 30)

try:
    # Tendencias de reproducciones
    st.subheader("📊 Tendencias de Reproducciones")
    trends = queries.get_trends_over_time(days=days)

    if not trends.empty:
        col1, col2 = st.columns(2)

        with col1:
            fig = px.line(
                trends,
                x="date",
                y="unique_tracks",
                labels={"date": "Fecha", "unique_tracks": "Tracks Únicos"},
                title="Tracks Únicos por Día",
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = px.line(
                trends,
                x="date",
                y="total_plays",
                labels={"date": "Fecha", "total_plays": "Total de Reproducciones"},
                title="Total de Reproducciones por Día",
            )
            st.plotly_chart(fig, use_container_width=True)

        st.dataframe(trends, use_container_width=True)

    # Comparación de top tracks por período
    st.subheader("🔄 Comparación de Top Tracks por Período")
    time_ranges = ["short_term", "medium_term", "long_term"]
    time_range_labels = {
        "short_term": "Últimas 4 semanas",
        "medium_term": "Últimos 6 meses",
        "long_term": "Todo el tiempo",
    }

    comparison_data = []
    for tr in time_ranges:
        top_tracks = queries.get_top_tracks_by_time_range(tr)
        if not top_tracks.empty:
            comparison_data.append(
                {
                    "Período": time_range_labels[tr],
                    "Tracks": len(top_tracks),
                    "Popularidad Promedio": top_tracks["popularity"].mean(),
                }
            )

    if comparison_data:
        import pandas as pd

        comparison_df = pd.DataFrame(comparison_data)
        fig = px.bar(
            comparison_df,
            x="Período",
            y=["Tracks", "Popularidad Promedio"],
            barmode="group",
            title="Comparación de Períodos",
        )
        st.plotly_chart(fig, use_container_width=True)

    # Comparación de top artists por período
    st.subheader("🔄 Comparación de Top Artists por Período")
    comparison_artists = []
    for tr in time_ranges:
        top_artists = queries.get_top_artists_by_time_range(tr)
        if not top_artists.empty:
            comparison_artists.append(
                {
                    "Período": time_range_labels[tr],
                    "Artistas": len(top_artists),
                    "Seguidores Promedio": top_artists["followers"].mean(),
                }
            )

    if comparison_artists:
        import pandas as pd

        comparison_artists_df = pd.DataFrame(comparison_artists)
        fig = px.bar(
            comparison_artists_df,
            x="Período",
            y=["Artistas", "Seguidores Promedio"],
            barmode="group",
            title="Comparación de Artistas por Período",
        )
        st.plotly_chart(fig, use_container_width=True)

    # Recently played timeline
    st.subheader("🎧 Timeline de Reproducciones Recientes")
    recently_played = queries.get_recently_played(limit=100)
    if not recently_played.empty:
        import pandas as pd

        recently_played["played_at"] = pd.to_datetime(recently_played["played_at"])
        recently_played = recently_played.sort_values("played_at")

        fig = px.scatter(
            recently_played,
            x="played_at",
            y="track_name",
            labels={"played_at": "Fecha", "track_name": "Track"},
            title="Timeline de Reproducciones",
        )
        st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Error al cargar datos: {e}")
    st.info("Asegúrate de que los datos hayan sido cargados en BigQuery ejecutando el pipeline ETL.")

