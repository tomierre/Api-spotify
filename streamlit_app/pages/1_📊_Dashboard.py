"""Dashboard principal con métricas generales."""

import sys
from pathlib import Path

import plotly.express as px
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from streamlit_app.utils.queries import BigQueryQueries

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

st.title("📊 Dashboard General")

queries = BigQueryQueries()

# Métricas principales
col1, col2, col3, col4 = st.columns(4)

try:
    playlist_count = queries.get_playlist_count()
    track_count = queries.get_track_count()
    artist_count = queries.get_artist_count()
    user_stats = queries.get_user_stats()

    col1.metric("Playlists", playlist_count)
    col2.metric("Tracks", track_count)
    col3.metric("Artistas", artist_count)
    col4.metric("Usuario", user_stats["display_name"].iloc[0] if not user_stats.empty else "N/A")

    # Información del usuario
    st.subheader("👤 Información del Usuario")
    if not user_stats.empty:
        user_col1, user_col2, user_col3 = st.columns(3)
        user_col1.metric("Seguidores", user_stats["followers"].iloc[0])
        user_col2.metric("País", user_stats["country"].iloc[0] or "N/A")
        user_col3.metric("Suscripción", user_stats["product"].iloc[0] or "N/A")

    # Estadísticas de audio features
    st.subheader("🎵 Estadísticas de Audio Features")
    audio_stats = queries.get_audio_features_stats()

    if not audio_stats.empty and audio_stats['avg_danceability'].iloc[0] > 0:
        stats_col1, stats_col2, stats_col3, stats_col4, stats_col5 = st.columns(5)
        stats_col1.metric("Danceability", f"{audio_stats['avg_danceability'].iloc[0]:.2f}")
        stats_col2.metric("Energy", f"{audio_stats['avg_energy'].iloc[0]:.2f}")
        stats_col3.metric("Valence", f"{audio_stats['avg_valence'].iloc[0]:.2f}")
        stats_col4.metric("Acousticness", f"{audio_stats['avg_acousticness'].iloc[0]:.2f}")
        stats_col5.metric("Tempo", f"{audio_stats['avg_tempo'].iloc[0]:.1f} BPM")
    else:
        st.info("ℹ️ No hay datos de audio features disponibles. Esto puede deberse a limitaciones de la API de Spotify.")

    # Top tracks y artists
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🔥 Top Tracks por Popularidad")
        top_tracks = queries.get_top_tracks_by_popularity(limit=10)
        if not top_tracks.empty:
            fig = px.bar(
                top_tracks,
                x="popularity",
                y="name",
                orientation="h",
                labels={"popularity": "Popularidad", "name": "Track"},
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("⭐ Top Artistas por Seguidores")
        top_artists = queries.get_top_artists_by_followers(limit=10)
        if not top_artists.empty:
            fig = px.bar(
                top_artists,
                x="followers",
                y="name",
                orientation="h",
                labels={"followers": "Seguidores", "name": "Artista"},
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

    # Distribución de géneros
    st.subheader("🎶 Distribución de Géneros")
    genre_dist = queries.get_genre_distribution(limit=15)
    if not genre_dist.empty:
        fig = px.pie(
            genre_dist, values="count", names="genre", title="Top Géneros Musicales"
        )
        st.plotly_chart(fig, use_container_width=True)

    # Recently played
    st.subheader("🎧 Reproducciones Recientes")
    recently_played = queries.get_recently_played(limit=20)
    if recently_played is not None and not recently_played.empty:
        st.dataframe(recently_played, use_container_width=True)
    else:
        st.info("ℹ️ No hay datos de reproducciones recientes disponibles.")

except Exception as e:
    st.error(f"Error al cargar datos: {e}")
    st.info("Asegúrate de que los datos hayan sido cargados en BigQuery ejecutando el pipeline ETL.")

