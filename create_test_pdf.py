#!/usr/bin/env python3
"""
Create a test PDF document for testing the PDF summary functionality
"""

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    print("✅ reportlab is available")
except ImportError:
    print("❌ reportlab not available. Installing...")
    import subprocess
    subprocess.check_call(["pip", "install", "reportlab"])
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch

def create_test_pdf():
    """Create a test PDF document."""
    filename = "test_document.pdf"
    
    # Create PDF document
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Create custom style
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        alignment=1  # Center alignment
    )
    
    # Content
    content = []
    
    # Title
    content.append(Paragraph("AI and Machine Learning Research Report", title_style))
    content.append(Spacer(1, 20))
    
    # Executive Summary
    content.append(Paragraph("Executive Summary", styles['Heading2']))
    content.append(Paragraph(
        "This comprehensive report examines the current state of artificial intelligence and machine learning technologies, "
        "their applications across various industries, and future trends. The research is based on analysis of recent "
        "developments, industry reports, and expert interviews conducted over the past six months.",
        styles['Normal']
    ))
    content.append(Spacer(1, 12))
    
    # Key Findings
    content.append(Paragraph("Key Findings", styles['Heading2']))
    findings = [
        "AI adoption has increased by 300% in the past two years across all major industries",
        "Machine learning models are becoming 40% more efficient while maintaining accuracy",
        "Natural language processing capabilities have improved significantly with transformer architectures",
        "Computer vision applications are expanding rapidly in healthcare, automotive, and retail sectors",
        "Edge computing is bringing AI capabilities to mobile and IoT devices"
    ]
    
    for finding in findings:
        content.append(Paragraph(f"• {finding}", styles['Normal']))
        content.append(Spacer(1, 6))
    
    # Technical Analysis
    content.append(Paragraph("Technical Analysis", styles['Heading2']))
    content.append(Paragraph(
        "The technical landscape of AI has evolved dramatically with the introduction of transformer architectures, "
        "which have revolutionized natural language processing. Deep learning models now achieve state-of-the-art "
        "performance on a wide range of tasks, from image recognition to language translation.",
        styles['Normal']
    ))
    content.append(Spacer(1, 12))
    
    content.append(Paragraph(
        "GPU acceleration has been crucial in enabling faster model training and inference. Modern AI systems "
        "can process vast amounts of data in real-time, making them suitable for production environments. "
        "Federated learning approaches are addressing privacy concerns while maintaining model performance.",
        styles['Normal']
    ))
    content.append(Spacer(1, 12))
    
    # Recommendations
    content.append(Paragraph("Recommendations", styles['Heading2']))
    recommendations = [
        "Invest in AI talent acquisition and training programs for existing employees",
        "Implement robust data governance frameworks to ensure data quality and privacy",
        "Focus on ethical AI development practices and bias mitigation",
        "Consider hybrid cloud architectures for AI workloads to balance performance and cost",
        "Establish partnerships with AI research institutions and technology providers"
    ]
    
    for rec in recommendations:
        content.append(Paragraph(f"• {rec}", styles['Normal']))
        content.append(Spacer(1, 6))
    
    # Conclusion
    content.append(Paragraph("Conclusion", styles['Heading2']))
    content.append(Paragraph(
        "The future of artificial intelligence looks exceptionally promising with continued innovation in algorithms, "
        "hardware, and applications. Organizations that invest strategically in AI capabilities today will be "
        "well-positioned to capitalize on the AI-driven transformation of their industries. The key to success "
        "lies in balancing technological advancement with ethical considerations and practical implementation.",
        styles['Normal']
    ))
    
    # Build PDF
    doc.build(content)
    print(f"✅ Created test PDF: {filename}")
    return filename

if __name__ == "__main__":
    create_test_pdf()
