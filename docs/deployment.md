# Guía de Despliegue

Esta guía cubre el despliegue, monitoreo de costos y estrategias de optimización para el Pipeline ETL de Spotify.

## Configuración de Producción

### Configuración del Entorno

1. **Establecer Variables de Entorno**:
   ```bash
   export SPOTIFY_CLIENT_ID="tu_client_id"
   export SPOTIFY_CLIENT_SECRET="tu_client_secret"
   export GOOGLE_APPLICATION_CREDENTIALS="/ruta/al/archivo/key.json"
   export BIGQUERY_PROJECT_ID="tu-id-de-proyecto"
   export ENVIRONMENT="production"
   export LOG_LEVEL="INFO"
   ```

2. **Credenciales Seguras**:
   - Nunca commitear el archivo `.env` al control de versiones
   - Usar servicios de gestión de secretos en producción
   - Rotar credenciales regularmente

### Configuración de BigQuery

1. **Crear Dataset**:
   ```bash
   python scripts/setup_bigquery.py
   ```

2. **Verificar Tablas**:
   - Verificar que todas las tablas estén creadas
   - Verificar que los esquemas sean correctos
   - Confirmar que el particionado esté configurado

### Ejecución Programada

#### Usando Cron (Linux/Mac)

```bash
# Editar crontab
crontab -e

# Ejecutar ETL diariamente a las 2 AM
0 2 * * * cd /ruta/a/Spotify-api && /ruta/a/venv/bin/python scripts/run_etl.py >> logs/cron.log 2>&1
```

#### Usando Cloud Scheduler (GCP)

1. Crear Cloud Function o servicio Cloud Run
2. Programar con Cloud Scheduler
3. Establecer zona horaria y frecuencia apropiadas

## Monitoreo de Costos

### Capa Gratuita de BigQuery

BigQuery ofrece una capa gratuita con:

- **10 GB** de almacenamiento por mes
- **1 TB** de consultas por mes
- **1 GB** de inserciones en streaming por mes

### Script de Monitoreo

Ejecutar el script de monitoreo de costos regularmente:

```bash
python scripts/monitor_costs.py
```

Este script muestra:
- Uso actual de almacenamiento
- Uso de consultas de los últimos 30 días
- Proyecciones mensuales
- Advertencias si se aproxima a los límites

### Configurar Alertas de Presupuesto en GCP

1. **Navegar a Facturación**:
   - Ir a [Consola de GCP](https://console.cloud.google.com)
   - Seleccionar tu proyecto
   - Ir a Facturación → Presupuestos y alertas

2. **Crear Presupuesto**:
   - Hacer clic en "Crear Presupuesto"
   - Establecer cantidad: **$1 USD/mes**
   - Seleccionar tu cuenta de facturación
   - Elegir alcance del proyecto

3. **Configurar Alertas**:
   - Agregar alerta al **50%** del presupuesto
   - Agregar alerta al **90%** del presupuesto
   - Agregar alerta al **100%** del presupuesto
   - Agregar notificaciones por email

4. **Guardar Presupuesto**:
   - Revisar configuración
   - Crear presupuesto

### Monitorear Uso de BigQuery

#### Uso de Almacenamiento

1. Ir a la Consola de BigQuery
2. Seleccionar tu dataset
3. Ver tamaños de tablas en la UI
4. Verificar pestaña "Storage" para uso total

#### Uso de Consultas

1. Ir a la Consola de BigQuery
2. Hacer clic en "Historial de trabajos"
3. Filtrar por rango de fechas
4. Ver columna "Bytes procesados"

#### Usando Information Schema

El uso de consultas se puede verificar con:

```sql
SELECT
  SUM(total_bytes_processed) / POW(1024, 4) as total_tb
FROM
  `project-id.region-us.INFORMATION_SCHEMA.JOBS_BY_PROJECT`
WHERE
  creation_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
  AND job_type = 'QUERY'
```

## Estrategias de Optimización de Costos

### Optimización de Almacenamiento

1. **Políticas de Retención de Datos**:
   - Implementar retención para datos de series temporales
   - Eliminar registros antiguos de `recently_played` (>90 días)
   - Archivar o eliminar snapshots antiguos de `top_tracks`/`top_artists`

2. **Tipos de Datos Eficientes**:
   - Usar STRING en lugar de TEXT
   - Usar INT64 en lugar de FLOAT cuando sea posible
   - Evitar almacenar datos redundantes

3. **Particionado**:
   - Particionar solo tablas de series temporales
   - Usar particionado por fecha para `recently_played`
   - Particionar `top_tracks` y `top_artists` por `extracted_at`

### Optimización de Consultas

1. **Limitar Extracción**:
   - Extraer solo datos necesarios
   - Usar límites de extracción (MAX_PLAYLISTS, etc.)
   - Evitar escaneos completos de tablas

2. **Carga Incremental**:
   - Cargar solo datos nuevos/modificados
   - Usar timestamps para rastrear última extracción
   - Implementar sistema de checkpoint

3. **Caché de Streamlit**:
   - Usar `@st.cache_data` para consultas
   - Establecer TTL apropiado
   - Cachear resultados agregados

4. **Mejores Prácticas de Consultas**:
   - Siempre usar cláusulas LIMIT
   - Filtrar temprano con WHERE
   - Usar SELECT de columnas específicas
   - Evitar SELECT *

### Ejemplo: Script de Retención de Datos

```python
from google.cloud import bigquery

client = bigquery.Client()
dataset_id = "spotify_data"
table_id = "recently_played"

# Eliminar registros más antiguos de 90 días
query = f"""
DELETE FROM `{client.project}.{dataset_id}.{table_id}`
WHERE played_at < TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 90 DAY)
"""

job = client.query(query)
job.result()
```

## Solución de Problemas

### Alto Uso de Almacenamiento

**Síntomas**: Almacenamiento aproximándose al límite de 10 GB

**Soluciones**:
1. Implementar políticas de retención de datos
2. Revisar tamaños de tablas
3. Eliminar datos históricos innecesarios
4. Archivar datos antiguos a Cloud Storage

### Alto Uso de Consultas

**Síntomas**: Uso de consultas aproximándose al límite de 1 TB

**Soluciones**:
1. Revisar consultas del dashboard de Streamlit
2. Agregar caché más agresivo
3. Optimizar consultas (agregar LIMIT, cláusulas WHERE)
4. Reducir frecuencia de actualización del dashboard
5. Limitar frecuencia de extracción de datos

### Problemas de Autenticación

**Síntomas**: Errores 401 Unauthorized

**Soluciones**:
1. Verificar expiración del token
2. Re-autenticarse con Spotify
3. Verificar credenciales en `.env`
4. Verificar permisos de cuenta de servicio

### Límites de Velocidad

**Síntomas**: Errores 429 Too Many Requests

**Soluciones**:
1. Reducir frecuencia de extracción
2. Implementar demoras más largas entre solicitudes
3. Agrupar solicitudes de forma más eficiente
4. Verificar headers de límite de velocidad

## Mejores Prácticas

1. **Monitoreo Regular**: Ejecutar `monitor_costs.py` semanalmente
2. **Establecer Alertas**: Configurar alertas de presupuesto de GCP
3. **Revisar Uso**: Verificar consola de BigQuery mensualmente
4. **Optimizar Consultas**: Revisar y optimizar consultas lentas
5. **Retención de Datos**: Implementar y mantener políticas de retención
6. **Documentación**: Mantener notas de despliegue actualizadas

## Consideraciones de Escalabilidad

### Limitaciones Actuales

- Extracción de usuario único
- Ejecución manual o programada
- Adecuado para uso personal

### Escalado Futuro

Si necesitas escalar:

1. **Soporte Multi-Usuario**:
   - Almacenar tokens por usuario
   - Rastrear extracción por usuario
   - Particionar datos por user_id

2. **Volumen Aumentado**:
   - Considerar capa de pago de BigQuery
   - Implementar caché más agresivo
   - Usar Cloud Functions para procesamiento

3. **Actualizaciones en Tiempo Real**:
   - Usar inserciones en streaming
   - Implementar captura de cambios de datos
   - Usar Pub/Sub para eventos

## Soporte

Para problemas o preguntas:

1. Verificar logs en `logs/spotify_etl.log`
2. Revisar mensajes de error
3. Verificar consola de GCP para errores de BigQuery
4. Revisar estado de la API de Spotify

## Referencias

- [Precios de BigQuery](https://cloud.google.com/bigquery/pricing)
- [Capa Gratuita de BigQuery](https://cloud.google.com/free/docs/free-cloud-features#bigquery)
- [Alertas de Presupuesto de GCP](https://cloud.google.com/billing/docs/how-to/budgets)
