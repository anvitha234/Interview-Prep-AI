# 🤖 AI Interview Feedback Bot – Apps Directory

This folder contains the core logic and configuration files for the **AI Interview Feedback Bot**, an intelligent system that simulates job interviews, generates dynamic questions based on resumes, and provides automated feedback reports.

## 📂 Folder: `app/`

| File | Description |
|------|-------------|
| `app.py` | 🔁 **Main application entry point** – launches the Streamlit web interface for interacting with the interview bot. |
| `Interview_evaluation.py` | 📊 **Feedback engine** – evaluates candidate answers using sentiment analysis, keyword coverage, and coherence metrics. |
| `resume_parsing.py` | 📄 **Resume parser** – extracts text and features from uploaded resumes for role prediction and interview customization. |
| `model.pkl` | 🧠 **Job role prediction model** – trained machine learning model (likely Logistic Regression or similar) to classify job roles based on resume content. |
| `tfidf_vectorizer.pkl` | 🧮 **TF-IDF transformer** – text vectorizer used to preprocess resume inputs before feeding into the classifier. |
| `interviewer_personalities.json` | 🎭 **Dynamic interviewer profiles** – defines diverse AI personas (e.g., friendly, strict, analytical) for adaptive interview sessions. |
| `chat_historyjson` | 💬 **Chat transcript (JSON)** – stores past interview conversations for reloading and session continuity. |
| `chat_history_eval.md` | 📋 **Evaluation notes** – markdown file recording human/AI evaluation of past interview sessions (can be useful for debugging and improvements). |
| `requirements.txt` | ⚙️ **Dependencies list** – specifies all Python packages required to run the application in a reproducible environment (for `pip install -r requirements.txt`). |

---

## 🚀 Features Implemented
- Role-specific question generation using Gemini 1.5 Flash
- Voice input
- Resume-based dynamic interviews
- Containerized deployment with Docker
- PDF report generation for feedback

---

## 🛠️ Setup Instructions
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py

