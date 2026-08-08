# Informe Tecnico: PricePulse AI

**Version:** 3.0
**Fecha:** Julio 2026
**Repositorio:** https://github.com/AndresF-GaleanoT/pricepulse-ai

---

## 1. Resumen Ejecutivo

PricePulse AI es un sistema automatizado de **monitoreo de precios e-commerce** que combina **3 agentes de IA generativa** (CrewAI + NVIDIA NIM) con busqueda en tiempo real via **SerpAPI** para analizar precios de **Amazon, eBay y Mercado Libre**, almacenar historial en **PostgreSQL** y exportar resultados a **Google Sheets y Excel** mediante **n8n**.

El sistema opera con **costo $0/mes** usando tiers gratuitos de NVIDIA NIM y SerpAPI, y corre completamente en **Docker Compose** sobre Oracle Linux.

---

## 2. Arquitectura General

```
┌─────────────────────────────────────────────────────────────┐
│                    ORQUESTACION (n8n)                        │
│            Schedule Trigger: 00:00 / 08:00 / 16:00           │
└──────────────────────────┬──────────────────────────────────┘
                           │ POST /analizar-precios
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                     API (FastAPI :8000)                      │
│                                                             │
│  ┌────────────┐   ┌────────────┐   ┌────────────────────┐  │
│  │  SerpAPI   │   │ Cache JSON │   │  3 Agentes CrewAI  │  │
│  │ Amazon     │   │ (TTL 4h)   │   │  NVIDIA NIM 70B    │  │
│  │ eBay       │   └────────────┘   │  temp=0, verbose   │  │
│  │ MercadoLib │                    └────────────────────┘  │
│  └────────────┘                     ┌────────────────────┐  │
│                                     │   PostgreSQL 16    │  │
│                                     │  (historial)       │  │
│                                     └────────────────────┘  │
└──────────────┬──────────────────────────────────────────────┘
               │ Respuesta JSON (filas[])
               ▼
┌─────────────────────────────────────────────────────────────┐
│                     SALIDAS                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────────┐  │
│  │Google Sheets │  │ Excel .xlsx  │  │ Dashboard Streamlit│ │
│  │ (backup)     │  │ (export)     │  │ (puerto 8501)      │ │
│  └──────────────┘  └──────────────┘  └───────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Componentes del Sistema

### 3.1 API (FastAPI) — `main.py`

Punto de entrada del sistema, corre en el contenedor `precios-api` (puerto 8000).

| Endpoint | Metodo | Funcion |
|----------|--------|---------|
| `/analizar-precios` | POST | Busca precios + analisis IA + guarda historial |
| `/historial` | GET | Consulta historial desde PostgreSQL |
| `/exportar-pdf` | GET | Genera reporte PDF descargable |
| `/health` | GET | Estado del servicio |

**Ejemplo de analisis:**
```bash
curl -X POST http://localhost:8000/analizar-precios \
  -H "Content-Type: application/json" \
  -d '{"producto":"Raspberry Pi 5","plataformas":["amazon","ebay","mercadolibre"]}'
```

**Respuesta JSON:**
```json
{
  "status": "success",
  "producto": "Raspberry Pi 5",
  "precios_encontrados": [
    {"plataforma": "Amazon", "titulo": "...", "precio": 86.18, "link": "..."}
  ],
  "reporte_ia": "Analisis completo...",
  "resumen": {
    "precio_minimo": 86.18,
    "precio_maximo": 259.95,
    "precio_promedio": 169.99,
    "mejor_plataforma": "Amazon",
    "veredicto": "oferta",
    "recomendacion": "comprar"
  },
  "filas": [
    {"fecha": "...", "producto": "...", "plataforma": "Amazon",
     "titulo": "...", "precio": 86.18, "link": "..."},
    {"fecha": "...", "producto": "RESUMEN: Raspberry Pi 5", "...": "..."}
  ]
}
```

### 3.2 Busqueda de Precios (SerpAPI) — `app/serpapi.py`

Ejecuta 3 busquedas paralelas y combina resultados:

| Plataforma | Estrategia | Resultados |
|-----------|-----------|-----------|
| **Amazon** | Motor dedicado `engine=amazon` | 5 |
| **eBay** | Google Shopping filtrado por `source=ebay` | 10 |
| **Mercado Libre** | Google `site:mercadolibre.com` + precio via `rich_snippet` | 5 |

- Los precios se normalizan a `float` (o `None`).
- Si una plataforma falla, las demas continuan (fallback silencioso).
- Maximo **20 precios** por ejecucion; los **10 mejores** van a CrewAI.

### 3.3 Cache — `app/cache.py`

- Cache en archivos JSON por producto (hash MD5 del nombre).
- **TTL configurable** via `CACHE_TTL_HOURS` (default 4h).
- Ubicacion persistente en volumen Docker (`cache_data`).
- Evita consumir cuotas de SerpAPI en consultas repetidas.

### 3.4 Agentes IA (CrewAI) — `app/crewai_flow.py`

Pipeline secuencial de 3 agentes con **NVIDIA NIM** (Llama 3.1 70B, temperatura 0):

```
[1. CAPTADOR]  → [2. ORGANIZADOR]  → [3. REDACTOR]  → JSON
```

| Agente | Funcion |
|--------|---------|
| **Captador de Datos** | Extrae precio minimo, maximo, promedio; detecta anomalias; identifica mejor plataforma |
| **Organizador** | Estructura el analisis en 4 secciones: METRICAS, COMPARATIVA, ANOMALIAS, RECOMENDACION |
| **Redactor** | Genera JSON estricto de 9 campos, sin markdown ni texto adicional |

Cada agente escribe su razonamiento en los logs (`verbose=True`).

### 3.5 Base de Datos — `app/database.py`

PostgreSQL 16 en contenedor `precios-db` (puerto 5432).

```sql
CREATE TABLE IF NOT EXISTS historial (
    id SERIAL PRIMARY KEY,
    fecha TIMESTAMP DEFAULT NOW(),
    producto TEXT NOT NULL,
    plataformas TEXT[],
    precios JSONB,
    reporte TEXT
);
```

### 3.6 Orquestador (n8n) — `n8n_workflow_excel.json`

Workflow de 5 nodos:

```
[Schedule Trigger] → [Set Variables] → [HTTP POST] → [Code] → [Google Sheets]
   0/8/16h UTC       API_URL           analizar        mapear       append
```

- Ejecuta cada **8 horas** (00:00, 08:00, 16:00 UTC).
- POST con **timeout de 600s** (los agentes tardan ~1-2 min).
- Node Code extrae solo el array `filas` (6 columnas).
- Append directo a Google Sheets (OAuth2 funcional).

### 3.7 Dashboard (Streamlit) — `dashboard.py`

Corre dentro del contenedor API (Python 3.11):

```bash
docker compose exec -e API_URL=http://localhost:8000 api \
  streamlit run dashboard.py --server.port 8501 --server.address 0.0.0.0
```

- Lee del endpoint `/historial` (sin dependencia externa).
- Muestra metricas, graficos de tendencia, tabla detallada con links.
- Filtros por producto, plataforma y rango de fechas.
- Compatible con Streamlit antiguo (fallbacks).

### 3.8 Exportacion PDF — `app/pdf.py`

Genera reporte ejecutivo descargable con precios + analisis IA.

---

## 4. Flujo de Trabajo Completo

**Ejecucion automatica (cada 8h):**

1. **n8n** dispara el workflow a las 00/08/16 UTC.
2. HTTP POST a `http://api:8000/analizar-precios` con el producto configurado.
3. **API** llama a **SerpAPI** (Amazon + eBay + Mercado Libre), consulta cache primero.
4. Los **3 agentes CrewAI** analizan los 10 mejores precios con NVIDIA NIM.
5. **API** guarda el resultado completo en **PostgreSQL**.
6. Responde JSON con array `filas[]` (6 columnas) + fila RESUMEN.
7. **n8n** mapea las filas y hace **append a Google Sheets**.
8. El **dashboard** muestra los datos en tiempo real.

---

## 5. Despliegue

### Requisitos
- Docker y Docker Compose
- API keys: `NVIDIA_API_KEY` (build.nvidia.com) y `SERPAPI_KEY`

### Comandos
```bash
git clone https://github.com/AndresF-GaleanoT/pricepulse-ai.git
cd pricepulse-ai
cp .env.example .env
nano .env                    # agregar claves
docker compose up -d --build # levanta api + db + n8n
```

### Servicios

| Servicio | Puerto | Acceso |
|----------|--------|--------|
| API | 8000 | Publica via Cloudflare Tunnel |
| n8n | 5678 | Con autenticacion basica |
| PostgreSQL | 5432 | Solo interno |
| Dashboard | 8501 | IP publica del servidor |

### Actualizacion
```bash
git pull
docker compose up -d --build api
```

---

## 6. Variables de Entorno (`.env`)

```env
NVIDIA_API_KEY=nvapi-...      # Clave NVIDIA NIM (LLM)
NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1
MODEL_NAME=openai/meta/llama-3.1-70b-instruct
SERPAPI_KEY=...               # Clave SerpAPI (precios)
DATABASE_URL=postgresql://precios:precios2024@db:5432/pricepulse
CACHE_TTL_HOURS=4             # Duracion del cache
CACHE_DIR=cache               # Ubicacion del cache
N8N_BASIC_AUTH_USER=admin     # Acceso n8n
N8N_BASIC_AUTH_PASSWORD=...   # Password n8n
N8N_WEBHOOK_URL=...           # URL publica para OAuth
PORT=8000
```

---

## 7. Seguridad

- Los secrets estan en `.env` (ignorado por git).
- n8n con autenticacion basica activa.
- Se recomienda restringir el puerto 8000 al firewall (la API la usan n8n internamente y el dashboard via red local):
  ```bash
  sudo firewall-cmd --permanent --remove-port=8000/tcp; sudo firewall-cmd --reload
  ```

---

## 8. Costos Operativos

| Servicio | Plan | Costo |
|----------|------|-------|
| NVIDIA NIM | Gratuito (1000 credits/mes) | $0 |
| SerpAPI | Gratuito (100 busquedas/mes) | $0 |
| PostgreSQL | Self-hosted | $0 |
| n8n | Self-hosted | $0 |
| Cloudflare Tunnel | Gratuito | $0 |
| **Total** | | **$0/mes** |

---

## 9. Roadmap

- [ ] Alertas Telegram (precio bajo detectado)
- [ ] Prediccion de tendencias con ML
- [ ] Autenticacion JWT
- [ ] Tests automatizados (pytest)
- [ ] Multi-idioma
- [ ] Mas e-commerce (AliExpress)
- [ ] Web scraping como fallback
- [ ] Modo oscuro en dashboard
