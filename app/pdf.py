from datetime import datetime
from fpdf import FPDF


def generar_pdf(producto: str, precios: list, reporte: str):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 20)
    pdf.cell(0, 15, "PricePulse AI - Reporte", ln=True, align="C")
    pdf.ln(5)

    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 10, f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True)
    pdf.cell(0, 10, f"Producto: {producto}", ln=True)
    pdf.ln(5)

    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "Precios encontrados:", ln=True)
    pdf.set_font("Helvetica", "", 10)

    for p in precios:
        pdf.cell(0, 7, f"  - {p.get('plataforma', 'N/A')}: ${p.get('precio', 'N/A')} | {p.get('titulo', 'N/A')}", ln=True)

    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "Reporte IA:", ln=True)
    pdf.set_font("Helvetica", "", 10)

    for line in reporte.split("\n"):
        pdf.multi_cell(0, 7, line.encode("latin-1", "replace").decode("latin-1"))

    return pdf.output()
