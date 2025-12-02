# Arquitectura

Este documento describe la arquitectura y el diseño del Pipeline ETL de Spotify.

## Resumen del Sistema

El pipeline sigue una arquitectura ETL (Extract, Transform, Load) tradicional con los siguientes componentes:

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐      ┌──────────────┐
│  Spotify   │─────▶│   Extraer    │─────▶│ Transformar │─────▶│    Cargar    │
│    API     │      │              │      │              │      │  BigQuery    │
└────────────┘      └──────────────┘      └─────────────┘      └──────────────┘
                                                      │
                                                      ▼
                                            ┌──────────────┐
                                            │  Streamlit   │
                                            │  Dashboard   │
                                            └──────────────┘
```

## Componentes

### 1. Cliente de Spotify (`src/spotify/client.py`)

**Responsabilidad**: Autenticación y comunicación con la API

- Maneja el flujo de autenticación OAuth2
- Gestiona la renovación y caché de tokens
- Implementa límites de velocidad y lógica de reintentos
- Proporciona métodos para todos los endpoints de la API de Spotify

**Características Clave**:
- Renovación automática de tokens
- Retroceso exponencial para límites de velocidad
- Manejo de errores y reintentos

### 2. Extractores de Datos (`src/spotify/extractor.py`)

**Responsabilidad**: Extraer datos de la API de Spotify

- Extrae información del perfil de usuario
- Obtiene playlists con paginación
- Recupera tracks y características de audio
- Obtiene información de artistas
- Obtiene tracks reproducidos recientemente
- Recupera tracks y artistas más escuchados

**Límites de Extracción** (para optimización de costos):
- Máximo 20 playlists
- Máximo 100 tracks por playlist
- Últimos 50 tracks reproducidos recientemente
- Top 20 tracks/artistas por rango de tiempo

### 3. Transformador de Datos (`src/spotify/transformers.py`)

**Responsabilidad**: Transformar y validar datos

- Normaliza estructuras de datos de diferentes endpoints
- Valida datos usando modelos Pydantic
- Enriquece datos con timestamps
- Limpia y estandariza formatos

**Modelos de Validación**:
- `UserModel` - Datos del perfil de usuario
- `PlaylistModel` - Información de playlists
- `TrackModel` - Detalles de tracks
- `AudioFeaturesModel` - Características de audio
- `ArtistModel` - Información de artistas

### 4. Cliente de BigQuery (`src/bigquery/client.py`)

**Responsabilidad**: Conexión a BigQuery y gestión de datasets

- Gestiona la conexión del cliente de BigQuery
- Asegura que el dataset exista
- Crea tablas con esquemas
- Maneja operaciones de tablas

### 5. Cargador de BigQuery (`src/bigquery/loader.py`)

**Responsabilidad**: Cargar datos en BigQuery

- Implementa estrategia upsert (merge)
- Maneja carga incremental
- Gestiona inserciones por lotes
- Deduplica datos

**Estrategia de Carga**:
- Upsert para registros existentes
- Insert para nuevos registros
- Procesamiento por lotes para eficiencia

### 6. Pipeline ETL (`pipelines/etl_pipeline.py`)

**Responsabilidad**: Orquestar el proceso ETL completo

- Coordina extracción, transformación y carga
- Maneja errores y logging
- Proporciona resumen de ejecución

## Flujo de Datos

### Fase de Extracción

1. Autenticarse con la API de Spotify
2. Extraer perfil de usuario
3. Extraer playlists del usuario (limitado a 20)
4. Para cada playlist, extraer tracks (limitado a 100 por playlist)
5. Extraer características de audio para tracks únicos
6. Extraer información de artistas para artistas únicos
7. Extraer tracks reproducidos recientemente (últimos 50)
8. Extraer tracks y artistas más escuchados (top 20 cada uno)

### Fase de Transformación

1. Normalizar estructuras de datos
2. Validar datos con modelos Pydantic
3. Agregar timestamps de extracción
4. Limpiar y estandarizar formatos
5. Preparar datos para esquemas de BigQuery

### Fase de Carga

1. Conectar a BigQuery
2. Para cada tabla:
   - Verificar si existen registros
   - Realizar operación upsert (merge)
   - Insertar nuevos registros
   - Actualizar registros existentes

## Esquema de Base de Datos

### Tablas

1. **users** - Información del perfil de usuario
2. **playlists** - Metadatos de playlists
3. **tracks** - Información de tracks
4. **track_audio_features** - Características de análisis de audio
5. **artists** - Información de artistas
6. **playlist_tracks** - Relación muchos a muchos
7. **recently_played** - Historial de reproducción (particionado por fecha)
8. **top_tracks** - Tracks más escuchados del usuario por rango de tiempo (particionado)
9. **top_artists** - Artistas más escuchados del usuario por rango de tiempo (particionado)

### Estrategia de Particionado

- **recently_played**: Particionado por `played_at` (fecha)
- **top_tracks**: Particionado por `extracted_at` (fecha)
- **top_artists**: Particionado por `extracted_at` (fecha)

Esto permite consultas eficientes de datos de series temporales y ayuda con políticas de retención de datos.

## Optimización de Costos

### Optimización de Almacenamiento

- Usar tipos de datos apropiados (STRING en lugar de TEXT)
- Particionar solo tablas de series temporales
- Implementar políticas de retención de datos (90 días para recently_played)

### Optimización de Consultas

- Limitar extracción solo a datos necesarios
- Usar carga incremental (solo datos nuevos/modificados)
- Implementar caché en el dashboard de Streamlit
- Usar cláusulas LIMIT en consultas

### Límites de la Capa Gratuita

- **Almacenamiento**: 10 GB/mes (gratis)
- **Consultas**: 1 TB/mes (gratis)

El pipeline está diseñado para mantenerse bien dentro de estos límites.

## Manejo de Errores

### Lógica de Reintentos

- Reintento automático con retroceso exponencial para límites de velocidad
- Renovación de token en errores de autenticación
- Máximo 3 reintentos para errores transitorios

### Logging

- Configuración centralizada de logging
- Diferentes niveles de log (DEBUG, INFO, WARNING, ERROR)
- Logging a archivo en entorno de producción

## Seguridad

### Gestión de Credenciales

- Variables de entorno para datos sensibles
- Archivo `.env` (no incluido en git)
- JSON de cuenta de servicio para GCP (almacenado de forma segura)

### Flujo OAuth2

- Almacenamiento seguro de tokens en `.spotify_cache`
- Renovación automática de tokens
- Sin credenciales hardcodeadas

## Consideraciones de Escalabilidad

### Diseño Actual

- Extracción de usuario único
- Ejecución manual
- Adecuado para análisis de datos personales

### Mejoras Futuras

- Soporte multi-usuario
- Ejecución programada (cron, Cloud Scheduler)
- Procesamiento paralelo para grandes conjuntos de datos
- Actualizaciones de datos en streaming

## Monitoreo

### Monitoreo de Costos

- Script para verificar uso de BigQuery
- Alertas para aproximarse a límites de la capa gratuita
- Proyecciones mensuales

### Monitoreo del Pipeline

- Logging detallado en cada paso
- Resúmenes de ejecución
- Seguimiento de errores

## Estrategia de Testing

### Tests Unitarios

- Probar cada componente independientemente
- Simular APIs externas (Spotify, BigQuery)
- Validar transformaciones de datos

### Tests de Integración

- Testing end-to-end del pipeline
- Probar con datos de prueba
- Verificar esquemas de BigQuery
