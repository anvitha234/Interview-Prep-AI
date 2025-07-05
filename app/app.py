import streamlit as st
import json
import os
from dotenv import load_dotenv
import google.generativeai as genai
from elevenlabs import generate, save, set_api_key
from elevenlabs import Client
import speech_recognition as sr
import tempfile
import wave
import pyaudio
import numpy as np
import time
from jobrole_prediction import predict_job_role
from resume_parsing import extract_resume_info
from Interview_evaluation import generate_report_pdf
import base64

load_dotenv()

# Configure Gemini
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# Configure ElevenLabs
ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
if ELEVENLABS_API_KEY:
    set_api_key(ELEVENLABS_API_KEY)

# Initialize Gemini model
if GEMINI_API_KEY:
    model = genai.GenerativeModel('gemini-1.5-flash')

# Initialize ElevenLabs client
if ELEVENLABS_API_KEY:
    client = Client(api_key=ELEVENLABS_API_KEY)

# Page config
st.set_page_config(
    page_title="AI Interview Bot",
    page_icon="🤖",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        color: #1f77b4;
    }
    .sidebar-button {
        background-color: #1f77b4 !important;
        color: white !important;
        border: none !important;
        padding: 0.5rem 1rem !important;
        border-radius: 5px !important;
        margin: 0.5rem 0 !important;
        width: 100% !important;
    }
    .voice-button {
        background-color: #28a745 !important;
        color: white !important;
        border: none !important;
        padding: 0.75rem 1rem !important;
        border-radius: 5px !important;
        margin: 0.5rem 0 !important;
        width: 100% !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 0.5rem !important;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .assistant-message {
        background-color: #f3e5f5;
        border-left: 4px solid #9c27b0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'interview_started' not in st.session_state:
    st.session_state.interview_started = False
if 'candidate_info' not in st.session_state:
    st.session_state.candidate_info = {}

def load_chat_history():
    """Load chat history from file"""
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        filename = os.path.join(current_dir, 'chat_history.json')
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                return json.load(f)
    except Exception as e:
        st.error(f"Error loading chat history: {e}")
    return []

def save_chat_history(history):
    """Save chat history to file"""
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        filename = os.path.join(current_dir, 'chat_history.json')
        with open(filename, 'w') as f:
            json.dump(history, f, indent=2)
    except Exception as e:
        st.error(f"Error saving chat history: {e}")

def clear_chat_history():
    """Clear chat history"""
    st.session_state.chat_history = [{"role": "assistant", "content": "Chat history cleared! Click 'Start Interview' to begin a new session."}]
    save_chat_history(st.session_state.chat_history)
    st.session_state.interview_started = False

def start_interview():
    """Start a new interview"""
    if not GEMINI_API_KEY:
        st.error("Please set your GEMINI_API_KEY in the .env file")
        return
    
    # Get candidate info
    name = st.session_state.get('candidate_name', '')
    job_role = st.session_state.get('predicted_role', '')
    experience = st.session_state.get('experience_level', '')
    skills = st.session_state.get('extracted_skills', [])
    
    # Create candidate info
    candidate_info = {
        "name": name,
        "job_role": job_role,
        "experience": experience,
        "skills": skills
    }
    st.session_state.candidate_info = candidate_info
    
    # Initialize interview
    interview_prompt = f"""
    You are a professional technical interviewer conducting an interview for a {job_role} position.
    
    Candidate Information:
    - Name: {name}
    - Target Role: {job_role}
    - Experience Level: {experience}
    - Skills: {', '.join(skills) if skills else 'Not specified'}
    
    Conduct a professional technical interview. Ask relevant technical questions based on the role and skills.
    Keep your responses concise and professional. Ask one question at a time and wait for the candidate's response.
    
    Start by introducing yourself and asking the first technical question.
    """
    
    if model:
        response = model.generate_content(interview_prompt)
        initial_message = response.text
        
        st.session_state.chat_history = [
            {"role": "assistant", "content": initial_message}
        ]
        st.session_state.interview_started = True
        save_chat_history(st.session_state.chat_history)

def generate_response(user_input):
    """Generate AI response based on conversation context"""
    if not GEMINI_API_KEY or not model:
        return "Error: Gemini API not configured"
    
    # Build conversation context
    conversation = ""
    for msg in st.session_state.chat_history[-5:]:  # Last 5 messages for context
        conversation += f"{msg['role'].upper()}: {msg['content']}\n"
    conversation += f"USER: {user_input}\n"
    
    prompt = f"""
    You are a professional technical interviewer. Continue the interview based on the conversation context.
    
    Previous conversation:
    {conversation}
    
    Provide a professional response that continues the interview. Ask follow-up questions, provide feedback, or ask new technical questions as appropriate.
    Keep responses concise and professional.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating response: {e}"

def text_to_speech(text):
    """Convert text to speech using ElevenLabs"""
    if not ELEVENLABS_API_KEY:
        return None
    
    try:
        # Use a professional voice ID (you can change this)
        voice_id = "21m00Tcm4TlvDq8ikWAM"  # Rachel voice
        
        audio = client.text_to_speech.convert(
            text=text,
            voice_id=voice_id,
            model_id="eleven_monolingual_v1"
        )
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
            tmp_file.write(audio)
            return tmp_file.name
    except Exception as e:
        st.error(f"Text-to-speech error: {e}")
        return None

def speech_to_text():
    """Convert speech to text"""
    recognizer = sr.Recognizer()
    
    with sr.Microphone() as source:
        st.info("Listening... Speak now!")
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            text = recognizer.recognize_google(audio)
            return text
        except sr.WaitTimeoutError:
            st.error("No speech detected. Please try again.")
            return None
        except sr.UnknownValueError:
            st.error("Could not understand audio. Please try again.")
            return None
        except Exception as e:
            st.error(f"Speech recognition error: {e}")
            return None

# Main UI
st.markdown('<h1 class="main-header">AI Interview Bot</h1>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("Controls")
    
    # API Key Status
    st.subheader("API Status")
    if GEMINI_API_KEY:
        st.success("✅ Gemini API Configured")
    else:
        st.error("❌ Gemini API Key Missing")
    
    if ELEVENLABS_API_KEY:
        st.success("✅ ElevenLabs API Configured")
    else:
        st.error("❌ ElevenLabs API Key Missing")
    
    st.divider()
    
    # Resume Upload
    st.subheader("Resume Upload")
    uploaded_file = st.file_uploader("Upload Resume (PDF)", type=['pdf'])
    
    if uploaded_file is not None:
        with st.spinner("Analyzing resume..."):
            resume_info = extract_resume_info(uploaded_file)
            if resume_info:
                st.session_state.candidate_name = resume_info.get('name', '')
                st.session_state.extracted_skills = resume_info.get('skills', [])
                
                # Predict job role
                predicted_role = predict_job_role(resume_info.get('text', ''))
                st.session_state.predicted_role = predicted_role
                
                st.success(f"Resume analyzed! Predicted role: {predicted_role}")
    
    st.divider()
    
    # Interview Controls
    st.subheader("Interview Controls")
    
    if st.button("Start Interview", key="start_btn", use_container_width=True):
        start_interview()
    
    if st.button("End Interview", key="end_btn", use_container_width=True):
        st.session_state.interview_started = False
        st.success("Interview ended!")
    
    if st.button("Clear History", key="clear_btn", use_container_width=True):
        clear_chat_history()
        st.success("Chat history cleared!")
    
    st.divider()
    
    # Analysis
    st.subheader("Analysis")
    
    if st.button("Get Analysis", key="analysis_btn", use_container_width=True):
        if not GEMINI_API_KEY:
            st.error("Gemini API key required for analysis")
        else:
            with st.spinner("Generating analysis..."):
                try:
                    from Interview_evaluation import save_and_evaluate
                    save_and_evaluate(GEMINI_API_KEY)
                    st.success("Analysis completed! Check the generated markdown file.")
                except Exception as e:
                    st.error(f"Analysis failed: {e}")
    
    # PDF Report
    if st.button("Generate PDF Report", key="pdf_btn", use_container_width=True):
        if not GEMINI_API_KEY:
            st.error("Gemini API key required for PDF generation")
        else:
            with st.spinner("Generating PDF report..."):
                try:
                    pdf_bytes = generate_report_pdf(GEMINI_API_KEY, st.session_state.candidate_info)
                    if pdf_bytes:
                        # Create download button
                        st.download_button(
                            label="Download PDF Report",
                            data=pdf_bytes,
                            file_name="interview_report.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                        st.success("PDF report generated successfully!")
                    else:
                        st.error("Failed to generate PDF report. Please ensure you have completed an interview.")
                except Exception as e:
                    st.error(f"PDF generation failed: {e}")

# Main chat area
col1, col2 = st.columns([3, 1])

with col1:
    st.subheader("Interview Chat")
    
    # Display chat history
    for message in st.session_state.chat_history:
        if message['role'] == 'user':
            st.markdown(f'<div class="chat-message user-message"><strong>You:</strong> {message["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-message assistant-message"><strong>Interviewer:</strong> {message["content"]}</div>', unsafe_allow_html=True)
    
    # Input area
    if st.session_state.interview_started:
        user_input = st.text_input("Your response:", key="user_input", placeholder="Type your answer here...")
        
        col_a, col_b = st.columns([1, 1])
        
        with col_a:
            if st.button("Send", key="send_btn", use_container_width=True):
                if user_input.strip():
                    # Add user message
                    st.session_state.chat_history.append({"role": "user", "content": user_input})
                    
                    # Generate AI response
                    ai_response = generate_response(user_input)
                    st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
                    
                    # Save to file
                    save_chat_history(st.session_state.chat_history)
                    
                    # Clear input
                    st.rerun()
        
        with col_b:
            if st.button("🎤 Voice Input", key="voice_btn", use_container_width=True):
                voice_text = speech_to_text()
                if voice_text:
                    st.session_state.chat_history.append({"role": "user", "content": voice_text})
                    
                    # Generate AI response
                    ai_response = generate_response(voice_text)
                    st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
                    
                    # Save to file
                    save_chat_history(st.session_state.chat_history)
                    
                    # Text-to-speech for AI response
                    if ELEVENLABS_API_KEY:
                        audio_file = text_to_speech(ai_response)
                        if audio_file:
                            with open(audio_file, 'rb') as f:
                                audio_bytes = f.read()
                            st.audio(audio_bytes, format='audio/mp3')
                            os.unlink(audio_file)  # Clean up
                    
                    st.rerun()
    else:
        st.info("Click 'Start Interview' in the sidebar to begin!")

with col2:
    st.subheader("Candidate Info")
    
    # Manual input fields
    name = st.text_input("Name:", value=st.session_state.get('candidate_name', ''), key="name_input")
    if name:
        st.session_state.candidate_name = name
    
    role = st.text_input("Job Role:", value=st.session_state.get('predicted_role', ''), key="role_input")
    if role:
        st.session_state.predicted_role = role
    
    experience = st.selectbox(
        "Experience Level:",
        ["Entry Level", "Mid Level", "Senior Level", "Expert"],
        index=0 if not st.session_state.get('experience_level') else ["Entry Level", "Mid Level", "Senior Level", "Expert"].index(st.session_state.get('experience_level')),
        key="exp_input"
    )
    st.session_state.experience_level = experience
    
    # Display extracted skills
    if st.session_state.get('extracted_skills'):
        st.write("**Skills from Resume:**")
        for skill in st.session_state.extracted_skills[:5]:  # Show first 5 skills
            st.write(f"• {skill}")

# Load chat history on startup
if not st.session_state.chat_history:
    st.session_state.chat_history = load_chat_history() 