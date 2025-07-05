import google.generativeai as genai
from dotenv import load_dotenv
import json
import random
import re
import requests
import base64
from io import BytesIO
import os
import streamlit as st
import elevenlabs
import io
import time
import tempfile
from audio_recorder_streamlit import audio_recorder
from io import StringIO
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

import Interview_evaluation
import stt
import resume_parsing
import jobrole_prediction

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

# 1. Configure the APIs
def setup_voice(api_key):
    # ElevenLabs API key is set globally
    pass

if "voice_id" not in st.session_state:
    st.session_state.voice_id = ""
# 2. Create the model instance
def get_model_name(personality,prompt,api_key):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        model_name='gemini-1.5-flash',  # or 'gemini-2.0-flash'
        system_instruction=prompt
    )
    return model


# Single professional interviewer configuration
def get_interviewer_config():
    return {
        "name": "AI Interviewer",
        "prompt": "You are a professional technical interviewer conducting a job interview. Ask relevant questions based on the candidate's background and the job role. Be professional, thorough, and fair in your assessment.",
        "voice_id": "21m00Tcm4TlvDq8ikWAM"  # Professional voice
    }

st.set_page_config(
    page_title="AI Interview Assistant",
    page_icon="",
    layout="centered"
)

# Custom CSS to change button colors to blue
st.markdown("""
<style>
    .stButton > button {
        background-color: #0068c9;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 0.5rem 1rem;
    }
    .stButton > button:hover {
        background-color: #0056b3;
    }
</style>
""", unsafe_allow_html=True)
# Initialize session state for messages
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! Shall we Start with interview?"}
    ]
if "chat" not in st.session_state:
    st.session_state.chat = None  # Set a default value

st.title("Welcome, Candidate!")
st.markdown(":blue[This is an **AI Interview Assistant** designed to help you prepare for your upcoming interviews.]")
def typewriter(text):
    for word in text.split():
        yield word + " "
        time.sleep(0.1)  # Adjust speed

if "voice_id" not in st.session_state:
    st.session_state.voice_id = ""

with st.sidebar:
    tab1, tab2,tab3= st.tabs(["Upload Resume", "Select Yourself","Controls"])

    with tab1:
        st.header("Upload Resume")
        uploaded_file = st.file_uploader("Choose a PDF file")
        setup_voice(ELEVENLABS_API_KEY)
        Experience = st.selectbox("Experience Level",("Entry-Level", "Mid-Level", "Senior-Level"),key = "Re")
        if uploaded_file is not None:
        # To read file as bytes:
            if st.button("Submit"):
                bytes_data = uploaded_file.getvalue()
                interviewer = get_interviewer_config()
                st.session_state.voice_id = interviewer["voice_id"]
                info = resume_parsing.extract_clean_text(bytes_data)
                job_prediction = jobrole_prediction.predict(bytes_data)
                
                # Extract the best match job role for the prompt (first job mentioned)
                import re
                best_match = re.search(r'\*\*(.*?)\*\*', job_prediction)
                Job_Role = best_match.group(1) if best_match else "Software Engineer"
                
                prompt = f"""{interviewer['prompt']}
                - Candidate Name: {info["name"]} applying for {Job_Role} position with {Experience} experience.
                - Candidate Skills: {info["skills"]}
                - Ask one question at a time, including Behavioral, Technical, and Cultural Fit questions.
                - Vary question types after 2-3 follow-up questions.
                - Wait for complete responses before proceeding.
                - Provide relevant follow-ups based on answers.
                - Keep responses concise (under 50 words when possible)."""
                # 3. Start the chat session
                st.session_state.chat = get_model_name(interviewer,prompt,GEMINI_API_KEY).start_chat(history=[])
                st.markdown(job_prediction)
                st.write(info)



    with tab2:
        st.header("Manual Information Entry")
        Name = st.text_input("Candidate Name", placeholder="Your Name")
        Job_Role = st.text_input("Job Role", placeholder="e.g., Software Engineer, Data Analyst, etc.")
        Experience = st.selectbox("Experience Level",("Entry-Level", "Mid-Level", "Senior-Level"),key = "manualexp")
        setup_voice(ELEVENLABS_API_KEY)
        if st.button("Start Interview",type = "primary"):
            if not Name or not Job_Role:
                st.markdown(":blue[Please fill in all required details!]")
            else:
                interviewer = get_interviewer_config()
                st.session_state.voice_id = interviewer["voice_id"]
                prompt = f"""{interviewer['prompt']}
                - Candidate Name: {Name} applying for {Job_Role} position with {Experience} experience.
                - Ask one question at a time, including Behavioral, Technical, and Cultural Fit questions.
                - Ask at least one follow-up question and maximum two follow-up questions.
                - Wait for complete responses before proceeding.
                - Provide relevant follow-ups based on answers.
                - Keep responses concise (under 50 words when possible)."""
                st.write(f"Interviewer: {interviewer['name']}")
                # 3. Start the chat session
                st.session_state.chat = get_model_name(interviewer,prompt,GEMINI_API_KEY).start_chat(history=[])
    with tab3:
        st.header("Chat Controls")
        
        # End Interview button
        if st.button("End Interview"):
            import os
            current_dir = os.path.dirname(os.path.abspath(__file__))
            file = os.path.join(current_dir, 'app', 'chat_history.json')
            # Ensure messages are JSON serializable
            messages_serializable = [{"role": msg["role"], "content": str(msg["content"])} for msg in st.session_state.messages]
            with open(file, 'w') as f:
                json.dump(messages_serializable, f)
            
            st.session_state.messages = [
                {"role": "assistant", "content": "Chat history cleared! Click 'Start Interview' to begin a new session."}
            ]
            st.rerun()
        
        # Get Analysis button
        if st.button("Get Analysis"):
            try:
                # Generate evaluation
                evaluate = Interview_evaluation.save_and_evaluate(GEMINI_API_KEY)
                
                # Read and display the evaluation
                import os
                current_dir = os.path.dirname(os.path.abspath(__file__))
                eval_path = os.path.join(current_dir, "app", "chat_history_eval.md")
                
                if os.path.exists(eval_path):
                    with open(eval_path, "r") as file:
                        content = file.read()
                    
                    if content.strip():
                        st.markdown("### Interview Analysis")
                        st.markdown(content)
                        
                        # Download as Markdown
                        st.download_button(
                            label="Download Analysis (Markdown)",
                            data=content,
                            file_name="interview_analysis.md",
                            mime="text/markdown"
                        )
                    else:
                        st.error("No analysis content found. Please ensure the interview has been completed.")
                else:
                    st.error("Analysis file not found. Please complete an interview first.")
                    
            except Exception as e:
                st.error(f"Error generating analysis: {str(e)}")
        
        # Download PDF Report button
        if st.button("Download PDF Report"):
            try:
                # Get candidate info from session state
                candidate_info = {
                    "name": st.session_state.get("candidate_name", "Not provided"),
                    "job_role": st.session_state.get("job_role", "Not provided"),
                    "experience": st.session_state.get("experience", "Not provided"),
                    "skills": st.session_state.get("skills", [])
                }
                
                # Generate PDF report
                from datetime import datetime
                pdf_bytes = Interview_evaluation.generate_report_pdf(GEMINI_API_KEY, candidate_info)
                
                if pdf_bytes:
                    st.download_button(
                        label="Download Interview Report PDF",
                        data=pdf_bytes,
                        file_name=f"interview_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf"
                    )
                else:
                    st.error("Failed to generate PDF report. Please ensure you have completed an interview.")
                    
            except Exception as e:
                st.error(f"Error generating PDF: {str(e)}")
        
        st.divider()



# Initialize session state for messages
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! Please start an interview by uploading a resume or filling in your details in the sidebar."}
    ]

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

def generate_audio(text):
    with st.spinner("Generating audio..."):                
        try:
            # Use the correct ElevenLabs API with client
            from elevenlabs import ElevenLabs, play
            
            # Create client with API key
            client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
            
            # Generate audio using text_to_speech method
            audio = client.text_to_speech.convert(
                text=text,
                voice_id=st.session_state.voice_id,
                model_id="eleven_multilingual_v2"
            )
            
            # Read audio bytes
            audio_bytes = b"".join(audio)
            
            # Convert audio to base64 for autoplay
            audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
            del audio_bytes
            
            # Create autoplay audio element
            audio_html = f"""
            <audio autoplay>
                <source src="data:audio/mpeg;base64,{audio_base64}" type="audio/mpeg">
                Your browser does not support the audio element.
            </audio>
            """
            st.markdown(audio_html, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Audio generation failed: {str(e)}")
            # Continue without audio if there's an error




def handle_message(input_text):
    # Add user message
    audio_bytes = None
    st.session_state.messages.append({"role": "user", "content": input_text})
    with st.chat_message("user"):
        st.markdown(input_text)
    
    # Generate bot response
    if st.session_state.chat:
        assistant_prompt = st.session_state.chat.send_message(f"Candidate response: {input_text}\n Ask an appropriate follow-up question or a new question")
        assistant_prompt = assistant_prompt.text
        generate_audio(assistant_prompt)
        with st.chat_message("assistant"):
            st.write_stream(typewriter(assistant_prompt))
        st.session_state.messages.append(
            {"role": "assistant", "content": assistant_prompt}
        )
    else:
        st.warning("Please start an interview first by uploading a resume or filling in your details in the sidebar.")



if prompt := st.chat_input("Type your response..."):
    # Handle text input
    handle_message(prompt)


if "last_audio_transcript" not in st.session_state:
    st.session_state.last_audio_transcript = None

audio_bytes = audio_recorder(pause_threshold=2.0, text="Click to Record", recording_color="#e8b62c", neutral_color="#6aa36f", icon_size="2x")

if audio_bytes:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
        temp_audio.write(audio_bytes)
        temp_path = temp_audio.name

    time.sleep(0.1)
    text = stt.transcribe_audio(temp_path)
    
    if text and text != st.session_state.last_audio_transcript:
        handle_message(text)
        st.session_state.last_audio_transcript = text

