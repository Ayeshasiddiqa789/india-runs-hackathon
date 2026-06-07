from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import csv
from pathlib import Path

CSV_PATH = Path(r"c:\Hackathon\submission_final.csv")
OUT_PDF = Path(r"c:\Hackathon\submission_final.pdf")


def read_csv(path):
    with path.open(newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)
    return rows


def build_pdf(rows, out_path):
    doc = SimpleDocTemplate(str(out_path), pagesize=landscape(A4), rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    styles = getSampleStyleSheet()
    story = []
    title = Paragraph('Ranked candidates — submission_final.csv', styles['Title'])
    story.append(title)
    story.append(Spacer(1, 12))

    # Prepare table data (ensure header repeated on every page)
    table = Table(rows, repeatRows=1)
    tbl_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E2E86')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
    ])
    table.setStyle(tbl_style)
    story.append(table)
    doc.build(story)


def main():
    if not CSV_PATH.exists():
        print(f"CSV not found: {CSV_PATH}")
        return
    rows = read_csv(CSV_PATH)
    if not rows:
        print("CSV is empty")
        return
    build_pdf(rows, OUT_PDF)
    print(f"Wrote PDF: {OUT_PDF}")


if __name__ == '__main__':
    main()
