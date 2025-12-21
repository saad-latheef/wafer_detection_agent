"""
PDF Report Generator for Wafer Analysis.
Generates comprehensive PDF reports for lot-level and individual wafer analysis.
"""
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from io import BytesIO
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

def generate_wafer_report_pdf(lot_data, wafer_analyses):
    """
    Generate a PDF report for a lot of wafers.
    
    Args:
        lot_data: Dictionary containing lot-level statistics
        wafer_analyses: List of wafer analysis results
    
    Returns:
        BytesIO buffer containing the PDF
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=18)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#00d4ff'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#00d4ff'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    # Title
    title = Paragraph("Wafer Analysis Report", title_style)
    elements.append(title)
    
    # Metadata
    metadata_text = f"""
    <b>Generated:</b> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}<br/>
    <b>Total Wafers:</b> {lot_data.get('total_wafers', 0)}<br/>
    <b>Defective Wafers:</b> {lot_data.get('defective_wafers', 0)}<br/>
    <b>Yield Rate:</b> {lot_data.get('yield_rate', 0):.2f}%
    """
    elements.append(Paragraph(metadata_text, styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Lot Summary Section
    elements.append(Paragraph("Lot-Level Summary", heading_style))
    
    # Create yield chart
    fig, ax = plt.subplots(figsize=(6, 4))
    pass_count = lot_data.get('total_wafers', 0) - lot_data.get('defective_wafers', 0)
    fail_count = lot_data.get('defective_wafers', 0)
    
    ax.pie([pass_count, fail_count], labels=['Pass', 'Fail'],
           colors=['#00d4ff', '#ff0055'], autopct='%1.1f%%',
           startangle=90)
    ax.set_title('Yield Distribution')
    
    # Save chart to buffer
    chart_buffer = BytesIO()
    plt.savefig(chart_buffer, format='png', dpi=150, bbox_inches='tight')
    chart_buffer.seek(0)
    plt.close()
    
    # Add chart to PDF
    chart_img = Image(chart_buffer, width=4*inch, height=3*inch)
    elements.append(chart_img)
    elements.append(Spacer(1, 20))
    
    # Defect Pattern Distribution
    if 'defect_distribution' in lot_data and lot_data['defect_distribution']:
        elements.append(Paragraph("Defect Pattern Distribution", heading_style))
        
        defect_data = [['Pattern', 'Count', 'Percentage']]
        total = lot_data.get('total_wafers', 1)
        for pattern, count in sorted(lot_data['defect_distribution'].items(), 
                                     key=lambda x: x[1], reverse=True):
            percentage = (count / total * 100) if total > 0 else 0
            defect_data.append([pattern, str(count), f"{percentage:.1f}%"])
        
        defect_table = Table(defect_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
        defect_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#00d4ff')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(defect_table)
        elements.append(PageBreak())
    
    # Individual Wafer Results
    elements.append(Paragraph("Individual Wafer Analysis", heading_style))
    
    for idx, wafer in enumerate(wafer_analyses[:10], 1):  # Limit to first 10
        wafer_data = [
            ['Wafer ID', wafer.get('waferId', 'N/A')],
            ['File Name', wafer.get('fileName', 'N/A')],
            ['Verdict', wafer.get('finalVerdict', 'N/A')],
            ['Confidence', f"{wafer.get('confidence', 0):.1f}%"],
            ['Severity', wafer.get('severity', 'N/A')],
        ]
        
        wafer_table = Table(wafer_data, colWidths=[2*inch, 4*inch])
        wafer_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ]))
        
        elements.append(wafer_table)
        elements.append(Spacer(1, 10))
        
        if idx >= 10:
            elements.append(Paragraph(f"...and {len(wafer_analyses) - 10} more wafers", styles['Italic']))
            break
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer
