# Documentación del Pipeline ETL de Spotify

¡Bienvenido a la documentación del Pipeline ETL de Spotify! Este proyecto proporciona una solución completa para extraer datos de la API de Spotify, transformarlos y cargarlos en BigQuery para su análisis.

> **Nota:** Esta documentación se despliega automáticamente mediante GitHub Actions.

## Resumen

El Pipeline ETL de Spotify está diseñado para:

- **Extraer** datos de la API Web de Spotify (perfil de usuario, playlists, tracks, artistas, características de audio)
- **Transformar** y validar datos usando modelos Pydantic
- **Cargar** datos en BigQuery con esquemas optimizados y actualizaciones incrementales
- **Visualizar** datos a través de un dashboard interactivo con Streamlit
- **Optimizar costos** para mantenerse dentro de los límites de la capa gratuita de BigQuery

## Características Principales

- 🔐 **Autenticación OAuth2** con la API de Spotify
- 📊 **Extracción Completa de Datos** desde múltiples endpoints de Spotify
- ✅ **Validación de Datos** usando modelos Pydantic
- 🚀 **Carga Eficiente en BigQuery** con estrategias upsert/incrementales
- 📈 **Dashboard Interactivo** con Streamlit
- 💰 **Optimización de Costos** para mantener el uso en la capa gratuita
- 📚 **Documentación Completa** con MkDocs

## Inicio Rápido

1. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configurar entorno**:
   ```bash
   cp .env.example .env
   # Editar .env con tus credenciales
   ```

3. **Configurar BigQuery**:
   ```bash
   python scripts/setup_bigquery.py
   ```

4. **Ejecutar Pipeline ETL**:
   ```bash
   python scripts/run_etl.py
   ```

5. **Iniciar Dashboard**:
   ```bash
   streamlit run streamlit_app/main.py
   ```

## Estructura del Proyecto

```
Spotify-api/
├── config/              # Configuración y esquemas
├── src/                 # Código fuente
│   ├── spotify/        # Cliente y extractores de la API de Spotify
│   ├── bigquery/       # Cliente y cargador de BigQuery
│   └── utils/          # Utilidades (logging, validadores)
├── pipelines/          # Pipelines ETL
├── streamlit_app/      # Dashboard de Streamlit
├── tests/              # Tests unitarios
├── scripts/            # Scripts ejecutables
└── docs/               # Documentación
```

## Secciones de Documentación

- **[Comenzar](getting-started.md)** - Guía de instalación y configuración
- **[Arquitectura](architecture.md)** - Arquitectura y diseño del sistema
- **[Referencia de API](api-reference.md)** - Documentación del código
- **[Guía de la API de Spotify](spotify-api-guide.md)** - Endpoints y uso de la API de Spotify
- **[Despliegue](deployment.md)** - Configuración de producción y monitoreo de costos

## Requisitos

- Python 3.11+
- Cuenta de Spotify Developer (Client ID y Secret)
- Cuenta de Google Cloud Platform con BigQuery habilitado
- Credenciales de cuenta de servicio de GCP (archivo JSON)

## Optimización de Costos

Este proyecto está diseñado para operar dentro de la capa gratuita de BigQuery:

- **10 GB** de almacenamiento por mes (gratis)
- **1 TB** de consultas por mes (gratis)

Consulta la [Guía de Despliegue](deployment.md) para estrategias de monitoreo y optimización de costos.

## Licencia

MIT License

## Contribuciones

¡Las contribuciones son bienvenidas! Por favor, no dudes en enviar un Pull Request.
