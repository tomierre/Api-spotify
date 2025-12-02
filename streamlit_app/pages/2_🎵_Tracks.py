"""Análisis detallado de tracks."""

import sys
from pathlib import Path

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from streamlit_app.utils.queries import BigQueryQueries

st.set_page_config(page_title="Tracks", page_icon="🎵", layout="wide")

st.title("🎵 Análisis de Tracks")

queries = BigQueryQueries()

# Filtros
col1, col2 = st.columns(2)
with col1:
    limit = st.slider("Número de tracks a mostrar", 10, 50, 20)
with col2:
    sort_by = st.selectbox(
        "Ordenar por",
        ["popularity", "danceability", "energy", "valence", "tempo"],
    )

try:
    # Top tracks
    st.subheader("🔥 Top Tracks")
    top_tracks = queries.get_top_tracks_by_popularity(limit=limit)
    if not top_tracks.empty:
        st.dataframe(top_tracks, use_container_width=True)

    # Audio features analysis
    st.subheader("🎚️ Análisis de Audio Features")
    audio_stats = queries.get_audio_features_stats()

    if not audio_stats.empty and audio_stats['avg_danceability'].iloc[0] > 0:
        # Radar chart de audio features promedio
        features = ["danceability", "energy", "valence", "acousticness"]
        values = [
            audio_stats["avg_danceability"].iloc[0],
            audio_stats["avg_energy"].iloc[0],
            audio_stats["avg_valence"].iloc[0],
            audio_stats["avg_acousticness"].iloc[0],
        ]

        fig = go.Figure()

        fig.add_trace(
            go.Scatterpolar(
                r=values,
                theta=features,
                fill="toself",
                name="Promedio",
            )
        )

        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
            showlegend=True,
            title="Audio Features Promedio",
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("ℹ️ No hay datos de audio features disponibles para mostrar el análisis.")

    # Tracks por audio feature
    st.subheader(f"🎯 Tracks por {sort_by.capitalize()}")
    tracks_by_feature = queries.get_tracks_by_audio_feature(sort_by, limit=limit)
    if not tracks_by_feature.empty:
        fig = px.bar(
            tracks_by_feature,
            x=sort_by,
            y="track_name",
            orientation="h",
            labels={sort_by: sort_by.capitalize(), "track_name": "Track"},
        )
        fig.update_layout(height=600)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info(f"ℹ️ No hay tracks con datos de {sort_by} disponibles.")

    # Top tracks por time range
    st.subheader("📊 Top Tracks por Período")
    time_range = st.selectbox(
        "Período",
        ["short_term", "medium_term", "long_term"],
        format_func=lambda x: {
            "short_term": "Últimas 4 semanas",
            "medium_term": "Últimos 6 meses",
            "long_term": "Todo el tiempo",
        }[x],
    )

    top_tracks_range = queries.get_top_tracks_by_time_range(time_range)
    if not top_tracks_range.empty:
        fig = px.bar(
            top_tracks_range,
            x="position",
            y="track_name",
            orientation="h",
            labels={"position": "Posición", "track_name": "Track"},
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(top_tracks_range, use_container_width=True)

except Exception as e:
    st.error(f"Error al cargar datos: {e}")
    st.info("Asegúrate de que los datos hayan sido cargados en BigQuery ejecutando el pipeline ETL.")

