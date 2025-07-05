import streamlit as st
import speech_recognition as sr
import os
import time



def transcribe_audio(audio_file_path):
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(audio_file_path) as source:
            audio_data = recognizer.record(source)
            try:
                return recognizer.recognize_google(audio_data)
            except sr.UnknownValueError:
                return "[Could not understand audio]"
            except sr.RequestError:
                return "[API unavailable]"
    except Exception as e:
        st.error(f"Error processing audio: {str(e)}")
        return None

