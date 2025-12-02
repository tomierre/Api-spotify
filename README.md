# Spotify ETL Pipeline to BigQuery

Pipeline completo de extracción, transformación y carga (ETL) de datos desde Spotify API hacia BigQuery, con visualización en Streamlit y documentación completa.

## 🎯 Características

- **Extracción de datos** desde Spotify API (perfil, playlists, tracks, artistas, historial)
- **Transformación y validación** de datos con Pydantic
- **Carga a BigQuery** con estrategia upsert/incremental
- **Dashboard interactivo** con Streamlit
- **Documentación completa** con MkDocs
- **Optimización de costos** para mantenerse en la capa gratuita de BigQuery

## 📋 Requisitos

- Python 3.11+
- Cuenta de Spotify Developer (Client ID y Client Secret)
- Proyecto de Google Cloud Platform con BigQuery habilitado
- Credenciales de servicio de GCP (JSON)

## 🚀 Instalación

1. Clonar el repositorio:
```bash
git clone <repository-url>
cd Spotify-api
```

2. Crear entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Para desarrollo
```

4. Configurar variables de entorno:
```bash
cp .env.example .env
# Editar .env con tus credenciales
```

5. Configurar credenciales de GCP:
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
```

## 📖 Uso

### Setup inicial de BigQuery

```bash
python scripts/setup_bigquery.py
```

### Ejecutar pipeline ETL

```bash
python scripts/run_etl.py
```

### Ejecutar dashboard Streamlit

```bash
streamlit run streamlit_app/main.py
```

### Monitorear costos

```bash
python scripts/monitor_costs.py
```

## 📁 Estructura del Proyecto

```
Spotify-api/
├── config/              # Configuración y schemas
├── src/                 # Código fuente principal
│   ├── spotify/        # Cliente y extractores de Spotify
│   ├── bigquery/       # Cliente y loader de BigQuery
│   └── utils/          # Utilidades (logging, validadores)
├── pipelines/          # Pipelines ETL
├── streamlit_app/      # Aplicación Streamlit
├── tests/              # Tests unitarios
├── scripts/            # Scripts ejecutables
└── docs/               # Documentación MkDocs
```

## 🔧 Configuración

Ver `.env.example` para todas las variables de entorno necesarias.

### Límites de extracción (para optimizar costos)

- Máximo 20 playlists
- Máximo 100 tracks por playlist
- Últimas 50 reproducciones recientes
- Top 20 tracks/artists por período

## 📚 Documentación

Para generar y ver la documentación:

```bash
mkdocs serve
```

Luego abrir http://localhost:8000

## 🧪 Testing

```bash
pytest
```

Con cobertura:

```bash
pytest --cov=src --cov-report=html
```

## 📊 Optimización de Costos

Este proyecto está diseñado para mantenerse dentro de la capa gratuita de BigQuery:
- 10 GB de almacenamiento/mes (gratis)
- 1 TB de consultas/mes (gratis)

Ver `docs/deployment.md` para más detalles sobre monitoreo de costos.

## 📝 Licencia

MIT

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor, abre un issue o pull request.

