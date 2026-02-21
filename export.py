import io
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, ListFlowable, ListItem, Image, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

def list_to_bullets(items, style):
    list_items = [ListItem(Paragraph(item, style)) for item in items]
    return ListFlowable(list_items, bulletType='bullet')

def generate_pdf_report(stats_df, etl_stats, health_score, figures=None, report_title="LuminaData Analytical Report"):
    """Generates a PDF report containing data health, stats, and visualizations."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    title_style.alignment = 1 # Center
    
    normal_style = styles['Normal']
    
    story = []
    
    # Title
    story.append(Paragraph(report_title, title_style))
    story.append(Spacer(1, 24))
    
    # Health Score
    story.append(Paragraph(f"<b>Data Health Score:</b> {health_score} / 100", styles['Heading2']))
    story.append(Paragraph("Score is penalized for missing values, duplicates, and outliers found in the raw data.", normal_style))
    story.append(Spacer(1, 12))
    
    # ETL Summary
    story.append(Paragraph("<b>Data Cleansing Summary:</b>", styles['Heading3']))
    story.append(list_to_bullets([
        f"Duplicates Removed: {etl_stats.get('duplicates_removed', 0)}",
        f"Missing Values Imputed: {etl_stats.get('missing_imputed', 0)}",
        f"Outliers Handled: {etl_stats.get('outliers_handled', 0)}"
    ], normal_style))
    story.append(Spacer(1, 24))
    
    # Stats Table
    story.append(Paragraph("<b>Descriptive Statistics:</b>", styles['Heading2']))
    story.append(Spacer(1, 12))
    
    if stats_df is not None and not stats_df.empty:
        # Convert DataFrame to list of lists for ReportLab Table
        data = [stats_df.columns.to_list()] + stats_df.round(2).astype(str).values.tolist()
        
        table = Table(data, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#00e6ff')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#444444')),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#333333'))
        ]))
        story.append(table)
    else:
        story.append(Paragraph("No numerical data available for statistics.", normal_style))
        
    story.append(Spacer(1, 24))

    # Visualizations
    if figures:
        story.append(Paragraph("<b>Visual Storytelling:</b>", styles['Heading2']))
        story.append(Spacer(1, 12))
        
        for item in figures:
            fig = item["fig"]
            interpretation = item["interpretation"]
            
            # Convert Plotly figure to an image byte stream
            img_bytes = fig.to_image(format="png", width=600, height=400, scale=2)
            img_stream = io.BytesIO(img_bytes)
            
            # Create a ReportLab Image (scale to fit page width)
            img = Image(img_stream, width=450, height=300)
            
            # Wrap the image and text in a KeepTogether to avoid page breaks in the middle of a figure
            block = []
            block.append(img)
            block.append(Spacer(1, 6))
            block.append(Paragraph(f"<i>Insight Engine:</i> {interpretation}", normal_style))
            block.append(Spacer(1, 24))
            
            story.append(KeepTogether(block))
            
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
