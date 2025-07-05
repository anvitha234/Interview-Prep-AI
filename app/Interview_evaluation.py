import google.generativeai as genai
from dotenv import load_dotenv
import json
import os
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from datetime import datetime
import io

load_dotenv()


def generate_evaluation(history_file: str,api_key) -> str:

    with open(history_file, 'r') as f:
        history = json.load(f)
    
    # Check if there's actual interview data
    if len(history) <= 1 or (len(history) == 1 and "cleared" in history[0]['content'].lower()):
        return "No interview data available for evaluation. Please complete an interview first."
    
    # Filter out system messages and get actual conversation
    conversation_messages = []
    for msg in history:
        if msg['role'] in ['user', 'assistant'] and not any(keyword in msg['content'].lower() for keyword in ['cleared', 'start interview', 'end interview']):
            conversation_messages.append(msg)
    
    if len(conversation_messages) < 2:
        return "Insufficient interview data for evaluation. Please complete an interview with at least one question and answer exchange."
    
    # Prepare conversation history for analysis
    conversation = "\n".join(
        f"{msg['role'].upper()}: {msg['content']}" 
        for msg in conversation_messages
    )
    
    # Initialize Gemini
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    Analyze this technical interview conversation and provide:
    
    1. Brief overall assessment (1 paragraph)
    2. Technical knowledge score (0-10)
    3. Communication skills score (0-10)
    4. Problem-solving score (0-10)
    5. Top 3 specific improvement suggestions
    
    Format your response in Markdown with clear headings.
    
    Conversation:
    {conversation}
    """
    
    response = model.generate_content(prompt)
    return response.text

# Modified save function that also generates evaluation
def save_and_evaluate(api_key):
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(current_dir, 'chat_history.json')
    evaluation = generate_evaluation(filename,api_key)
    print("\n=== AI Evaluation ===")
    print(evaluation)
    
    # Also save evaluation to file
    eval_filename = os.path.join(current_dir, 'chat_history_eval.md')
    with open(eval_filename, 'w') as f:
        f.write(evaluation)
    print(f"Evaluation saved to {eval_filename}")


def generate_pdf_report(history_file: str, api_key, candidate_info=None) -> bytes:
    """Generate a comprehensive PDF report of the interview"""
    
    # Get the evaluation
    evaluation = generate_evaluation(history_file, api_key)
    
    # Check if evaluation indicates no data
    if "No interview data available" in evaluation or "Insufficient interview data" in evaluation:
        raise ValueError("No interview data available for PDF generation. Please complete an interview first.")
    
    # Create PDF buffer
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=1  # Center alignment
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        spaceBefore=20
    )
    
    # Build PDF content
    story = []
    
    # Title
    story.append(Paragraph("Interview Report", title_style))
    story.append(Spacer(1, 20))
    
    # Report metadata
    story.append(Paragraph(f"<b>Report Generated:</b> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", styles['Normal']))
    story.append(Spacer(1, 12))
    
    # Candidate information (if available)
    if candidate_info:
        story.append(Paragraph("Candidate Information", heading_style))
        candidate_data = [
            ["Name", candidate_info.get("name", "Not provided")],
            ["Job Role", candidate_info.get("job_role", "Not provided")],
            ["Experience Level", candidate_info.get("experience", "Not provided")],
            ["Skills", ", ".join(candidate_info.get("skills", [])) if candidate_info.get("skills") else "Not provided"]
        ]
        
        candidate_table = Table(candidate_data, colWidths=[2*inch, 4*inch])
        candidate_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.grey),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (1, 0), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(candidate_table)
        story.append(Spacer(1, 20))
    
    # Interview Summary
    story.append(Paragraph("Interview Summary", heading_style))
    
    # Parse the evaluation to extract scores
    lines = evaluation.split('\n')
    summary_text = ""
    scores = {}
    
    for line in lines:
        if "Technical knowledge score" in line:
            try:
                score = line.split('(')[1].split('-')[0].strip()
                scores['technical'] = score
            except:
                scores['technical'] = "N/A"
        elif "Communication skills score" in line:
            try:
                score = line.split('(')[1].split('-')[0].strip()
                scores['communication'] = score
            except:
                scores['communication'] = "N/A"
        elif "Problem-solving score" in line:
            try:
                score = line.split('(')[1].split('-')[0].strip()
                scores['problem_solving'] = score
            except:
                scores['problem_solving'] = "N/A"
        elif "Brief overall assessment" in line or "overall assessment" in line.lower():
            continue
        else:
            summary_text += line + " "
    
    # Add the evaluation text
    story.append(Paragraph(summary_text, styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Scores table
    if scores:
        story.append(Paragraph("Performance Scores", heading_style))
        scores_data = [
            ["Category", "Score (0-10)"],
            ["Technical Knowledge", scores.get('technical', 'N/A')],
            ["Communication Skills", scores.get('communication', 'N/A')],
            ["Problem Solving", scores.get('problem_solving', 'N/A')]
        ]
        
        scores_table = Table(scores_data, colWidths=[3*inch, 3*inch])
        scores_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(scores_table)
        story.append(Spacer(1, 20))
    
    # Recommendations
    story.append(Paragraph("Recommendations", heading_style))
    
    # Extract recommendations from evaluation
    recommendations = []
    in_recommendations = False
    for line in lines:
        if "improvement suggestions" in line.lower() or "recommendations" in line.lower():
            in_recommendations = True
            continue
        elif in_recommendations and line.strip():
            if line.strip().startswith(('1.', '2.', '3.', '-', '*')):
                recommendations.append(line.strip())
    
    if recommendations:
        for rec in recommendations:
            story.append(Paragraph(f"• {rec.lstrip('123.-* ')}", styles['Normal']))
            story.append(Spacer(1, 6))
    else:
        story.append(Paragraph("No specific recommendations available.", styles['Normal']))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

def generate_report_pdf(api_key, candidate_info=None):
    """Generate and return PDF report bytes"""
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(current_dir, 'chat_history.json')
    
    try:
        pdf_bytes = generate_pdf_report(filename, api_key, candidate_info)
        return pdf_bytes
    except ValueError as e:
        # This is the case when there's no interview data
        print(f"PDF generation failed: {e}")
        return None
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return None

