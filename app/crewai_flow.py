import json
import asyncio
from crewai import Agent, Task, Crew, LLM
from app.config import NVIDIA_BASE_URL, MODEL_NAME
import os


def _create_llm():
    return LLM(
        model=MODEL_NAME,
        base_url=NVIDIA_BASE_URL,
        api_key=os.environ["OPENAI_API_KEY"],
        temperature=0,
        timeout=120
    )


async def analizar(producto: str, plataformas: list, precios_reales: list) -> dict:
    precios_texto = "\n".join(
        f"- {p['plataforma']}: ${p['precio']} | {p['titulo']}" for p in precios_reales[:10]
    ) if precios_reales else "No se encontraron precios."

    llm = _create_llm()

    captador = Agent(
        role="Captador de Datos",
        goal="Extraer precios, calcular minimo, maximo, promedio y detectar anomalias.",
        backstory="Analista numerico especializado en extraer metricas de precios de e-commerce.",
        llm=llm,
        verbose=False,
        allow_delegation=False
    )

    organizador = Agent(
        role="Organizador de Datos",
        goal="Estructurar el analisis numerico en secciones claras: metricas, comparativa, anomalias, recomendacion.",
        backstory="Estructurador de informacion que transforma datos crudos en secciones ordenadas.",
        llm=llm,
        verbose=False,
        allow_delegation=False
    )

    redactor = Agent(
        role="Generador de Reportes JSON",
        goal="Generar UNICAMENTE un JSON valido sin texto adicional, sin markdown, sin etiquetas codeblock.",
        backstory="Especialista en formato JSON estricto para integracion automatica con APIs.",
        llm=llm,
        verbose=False,
        allow_delegation=False
    )

    tarea1 = Task(
        description=f"""
        Eres el Captador de Datos. Analiza estos precios en bruto para '{producto}' en las plataformas: {plataformas}.

        PRECIOS:
        {precios_texto}

        Debes identificar y devolver:
        - Precio minimo, maximo y promedio de todos los listados.
        - La plataforma con el precio mas bajo (mejor plataforma).
        - Cualquier anomalia (precio extremadamente alto o bajo comparado con el promedio).
        - Total de ofertas analizadas.

        Devuelve SOLO los hallazgos, sin JSON ni formato especial.
        """,
        expected_output="Lista de hallazgos: precio minimo, maximo, promedio, mejor plataforma, anomalias, total ofertas.",
    )

    tarea2 = Task(
        description="""
        Eres el Organizador de Datos. Toma los hallazgos del Captador y organizalos en estas 4 secciones exactas:

        1. METRICAS: precio minimo, maximo, promedio, total ofertas.
        2. COMPARATIVA: mejor plataforma y por que.
        3. ANOMALIAS: si hay precios sospechosos o destacables.
        4. RECOMENDACION: comprar, esperar o evitar, con justificacion.

        Devuelve SOLO el texto organizado con las 4 secciones. No incluyas JSON.
        """,
        expected_output="Texto con 4 secciones: METRICAS, COMPARATIVA, ANOMALIAS, RECOMENDACION.",
    )

    tarea3 = Task(
        description=f"""
        Eres el Generador de Reportes JSON. Toma el texto organizado del Organizador y genera UNICAMENTE este JSON, sin texto antes ni despues, sin ```json, sin markdown:

        {{
          "producto": "{producto}",
          "precio_minimo": <numero>,
          "precio_maximo": <numero>,
          "precio_promedio": <numero>,
          "mejor_plataforma": "<nombre>",
          "total_ofertas": <numero>,
          "veredicto": "oferta" o "normal" o "anomalia",
          "explicacion": "<frase corta explicando el veredicto>",
          "recomendacion": "comprar" o "esperar" o "evitar"
        }}

        IMPORTANTE: Los valores <numero> deben ser numeros, no texto. No uses comillas alrededor de numeros.
        IMPORTANTE: Devuelve SOLO el JSON, sin texto adicional, sin etiquetas de codigo, sin explicaciones.
        """,
        expected_output="JSON valido con los 9 campos exactos.",
    )

    tarea1.agent = captador
    tarea2.agent = organizador
    tarea3.agent = redactor

    crew = Crew(agents=[captador, organizador, redactor], tasks=[tarea1, tarea2, tarea3], verbose=False)

    resultado = await asyncio.to_thread(crew.kickoff)
    texto = str(resultado)

    try:
        inicio = texto.index("{")
        fin = texto.rindex("}") + 1
        datos = json.loads(texto[inicio:fin])
    except (ValueError, json.JSONDecodeError):
        datos = {}

    return {
        "texto": texto,
        "estructurado": datos
    }


async def analisis_rapido(producto: str, precios: list) -> str:
    llm = _create_llm()
    analista = Agent(
        role="Analista",
        goal=f"Analizar precios de {producto}",
        backstory="Eres un analista de mercados.",
        verbose=False,
        llm=llm,
        allow_delegation=False
    )
    tarea = Task(
        description=f"Analiza precios de {producto}: {json.dumps(precios[:5])}",
        expected_output="Reporte corto.",
    )
    tarea.agent = analista
    crew = Crew(agents=[analista], tasks=[tarea], verbose=False)
    resultado = await asyncio.to_thread(crew.kickoff)
    return str(resultado)
