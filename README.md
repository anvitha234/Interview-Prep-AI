# AI Interview Bot - NLP Pipeline

An intelligent interview system demonstrating comprehensive Natural Language Processing techniques for resume analysis, job prediction, and automated interviews.

## NLP Pipeline

### 1. Text Processing
- **PDF Extraction**: PyMuPDF for resume text extraction
- **Preprocessing**: NLTK tokenization, stop word removal, lemmatization
- **Vectorization**: TF-IDF feature extraction

### 2. Information Extraction
- **NER**: Regex-based name, email, phone extraction
- **Skill Matching**: 50+ technical skills detection
- **URL Detection**: LinkedIn/GitHub profile extraction

### 3. Classification
- **Model**: LinearSVC with TF-IDF features
- **Classes**: 42 job roles (Data Science, DevOps, etc.)
- **Output**: Top-2 role predictions with confidence scores

### 4. Conversational AI
- **LLM**: Google Gemini 1.5 Flash
- **Context**: JSON-based conversation history
- **Prompting**: Role-specific interview generation

### 5. Speech Processing
- **STT**: Google Speech Recognition
- **TTS**: ElevenLabs API
- **Real-time**: Audio input/output processing

### 6. Evaluation
- **Analysis**: Gemini-based conversation evaluation
- **Scoring**: Technical, Communication, Problem-solving (0-10)
- **Output**: PDF reports with recommendations

## Quick Start

### Prerequisites
- Python 3.8+
- API Keys: Google Gemini, ElevenLabs.


Generate 2 API keys from these 2 sites:
https://aistudio.google.com/app/apikey
https://elevenlabs.io/app/settings/api-keys


### Installation
```bash
# Clone repository
git clone https://github.com/anvitha234/Interview-Prep-AI
cd Interview-Prep-AI

# Setup environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install streamlit google-generativeai elevenlabs speechrecognition pyaudio PyMuPDF nltk scikit-learn reportlab python-dotenv

# Download NLTK data
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet')"
```

### Environment Setup - 
Create `.env` file:
```env
GEMINI_API_KEY=your_gemini_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key
```

### Run Application
```bash
cd app
streamlit run app.py
```

## Usage

1. **Upload Resume**: PDF file for automatic analysis
2. **Start Interview**: AI generates role-specific questions
3. **Conduct Interview**: Text or voice responses
4. **Get Evaluation**: AI analysis and PDF report
