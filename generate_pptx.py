from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

BG_DARK = RGBColor(0x1E, 0x1E, 0x2E)
BG_CARD = RGBColor(0x27, 0x28, 0x3B)
ACCENT = RGBColor(0x00, 0xD2, 0xFF)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
GRAY = RGBColor(0xAA, 0xAA, 0xAA)
GREEN = RGBColor(0x4C, 0xAF, 0x50)
ORANGE = RGBColor(0xFF, 0x98, 0x00)

def add_bg(slide, color=BG_DARK):
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = color

def add_shape(slide, left, top, width, height, color, alpha=None):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()
    return shape

def add_text_box(slide, left, top, width, height, text, font_size=18, color=WHITE, bold=False, alignment=PP_ALIGN.LEFT, font_name="Calibri"):
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(font_size)
    p.font.color.rgb = color
    p.font.bold = bold
    p.font.name = font_name
    p.alignment = alignment
    return tf

def add_card(slide, left, top, width, height, title, body, title_size=20, body_size=14, title_color=ACCENT):
    shape = add_shape(slide, left, top, width, height, BG_CARD)
    tf = shape.text_frame
    tf.word_wrap = True
    tf.margin_left = Pt(16)
    tf.margin_right = Pt(16)
    tf.margin_top = Pt(16)
    tf.margin_bottom = Pt(16)
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(title_size)
    p.font.color.rgb = title_color
    p.font.bold = True
    p.font.name = "Calibri"
    p2 = tf.add_paragraph()
    p2.text = body
    p2.font.size = Pt(body_size)
    p2.font.color.rgb = GRAY
    p2.font.name = "Calibri"
    p2.space_before = Pt(8)

# --- SLIDE 1: Portada ---
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide)
add_shape(slide, Inches(0), Inches(2.8), Inches(13.333), Inches(0.06), ACCENT)
add_text_box(slide, Inches(1), Inches(1.5), Inches(11), Inches(1.2), "PricePulse AI", font_size=54, color=WHITE, bold=True, alignment=PP_ALIGN.CENTER)
add_text_box(slide, Inches(1), Inches(3.2), Inches(11), Inches(0.8), "Monitoreo inteligente de precios e-commerce con 3 agentes IA", font_size=26, color=ACCENT, alignment=PP_ALIGN.CENTER)
add_text_box(slide, Inches(1), Inches(4.2), Inches(11), Inches(0.6), "Python  FastAPI  CrewAI  NVIDIA NIM  n8n  PostgreSQL", font_size=18, color=GRAY, alignment=PP_ALIGN.CENTER)
add_text_box(slide, Inches(1), Inches(5.8), Inches(11), Inches(0.5), "github.com/AndresF-GaleanoT/pricepulse-ai", font_size=16, color=GRAY, alignment=PP_ALIGN.CENTER)

# --- SLIDE 2: El Problema ---
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide)
add_text_box(slide, Inches(0.8), Inches(0.5), Inches(11), Inches(0.8), "El Problema", font_size=40, color=WHITE, bold=True)
add_shape(slide, Inches(0.8), Inches(1.2), Inches(3), Inches(0.04), ACCENT)
add_card(slide, Inches(0.8), Inches(2), Inches(3.7), Inches(1.5), "Seguimiento manual imposible", "Miles de productos cambian de precio cada hora. Hacer tracking manual es inviable.")
add_card(slide, Inches(4.8), Inches(2), Inches(3.7), Inches(1.5), "Ofertas efimeras", "Las mejores ofertas duran minutos. Sin automatizacion, es imposible detectarlas a tiempo.")
add_card(slide, Inches(8.8), Inches(2), Inches(3.7), Inches(1.5), "3 plataformas, 1 problema", "Comparar Amazon + eBay + Mercado Libre simultaneamente es tedioso.")
add_text_box(slide, Inches(0.8), Inches(4.2), Inches(11), Inches(0.5), "Solucion: PricePulse AI automatiza todo en menos de 10 segundos", font_size=22, color=GREEN, bold=True, alignment=PP_ALIGN.CENTER)

# --- SLIDE 3: Stack Tecnologico ---
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide)
add_text_box(slide, Inches(0.8), Inches(0.5), Inches(11), Inches(0.8), "Stack Tecnologico", font_size=40, color=WHITE, bold=True)
add_shape(slide, Inches(0.8), Inches(1.2), Inches(3), Inches(0.04), ACCENT)
techs = [
    ("FastAPI", "API asincrona con auto-docs"),
    ("CrewAI", "Pipeline de 3 agentes IA"),
    ("NVIDIA NIM", "Llama 3.1 70B en GPU"),
    ("SerpAPI", "Precios de Amazon, eBay, ML"),
    ("n8n", "Orquestador + scheduler"),
    ("PostgreSQL", "Historial completo"),
    ("Streamlit", "Dashboard en vivo"),
    ("Docker", "Contenedores portables"),
]
for i, (name, desc) in enumerate(techs):
    col = i % 4
    row = i // 4
    left = Inches(0.8 + col * 3.1)
    top = Inches(2.0 + row * 2.5)
    add_card(slide, left, top, Inches(2.8), Inches(1.8), name, desc, title_size=22, body_size=13)

# --- SLIDE 4: Arquitectura ---
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide)
add_text_box(slide, Inches(0.8), Inches(0.5), Inches(11), Inches(0.8), "Arquitectura", font_size=40, color=WHITE, bold=True)
add_shape(slide, Inches(0.8), Inches(1.2), Inches(3), Inches(0.04), ACCENT)
boxes = [
    (Inches(0.3), Inches(2.2), Inches(3.8), "n8n Schedule", "00:00 / 08:00 / 16:00 UTC dispara el flujo"),
    (Inches(4.7), Inches(2.2), Inches(3.8), "SerpAPI", "Busca precios en Amazon, eBay y Mercado Libre"),
    (Inches(9.1), Inches(2.2), Inches(3.8), "CrewAI Agents", "3 agentes IA con NVIDIA NIM"),
]
for x, y, w, t, d in boxes:
    add_card(slide, x, y, w, Inches(1.5), t, d)
outs = [
    (Inches(0.3), Inches(4.5), Inches(2.8), "PostgreSQL", "Historial de precios"),
    (Inches(3.8), Inches(4.5), Inches(2.8), "Google Sheets", "Backup automatico"),
    (Inches(7.3), Inches(4.5), Inches(2.8), "Excel", "Exportacion .xlsx"),
    (Inches(10.8), Inches(4.5), Inches(2.0), "Dashboard", "Streamlit"),
]
for x, y, w, t, d in outs:
    add_card(slide, x, y, w, Inches(1.3), t, d, title_size=18, body_size=12)

# --- SLIDE 5: Flujo de precios ---
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide)
add_text_box(slide, Inches(0.8), Inches(0.5), Inches(11), Inches(0.8), "Flujo de Precios", font_size=40, color=WHITE, bold=True)
add_shape(slide, Inches(0.8), Inches(1.2), Inches(3), Inches(0.04), ACCENT)
add_text_box(slide, Inches(0.8), Inches(1.8), Inches(11), Inches(0.5), "Cada ejecucion busca hasta 20 precios (5 Amazon + 10 eBay + 5 ML), los 10 mejores van a CrewAI", font_size=18, color=GRAY, alignment=PP_ALIGN.CENTER)
cards_data = [
    (Inches(0.8), Inches(2.8), "Amazon", "engine=amazon\n5 resultados\nprecio + link limpio"),
    (Inches(4.8), Inches(2.8), "eBay", "Google Shopping filtrado por source=ebay\n10 resultados\nprecio + product link"),
    (Inches(8.8), Inches(2.8), "Mercado Libre", "Google site:mercadolibre.com\n5 resultados\nprecio via rich_snippet"),
]
for x, y, t, d in cards_data:
    add_card(slide, x, y, Inches(3.5), Inches(2.5), t, d)
add_text_box(slide, Inches(0.8), Inches(5.8), Inches(11), Inches(0.7), "Cache configurable (TTL 4h) + PostgreSQL persistente", font_size=18, color=ORANGE, alignment=PP_ALIGN.CENTER)

# --- SLIDE 6: 3 Agentes CrewAI ---
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide)
add_text_box(slide, Inches(0.8), Inches(0.5), Inches(11), Inches(0.8), "3 Agentes CrewAI", font_size=40, color=WHITE, bold=True)
add_shape(slide, Inches(0.8), Inches(1.2), Inches(3), Inches(0.04), ACCENT)
pipeline = [
    (Inches(0.8), Inches(2.2), "Captador de Datos", "* Extrae precio minimo, maximo, promedio\n* Identifica anomalias\n* Detecta mejor plataforma"),
    (Inches(4.8), Inches(2.2), "Organizador", "* Estructura en 4 secciones\n* Metricas, Comparativa, Anomalias, Recomendacion"),
    (Inches(8.8), Inches(2.2), "Redactor JSON", "* Genera JSON valido\n* Sin markdown, sin texto extra\n* 9 campos exactos"),
]
for x, y, t, d in pipeline:
    add_card(slide, x, y, Inches(3.5), Inches(2.8), t, d, title_size=22, body_size=14)
add_text_box(slide, Inches(0.8), Inches(5.5), Inches(11), Inches(0.5), "Temperatura: 0 | Verbose: false | NVIDIA NIM Llama 3.1 70B", font_size=16, color=GRAY, alignment=PP_ALIGN.CENTER)

# --- SLIDE 7: Dashboard ---
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide)
add_text_box(slide, Inches(0.8), Inches(0.5), Inches(11), Inches(0.8), "Dashboard en Vivo", font_size=40, color=WHITE, bold=True)
add_shape(slide, Inches(0.8), Inches(1.2), Inches(3), Inches(0.04), ACCENT)
features = [
    (Inches(0.8), Inches(2.0), "Metricas", "Precios registrados, productos, plataformas, ultimo registro"),
    (Inches(4.8), Inches(2.0), "Graficos", "Promedio por plataforma, tendencias historicas"),
    (Inches(8.8), Inches(2.0), "Filtros", "Por producto, plataforma y rango de fechas"),
    (Inches(0.8), Inches(3.8), "Tabla detallada", "Links directos a cada oferta, precios formateados"),
    (Inches(4.8), Inches(3.8), "Rapido", "Lee directo de la API (no Google Sheets)"),
    (Inches(8.8), Inches(3.8), "Docker", "Corre dentro del contenedor API (Python 3.11)"),
]
for x, y, t, d in features:
    add_card(slide, x, y, Inches(3.5), Inches(1.5), t, d, title_size=20, body_size=13)

# --- SLIDE 8: Resultados ---
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide)
add_text_box(slide, Inches(0.8), Inches(0.5), Inches(11), Inches(0.8), "Resultados Reales", font_size=40, color=WHITE, bold=True)
add_shape(slide, Inches(0.8), Inches(1.2), Inches(3), Inches(0.04), ACCENT)
results = [
    (Inches(0.8), Inches(2.0), "34+ precios por ejecucion", "Amazon + eBay + Mercado Libre simultaneamente"),
    (Inches(4.8), Inches(2.0), "< 10 segundos", "Desde POST hasta JSON con analisis IA completo"),
    (Inches(8.8), Inches(2.0), "Costo $0/mes", "Todo en tiers gratuitos (NVIDIA NIM + SerpAPI)"),
]
for x, y, t, d in results:
    add_card(slide, x, y, Inches(3.5), Inches(1.5), t, d, title_size=20, body_size=14)
add_card(slide, Inches(0.8), Inches(4.2), Inches(11.5), Inches(2.5), "Demo: Raspberry Pi 5",
    'POST /analizar-precios\n'
    '{"producto": "Raspberry Pi 5", "plataformas": ["amazon", "ebay", "mercadolibre"]}\n\n'
    "Respuesta: 16 precios en Amazon (desde $86), 8 en eBay, metricas IA + veredicto",
    title_size=22, body_size=14)

# --- SLIDE 9: Roadmap ---
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide)
add_text_box(slide, Inches(0.8), Inches(0.5), Inches(11), Inches(0.8), "Roadmap", font_size=40, color=WHITE, bold=True)
add_shape(slide, Inches(0.8), Inches(1.2), Inches(3), Inches(0.04), ACCENT)
add_card(slide, Inches(0.8), Inches(2.0), Inches(5.5), Inches(4.0), "Completado",
    "* 3 agentes CrewAI + NVIDIA NIM\n"
    "* Amazon, eBay, Mercado Libre\n"
    "* Dashboard Streamlit\n"
    "* n8n scheduler + Google Sheets\n"
    "* Docker Compose\n"
    "* Exportar PDF\n"
    "* PostgreSQL persistente\n"
    "* Cloudflare tunnel HTTPS",
    title_color=GREEN, title_size=22, body_size=14)
add_card(slide, Inches(6.8), Inches(2.0), Inches(5.5), Inches(4.0), "Proximos",
    "* Alertas Telegram\n"
    "* Prediccion tendencias ML\n"
    "* Autenticacion JWT\n"
    "* Tests automatizados\n"
    "* Multi-idioma\n"
    "* Mas e-commerce (AliExpress)\n"
    "* Web scraping fallback\n"
    "* Modo oscuro dashboard",
    title_color=ORANGE, title_size=22, body_size=14)

# --- SLIDE 10: Cierre ---
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide)
add_shape(slide, Inches(0), Inches(3.2), Inches(13.333), Inches(0.06), ACCENT)
add_text_box(slide, Inches(1), Inches(1.5), Inches(11), Inches(1.2), "Gracias", font_size=54, color=WHITE, bold=True, alignment=PP_ALIGN.CENTER)
add_text_box(slide, Inches(1), Inches(3.6), Inches(11), Inches(0.8), "github.com/AndresF-GaleanoT/pricepulse-ai", font_size=26, color=ACCENT, alignment=PP_ALIGN.CENTER)
add_text_box(slide, Inches(1), Inches(4.6), Inches(11), Inches(0.6), "Hecho con Python, NVIDIA NIM, CrewAI y mucho cafe", font_size=18, color=GRAY, alignment=PP_ALIGN.CENTER)

prs.save("PricePulse_AI_Presentation.pptx")
print("Presentacion generada: PricePulse_AI_Presentation.pptx")
