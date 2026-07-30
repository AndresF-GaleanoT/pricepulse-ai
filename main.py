from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse

from datetime import datetime
from app.models import ProductRequest
from app.config import PORT
from app.database import init_db, save_analysis, get_history
from app.serpapi import buscar_precios
from app.crewai_flow import analizar, analisis_rapido
from app.pdf import generar_pdf


@asynccontextmanager
async def lifespan(app):
    init_db()
    yield


app = FastAPI(title="PricePulse AI", version="3.0", lifespan=lifespan)


@app.post("/analizar-precios")
async def endpoint_analizar(data: ProductRequest):
    try:
        precios = await buscar_precios(data.producto)
        reporte = await analizar(data.producto, data.plataformas, precios)
        save_analysis(data.producto, data.plataformas, precios, reporte["texto"])

        resumen = reporte.get("estructurado", {})
        filas = [
            {
                "fecha": datetime.now().isoformat(),
                "producto": data.producto,
                "plataforma": p.get("plataforma"),
                "titulo": p.get("titulo"),
                "precio": p.get("precio"),
                "link": p.get("link"),
            }
            for p in precios
        ]

        filas.append({
            "fecha": datetime.now().isoformat(),
            "producto": f"RESUMEN: {data.producto}",
            "plataforma": resumen.get("mejor_plataforma", ""),
            "titulo": resumen.get("veredicto", ""),
            "precio": resumen.get("precio_promedio"),
            "link": resumen.get("explicacion", ""),
        })

        return {
            "status": "success",
            "producto": data.producto,
            "precios_encontrados": precios,
            "reporte_ia": reporte["texto"],
            "resumen": resumen,
            "filas": filas
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/historial")
async def endpoint_historial(producto: str = None, limit: int = 50):
    return get_history(producto, limit)


@app.get("/exportar-pdf")
async def endpoint_exportar(producto: str):
    try:
        precios = await buscar_precios(producto)
        reporte = await analisis_rapido(producto, precios)
        pdf_bytes = generar_pdf(producto, precios, reporte)

        return StreamingResponse(
            iter([pdf_bytes]),
            media_type="application/pdf",
            headers={
                "Content-Disposition":
                    f"attachment; filename=reporte_{producto.replace(' ', '_')}.pdf"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    return {"status": "ok", "version": "3.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
