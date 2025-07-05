# jobrole_prediction.py

import nltk
import re
import pickle
import fitz  # PyMuPDF
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Download NLTK data (can be skipped after first run)
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

# Initialize
stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

# Job label list
y_list = [
    'Accountant', 'Advocate', 'Agriculture', 'Apparel', 'Architecture',
    'Arts', 'Automobile', 'Aviation', 'Banking', 'Blockchain', 'BPO',
    'Building and Construction', 'Business Analyst', 'Civil Engineer',
    'Consultant', 'Data Science', 'Database', 'Designing', 'DevOps',
    'Digital Media', 'DotNet Developer', 'Education',
    'Electrical Engineering', 'ETL Developer', 'Finance',
    'Food and Beverages', 'Health and Fitness', 'Human Resources',
    'Information Technology', 'Java Developer', 'Management',
    'Mechanical Engineer', 'Network Security Engineer',
    'Operations Manager', 'PMO', 'Public Relations',
    'Python Developer', 'React Developer', 'Sales', 'SAP Developer',
    'SQL Developer', 'Testing', 'Web Designing'
]

# Path config
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(current_dir, "model.pkl")
VEC_PATH = os.path.join(current_dir, "tfidf_vectorizer.pkl")

def preprocess_text(text):
    text = re.sub(r'[^a-zA-Z ]', ' ', text).lower()
    tokens = word_tokenize(text)
    tokens = [lemmatizer.lemmatize(word) for word in tokens if word not in stop_words]
    return ' '.join(tokens)

def load_model_and_vectorizer():
    with open(MODEL_PATH, 'rb') as f_model, open(VEC_PATH, 'rb') as f_vec:
        model = pickle.load(f_model)
        vectorizer = pickle.load(f_vec)
    return model, vectorizer

def extract_text_from_pdf(file_bytes):
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    text = "\n".join([page.get_text() for page in doc])
    return text

def predict(file_bytes):
    try:
        text = extract_text_from_pdf(file_bytes)
        cleaned = preprocess_text(text)
        model, vectorizer = load_model_and_vectorizer()
        X_new = vectorizer.transform([cleaned])
        
        # Get decision function scores for all classes
        decision_scores = model.decision_function(X_new)[0]
        
        # Get top 2 predictions based on decision scores
        top_indices = decision_scores.argsort()[-2:][::-1]  # Get indices of top 2
        top_jobs = [y_list[i] for i in top_indices]
        top_scores = [decision_scores[i] for i in top_indices]
        
        # Format the result as a proper sentence
        best_match = top_jobs[0]
        second_best = top_jobs[1]
        
        result = f"Based on your resume, you are best suited for **{best_match}** position. Other possible roles include **{second_best}**."
        
        return result
    except Exception as e:
        return f"Prediction failed: {e}"
