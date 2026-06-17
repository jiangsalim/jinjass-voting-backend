import io
from openpyxl import Workbook
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

def export_excel(election_title, results):
    """Generate Excel file from results"""
    wb = Workbook()
    ws = wb.active
    ws.title = "Election Results"
    
    ws.append([election_title])
    ws.append([])
    
    for position, candidates in results.items():
        ws.append([position])
        ws.append(['Rank', 'Candidate', 'Votes'])
        for c in candidates:
            ws.append([c['rank'], c['candidate_name'], c['votes']])
        ws.append([])
    
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output


def export_pdf(election_title, results):
    """Generate PDF file from results"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []
    
    elements.append(Paragraph(election_title, styles['Title']))
    
    for position, candidates in results.items():
        elements.append(Paragraph(f"<br/>{position}", styles['Heading2']))
        
        data = [['Rank', 'Candidate', 'Votes']]
        for c in candidates:
            data.append([str(c['rank']), c['candidate_name'], str(c['votes'])])
        
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(table)
    
    doc.build(elements)
    buffer.seek(0)
    return buffer