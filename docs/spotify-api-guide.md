# Guía de la API de Spotify

Esta guía explica cómo usar los endpoints de la API Web de Spotify en este proyecto.

## Autenticación

El proyecto usa autenticación OAuth2 con el siguiente flujo:

1. El usuario autoriza la aplicación
2. Se recibe el código de autorización
3. Se intercambia el código por un token de acceso
4. Se usa el token de acceso para solicitudes a la API
5. Se renueva el token cuando expira

### Scopes Requeridos

- `user-read-recently-played`: Leer tracks reproducidos recientemente
- `user-top-read`: Leer tracks y artistas más escuchados del usuario
- `user-library-read`: Leer tracks y álbumes guardados del usuario
- `playlist-read-private`: Leer playlists privadas del usuario

## Endpoints Utilizados

### Perfil de Usuario

**Endpoint**: `GET /v1/me`

**Uso**: Obtener información del perfil del usuario actual

**Campos de Respuesta**:
- `id`: ID de usuario
- `display_name`: Nombre para mostrar
- `followers`: Cantidad de seguidores
- `country`: Código de país
- `product`: Tipo de suscripción (free/premium)

### Playlists del Usuario

**Endpoint**: `GET /v1/users/{user_id}/playlists`

**Uso**: Obtener playlists del usuario

**Paginación**: Soporta parámetros `limit` y `offset`

**Campos de Respuesta**:
- `id`: ID de playlist
- `name`: Nombre de playlist
- `description`: Descripción de playlist
- `owner`: Información del propietario
- `public`: Estado público/privado
- `collaborative`: Estado colaborativo
- `followers`: Cantidad de seguidores
- `tracks`: Información de tracks

### Tracks de Playlist

**Endpoint**: `GET /v1/playlists/{playlist_id}/tracks`

**Uso**: Obtener tracks de una playlist

**Paginación**: Soporta parámetros `limit` y `offset`

**Campos de Respuesta**:
- `track`: Objeto de track
- `added_at`: Cuándo se agregó el track
- `added_by`: Usuario que agregó el track

### Características de Audio de Tracks

**Endpoint**: `GET /v1/audio-features`

**Uso**: Obtener características de audio para múltiples tracks

**Límites**: Máximo 100 IDs de tracks por solicitud

**Campos de Respuesta**:
- `danceability`: 0.0-1.0
- `energy`: 0.0-1.0
- `key`: 0-11 (tono musical)
- `loudness`: Valor en dB
- `mode`: 0 (menor) o 1 (mayor)
- `speechiness`: 0.0-1.0
- `acousticness`: 0.0-1.0
- `instrumentalness`: 0.0-1.0
- `liveness`: 0.0-1.0
- `valence`: 0.0-1.0 (positividad)
- `tempo`: BPM
- `time_signature`: 3-7

### Información de Artistas

**Endpoint**: `GET /v1/artists`

**Uso**: Obtener información de múltiples artistas

**Límites**: Máximo 50 IDs de artistas por solicitud

**Campos de Respuesta**:
- `id`: ID de artista
- `name`: Nombre del artista
- `genres`: Lista de géneros
- `popularity`: 0-100
- `followers`: Cantidad de seguidores
- `external_urls`: URLs de Spotify

### Tracks Reproducidos Recientemente

**Endpoint**: `GET /v1/me/player/recently-played`

**Uso**: Obtener tracks reproducidos recientemente

**Límites**: Máximo 50 tracks por solicitud

**Campos de Respuesta**:
- `track`: Objeto de track
- `played_at`: Timestamp de cuándo se reprodujo
- `context`: Contexto de reproducción

### Tracks Más Escuchados

**Endpoint**: `GET /v1/me/top/tracks`

**Uso**: Obtener los tracks más escuchados del usuario

**Parámetros**:
- `time_range`: `short_term` (4 semanas), `medium_term` (6 meses), `long_term` (todo el tiempo)
- `limit`: Máximo 50

**Campos de Respuesta**:
- `id`: ID de track
- `name`: Nombre del track
- `artists`: Información de artistas
- `popularity`: Puntuación de popularidad
- `album`: Información de álbum

### Artistas Más Escuchados

**Endpoint**: `GET /v1/me/top/artists`

**Uso**: Obtener los artistas más escuchados del usuario

**Parámetros**:
- `time_range`: `short_term`, `medium_term`, `long_term`
- `limit`: Máximo 50

**Campos de Respuesta**:
- `id`: ID de artista
- `name`: Nombre del artista
- `genres`: Géneros
- `popularity`: Puntuación de popularidad
- `followers`: Cantidad de seguidores

## Límites de Velocidad

La API de Spotify tiene límites de velocidad:

- **30 solicitudes por segundo** por aplicación
- Headers de límite de velocidad en respuestas:
  - `X-RateLimit-Limit`: Solicitudes permitidas
  - `X-RateLimit-Remaining`: Solicitudes restantes
  - `Retry-After`: Segundos a esperar si se excede el límite

El cliente maneja automáticamente los límites de velocidad con retroceso exponencial.

## Manejo de Errores

### Códigos de Error Comunes

- `400 Bad Request`: Parámetros inválidos
- `401 Unauthorized`: Token inválido o expirado
- `403 Forbidden`: Permisos insuficientes
- `404 Not Found`: El recurso no existe
- `429 Too Many Requests`: Límite de velocidad excedido
- `500 Internal Server Error`: Error del servidor de Spotify

### Formato de Respuesta de Error

```json
{
  "error": {
    "status": 401,
    "message": "Invalid access token"
  }
}
```

## Mejores Prácticas

1. **Cachear Tokens**: Almacenar tokens de forma segura y renovar antes de la expiración
2. **Manejar Paginación**: Siempre verificar el campo `next` en respuestas paginadas
3. **Solicitudes por Lotes**: Usar endpoints por lotes cuando estén disponibles (características de audio, artistas)
4. **Respetar Límites de Velocidad**: Implementar retroceso exponencial
5. **Manejo de Errores**: Manejar todos los casos de error de forma elegante
6. **Validación de Datos**: Validar todas las respuestas de la API antes de procesarlas

## Límites de Extracción de Datos

Para optimizar costos y mantenerse dentro de la capa gratuita, el proyecto implementa límites:

- **Playlists**: Máximo 20 playlists
- **Tracks por Playlist**: Máximo 100 tracks
- **Reproducidos Recientemente**: Últimos 50 tracks
- **Items Más Escuchados**: Top 20 tracks/artistas por rango de tiempo
- **Características de Audio**: Procesados en grupos de 100

Estos límites se pueden ajustar en el archivo `.env`.

## Referencias

- [Documentación de la API Web de Spotify](https://developer.spotify.com/documentation/web-api)
- [Referencia de la API Web de Spotify](https://developer.spotify.com/documentation/web-api/reference)
- [Guía de Autorización](https://developer.spotify.com/documentation/general/guides/authorization)
