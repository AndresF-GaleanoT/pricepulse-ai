import re
import httpx
from app.config import SERPAPI_KEY
from app.cache import get_cache, set_cache


def _extraer_precio(item: dict) -> float | None:
    price = item.get("extracted_price") or item.get("price")
    if price is None:
        return None
    if isinstance(price, (int, float)):
        return float(price)
    if isinstance(price, str):
        price = re.sub(r"[^\d.,]", "", price).replace(",", ".")
        try:
            return float(price)
        except ValueError:
            return None
    return None


async def _buscar_amazon(producto: str) -> list:
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(
            "https://serpapi.com/search.json",
            params={
                "engine": "amazon",
                "k": producto,
                "api_key": SERPAPI_KEY,
                "amazon_domain": "amazon.com",
                "num": 5,
            },
        )
        resp.raise_for_status()
        data = resp.json()

    return [
        {
            "plataforma": "Amazon",
            "titulo": item.get("title", ""),
            "precio": _extraer_precio(item),
            "link": item.get("link_clean") or item.get("link", ""),
        }
        for item in data.get("organic_results", [])
        if item.get("extracted_price") or item.get("price")
    ]


async def _buscar_ebay(producto: str) -> list:
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(
            "https://serpapi.com/search.json",
            params={
                "engine": "google_shopping",
                "q": producto,
                "api_key": SERPAPI_KEY,
                "num": 10,
            },
        )
        resp.raise_for_status()
        data = resp.json()

    return [
        {
            "plataforma": "eBay",
            "titulo": item.get("title", ""),
            "precio": _extraer_precio(item),
            "link": item.get("link") or item.get("product_link") or "",
        }
        for item in data.get("shopping_results", [])
        if "ebay" in (item.get("source", "") or "").lower()
    ]


async def _buscar_mercadolibre(producto: str) -> list:
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(
            "https://serpapi.com/search.json",
            params={
                "engine": "google",
                "q": f"site:mercadolibre.com {producto}",
                "api_key": SERPAPI_KEY,
                "num": 5,
                "gl": "mx",
                "hl": "es",
            },
        )
        resp.raise_for_status()
        data = resp.json()

    resultados = []
    for item in data.get("organic_results", []):
        link = item.get("link", "")
        if not link or "/libro" in link.lower():
            continue

        rich = item.get("rich_snippet", {})
        exts = (
            rich.get("top", {}).get("detected_extensions", {})
            or rich.get("bottom", {}).get("detected_extensions", {})
        )
        price = exts.get("price")
        if not isinstance(price, (int, float)):
            price = _extraer_precio(item)

        resultados.append({
            "plataforma": "Mercado Libre",
            "titulo": item.get("title", ""),
            "precio": price,
            "link": link,
        })

    return resultados


async def buscar_precios(producto: str):
    cached = get_cache(producto)
    if cached:
        return cached

    resultados = []

    for fn in [_buscar_amazon, _buscar_ebay, _buscar_mercadolibre]:
        try:
            resultados.extend(await fn(producto))
        except Exception:
            pass

    if resultados:
        set_cache(producto, resultados)

    return resultados
