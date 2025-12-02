# Comenzar

Esta guía te ayudará a configurar y ejecutar el Pipeline ETL de Spotify desde cero.

## Prerrequisitos

Antes de comenzar, asegúrate de tener:

1. **Python 3.11 o superior** instalado
2. **Cuenta de Spotify Developer** con una aplicación creada
3. **Cuenta de Google Cloud Platform** con BigQuery habilitado
4. **Cuenta de Servicio de GCP** con permisos de BigQuery

## Paso 1: Clonar y Configurar el Proyecto

```bash
# Clonar el repositorio
git clone <repository-url>
cd Spotify-api

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Para desarrollo
```

## Paso 2: Configurar la API de Spotify

1. Ve al [Panel de Spotify Developer](https://developer.spotify.com/dashboard)
2. Crea una nueva aplicación
3. Anota tu **Client ID** y **Client Secret**
4. Agrega la URI de redirección: `http://localhost:8888/callback`
5. Selecciona **Web API** en la sección API/SDKs

## Paso 3: Configurar Google Cloud Platform

1. Crea un nuevo proyecto de GCP o usa uno existente
2. Habilita la API de BigQuery
3. Crea una Cuenta de Servicio:
   - Ve a IAM & Admin → Service Accounts
   - Crea una nueva cuenta de servicio
   - Otorga los roles "BigQuery Data Editor" y "BigQuery Job User"
   - Crea y descarga el archivo JSON de la clave

## Paso 4: Configurar Variables de Entorno

```bash
# Copiar archivo de ejemplo de entorno
cp .env.example .env

# Editar .env con tus credenciales
```

Actualiza `.env` con:

```env
# API de Spotify
SPOTIFY_CLIENT_ID=tu_client_id_aqui
SPOTIFY_CLIENT_SECRET=tu_client_secret_aqui
SPOTIFY_REDIRECT_URI=http://localhost:8888/callback
SPOTIFY_SCOPE=user-read-recently-played,user-top-read,user-library-read,playlist-read-private

# Google Cloud / BigQuery
GOOGLE_APPLICATION_CREDENTIALS=/ruta/al/archivo-service-account-key.json
BIGQUERY_PROJECT_ID=tu-id-de-proyecto-gcp
BIGQUERY_DATASET_ID=spotify_data

# Límites de Extracción (opcional - valores por defecto mostrados)
MAX_PLAYLISTS=20
MAX_TRACKS_PER_PLAYLIST=100
MAX_RECENTLY_PLAYED=50
TOP_ITEMS_LIMIT=20
MAX_AUDIO_FEATURES_BATCH=100

# Configuración de la Aplicación
LOG_LEVEL=INFO
ENVIRONMENT=development
```

## Paso 5: Autenticarse con Spotify

En la primera ejecución, necesitarás autenticarte con Spotify:

1. Ejecuta cualquier script que use la API de Spotify (ej: `python scripts/run_etl.py`)
2. Verás una URL en la consola
3. Abre la URL en tu navegador
4. Autoriza la aplicación
5. Serás redirigido a `http://localhost:8888/callback`
6. Copia la URL completa de tu navegador
7. El token se guardará en caché en `.spotify_cache` para uso futuro

## Paso 6: Configurar Tablas de BigQuery

```bash
python scripts/setup_bigquery.py
```

Esto:
- Creará el dataset de BigQuery (si no existe)
- Creará todas las tablas necesarias con los esquemas apropiados
- Configurará el particionado para las tablas de series temporales

## Paso 7: Ejecutar Pipeline ETL

```bash
python scripts/run_etl.py
```

Esto:
1. Extraerá datos de la API de Spotify
2. Transformará y validará los datos
3. Cargará datos en BigQuery

## Paso 8: Iniciar Dashboard de Streamlit

```bash
streamlit run streamlit_app/main.py
```

Abre tu navegador en `http://localhost:8501` para ver el dashboard.

## Paso 9: Monitorear Costos (Opcional)

```bash
python scripts/monitor_costs.py
```

Esto mostrará:
- Uso actual de almacenamiento
- Uso de consultas de los últimos 30 días
- Proyecciones de uso mensual
- Advertencias si se aproxima a los límites de la capa gratuita

## Solución de Problemas

### Problemas de Autenticación con Spotify

- Asegúrate de que la URI de redirección coincida exactamente en la configuración de la aplicación de Spotify
- Limpia el archivo `.spotify_cache` y vuelve a autenticarte
- Verifica que los scopes estén configurados correctamente

### Problemas de Conexión con BigQuery

- Verifica que la ruta de `GOOGLE_APPLICATION_CREDENTIALS` sea correcta
- Asegúrate de que la cuenta de servicio tenga los permisos apropiados
- Verifica que la API de BigQuery esté habilitada en GCP

### Errores de Importación

- Asegúrate de que el entorno virtual esté activado
- Ejecuta `pip install -r requirements.txt` nuevamente
- Verifica la versión de Python: `python --version` (debe ser 3.11+)

## Próximos Pasos

- Lee la guía de [Arquitectura](architecture.md) para entender el diseño del sistema
- Revisa la [Referencia de API](api-reference.md) para la documentación del código
- Consulta [Despliegue](deployment.md) para la configuración de producción y monitoreo de costos
