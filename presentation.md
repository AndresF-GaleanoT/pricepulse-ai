---
marp: true
theme: uncover
class:
  - lead
  - invert
paginate: true
---

<!-- _class: lead invert -->

# **PricePulse AI**

Monitoreo inteligente de precios e-commerce con **3 agentes IA**

Hecho con 🐍 Python · NVIDIA NIM · CrewAI · n8n · PostgreSQL

---

## El Problema

Cada hora, miles de productos cambian de precio.

- Hacer seguimiento **manual** es imposible
- Detectar **ofertas** requiere estar 24/7
- Comparar **Amazon + eBay + Mercado Libre** es tedioso

**PricePulse AI automatiza todo.**

---

## Stack Tecnológico

| Componente | Tecnología |
|------------|-----------|
| **API** | FastAPI (async) |
| **Agentes IA** | CrewAI (3 agentes) |
| **LLM** | NVIDIA NIM - Llama 3.1 70B |
| **Precios** | SerpAPI |
| **Orquestador** | n8n |
| **BD** | PostgreSQL 16 |
| **Dashboard** | Streamlit |
| **Infra** | Docker Compose + Oracle Linux |
| **HTTPS** | Cloudflare Tunnel |

---

## Arquitectura

![h:500](https://raw.githubusercontent.com/AndresF-GaleanoT/pricepulse-ai/main/assets/architecture.png)

---

## 3 Agentes CrewAI

```
SerpAPI ──► Cache ──► [Captador] ──► [Organizador] ──► [Redactor]
                           │                │                │
                      Métricas          Secciones          JSON
                     (min/max/avg)   (comparativa,    (reporte final)
                                      anomalías)
```

- **Captador**: extrae métricas numéricas
- **Organizador**: estructura en secciones claras
- **Redactor**: genera JSON sin markdown, temperatura 0

---

## Flujo Completo

```
[Schedule n8n]
     │
     ▼
[SerpAPI] ─── Amazon, eBay, Mercado Libre
     │
     ▼
[CrewAI] ─── 3 agentes con NVIDIA NIM
     │
     ├──► PostgreSQL (historial)
     ├──► Google Sheets (backup)
     ├──► Excel (.xlsx)
     └──► Dashboard Streamlit
```

---

## Dashboard en Vivo

- **Métricas**: total precios, productos, plataformas
- **Gráficos**: promedio por plataforma, tendencias históricas
- **Filtros**: por producto, plataforma, rango de fechas
- **Tabla**: detalle con links a cada oferta

Sin dependencia externa — lee directo de la API.

---

## Demo

```bash
curl -X POST http://localhost:8000/analizar-precios \
  -H "Content-Type: application/json" \
  -d '{"producto":"Raspberry Pi 5",
       "plataformas":["amazon","ebay","mercadolibre"]}' | jq '.filas'
```

Respuesta en **< 10s** con precios reales + análisis IA.

---

## Resultados Reales

| Producto | Plataforma | Precio más bajo |
|----------|-----------|----------------|
| Raspberry Pi 5 | Amazon | **$86.18** |
| NVIDIA Jetson Orin | eBay | **$675.04** |

- **34+ precios** por ejecución
- **3 plataformas** simultáneas
- **Anomalías** detectadas automáticamente
- **Veredicto**: oferta, normal o anomalía

---

## Costos

| Servicio | Plan | Costo |
|----------|------|-------|
| NVIDIA NIM | Gratuito | $0 |
| SerpAPI | Gratuito (100/mes) | $0 |
| PostgreSQL | Self-hosted | $0 |
| n8n | Self-hosted | $0 |
| Cloudflare | Gratuito | $0 |
| **Total** | | **$0/mes** |

---

## Roadmap

✅ **Completado**
- 3 agentes CrewAI + NVIDIA NIM
- Amazon, eBay, Mercado Libre
- Dashboard Streamlit
- n8n scheduler + Google Sheets
- Docker Compose

🔜 **Próximos**
- Alertas Telegram
- Predicción de tendencias ML
- Autenticación JWT
- Tests automatizados
- Modo oscuro

---

<!-- _class: lead invert -->

# **Gracias**

### ⭐ ¿Te gusta? ¡Dale una estrella en GitHub!

https://github.com/AndresF-GaleanoT/pricepulse-ai

---

*Hecho con Python, NVIDIA NIM, CrewAI y mucho café ☕*
