from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from io import BytesIO

async def generate_pdf(job_data):
    """
    Generate a PDF from job description data
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, 
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=18)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Get styles
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    heading_style = styles['Heading2']
    normal_style = styles['Normal']
    
    # Custom styles
    company_style = ParagraphStyle(
        'Company',
        parent=styles['Heading3'],
        textColor=colors.darkblue,
    )
    
    section_style = ParagraphStyle(
        'Section',
        parent=styles['Heading3'],
        textColor=colors.darkblue,
        spaceBefore=12,
        spaceAfter=6,
    )
    
    # Title
    elements.append(Paragraph(job_data.get("job_title", "Job Description"), title_style))
    elements.append(Spacer(1, 12))
    
    # Company information
    if job_data.get("company_name"):
        elements.append(Paragraph(f"Company: {job_data.get('company_name')}", company_style))
        elements.append(Spacer(1, 6))
    
    if job_data.get("company_location") or job_data.get("job_location"):
        location = job_data.get("company_location") or job_data.get("job_location", "")
        elements.append(Paragraph(f"Location: {location}", normal_style))
        elements.append(Spacer(1, 6))
    
    # Job details table
    job_details = []
    
    # Add job details if available
    if job_data.get("job_type"):
        job_details.append(["Job Type", job_data.get("job_type")])
    
    if job_data.get("salary"):
        job_details.append(["Salary", job_data.get("salary")])
    
    if job_data.get("job_category"):
        job_details.append(["Category", job_data.get("job_category")])
        
    if job_data.get("application_deadline"):
        job_details.append(["Application Deadline", job_data.get("application_deadline")])
    
    # Add job details table if we have entries
    if job_details:
        job_details_table = Table(job_details, colWidths=[100, 350])
        job_details_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(job_details_table)
        elements.append(Spacer(1, 12))
    
    # Job description
    if job_data.get("job_description"):
        elements.append(Paragraph("Job Description", section_style))
        elements.append(Paragraph(job_data.get("job_description"), normal_style))
        elements.append(Spacer(1, 12))
    
    # Responsibilities
    if job_data.get("job_responsibilities"):
        elements.append(Paragraph("Responsibilities", section_style))
        responsibilities = job_data.get("job_responsibilities")
        # Check if this is a string and try to format as bullet points if it contains line breaks
        if isinstance(responsibilities, str) and "\n" in responsibilities:
            for item in responsibilities.split("\n"):
                if item.strip():
                    elements.append(Paragraph(f"• {item.strip()}", normal_style))
        else:
            elements.append(Paragraph(responsibilities, normal_style))
        elements.append(Spacer(1, 12))
    
    # Skills
    if job_data.get("job_skills"):
        elements.append(Paragraph("Skills", section_style))
        skills = job_data.get("job_skills")
        # Check if this is a string and try to format as bullet points if it contains line breaks
        if isinstance(skills, str) and "\n" in skills:
            for item in skills.split("\n"):
                if item.strip():
                    elements.append(Paragraph(f"• {item.strip()}", normal_style))
        else:
            elements.append(Paragraph(skills, normal_style))
        elements.append(Spacer(1, 12))
    
    # Education and Experience
    if job_data.get("job_education") or job_data.get("job_experience"):
        elements.append(Paragraph("Education & Experience", section_style))
        if job_data.get("job_education"):
            elements.append(Paragraph(f"Education: {job_data.get('job_education')}", normal_style))
        if job_data.get("job_experience"):
            elements.append(Paragraph(f"Experience: {job_data.get('job_experience')}", normal_style))
        elements.append(Spacer(1, 12))
    
    # Benefits
    if job_data.get("job_benefits") or job_data.get("company_benefits"):
        elements.append(Paragraph("Benefits", section_style))
        benefits = job_data.get("job_benefits") or job_data.get("company_benefits", "")
        # Check if this is a string and try to format as bullet points if it contains line breaks
        if isinstance(benefits, str) and "\n" in benefits:
            for item in benefits.split("\n"):
                if item.strip():
                    elements.append(Paragraph(f"• {item.strip()}", normal_style))
        else:
            elements.append(Paragraph(benefits, normal_style))
        elements.append(Spacer(1, 12))
    
    # Company description
    if job_data.get("company_description"):
        elements.append(Paragraph("About the Company", section_style))
        elements.append(Paragraph(job_data.get("company_description"), normal_style))
        elements.append(Spacer(1, 12))
    
    # Company details (industry, size, website)
    company_details = []
    if job_data.get("company_industry"):
        company_details.append(["Industry", job_data.get("company_industry")])
    if job_data.get("company_size"):
        company_details.append(["Company Size", job_data.get("company_size")])
    if job_data.get("company_website"):
        company_details.append(["Website", job_data.get("company_website")])
    
    if company_details:
        company_details_table = Table(company_details, colWidths=[100, 350])
        company_details_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(company_details_table)
    
    # Build the PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer