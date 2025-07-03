import markdown
from weasyprint import HTML
from io import BytesIO
import streamlit as st


def markdown_to_pdf(markdown_text):
    """
    Convert markdown text to PDF with proper styling.
    """
    try:
        # Validate input
        if not markdown_text or not isinstance(markdown_text, str):
            return None
            
        # Convert markdown to HTML
        html_content = markdown.markdown(markdown_text, extensions=['extra', 'codehilite'])
        
        # Add CSS styling for better PDF appearance
        css_styles = """
        <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
        }
        h1 {
            font-size: 2.5em;
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
        h2 {
            font-size: 2em;
            color: #34495e;
            border-bottom: 2px solid #ecf0f1;
            padding-bottom: 8px;
            margin-top: 30px;
            margin-bottom: 15px;
        }
        h3 {
            font-size: 1.5em;
            color: #34495e;
            margin-top: 25px;
            margin-bottom: 10px;
        }
        h4 {
            font-size: 1.3em;
            color: #34495e;
            margin-top: 20px;
            margin-bottom: 8px;
        }
        h5, h6 {
            font-size: 1.1em;
            color: #34495e;
            margin-top: 15px;
            margin-bottom: 5px;
        }
        p {
            margin-bottom: 12px;
            text-align: justify;
        }
        ul, ol {
            margin-bottom: 15px;
            padding-left: 30px;
        }
        li {
            margin-bottom: 5px;
        }
        blockquote {
            border-left: 4px solid #3498db;
            padding-left: 20px;
            margin: 20px 0;
            font-style: italic;
            background-color: #f8f9fa;
            padding: 15px 20px;
        }
        code {
            background-color: #f1f2f6;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }
        pre {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid #3498db;
            overflow-x: auto;
            margin: 15px 0;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
            font-weight: bold;
        }
        strong {
            color: #2c3e50;
        }
        em {
            color: #7f8c8d;
        }
        .page-break {
            page-break-before: always;
        }
        </style>
        """
        
        # Combine CSS and HTML
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Rapport Compilé</title>
            {css_styles}
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """
        
        # Generate PDF
        pdf_buffer = BytesIO()
        HTML(string=full_html).write_pdf(pdf_buffer)
        pdf_buffer.seek(0)
        
        return pdf_buffer.getvalue()
    
    except Exception as e:
        # Only show streamlit error if st is available and imported properly
        try:
            st.error(f"Erreur lors de la génération du PDF: {str(e)}")
        except:
            pass  # Silently fail if streamlit isn't available
        return None 