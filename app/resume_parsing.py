import streamlit as st
import fitz  # PyMuPDF
import io
import re

def extract_clean_text(bytes_data):
    doc = fitz.open(stream=bytes_data, filetype="pdf")
    # Extract text from each page
    text = "\n".join([page.get_text() for page in doc])
    #cleaning the txt
    info = clean_text(text)
    return info 
def clean_text(text):
    # Remove extra spaces, line breaks, and special characters
    text = re.sub(r'\s+', ' ', text)         # Remove extra whitespace
    text = re.sub(r'[^\x00-\x7F]+', '', text) # Remove non-ASCII
    info = extract_info(text.strip(),tech_skills)
    return info

def extract_email(text):
    match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    return match.group() if match else None

def extract_phone(text):
    match = re.search(r"(\+91[\-\s]?)?[789]\d{9}", text)
    return match.group() if match else None

def extract_links(text):
    links = re.findall(r"(https?://[^\s]+)", text)
    linkedin = next((url for url in links if 'linkedin' in url.lower()), None)
    github = next((url for url in links if 'github' in url.lower()), None)
    return linkedin, github


def extract_name(text):
    # Regular expression to find capitalized words (assuming names are capitalized)
    name_pattern = r"\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)*\b"
    matches = re.findall(name_pattern, text)

    # Returning the first match as the most likely candidate
    return matches[0] if matches else None



def extract_skills(text, skill_list):
    text_lower = text.lower()
    found = set()
    for skill in skill_list:
        if re.search(rf'\b{re.escape(skill.lower())}\b', text_lower):
            found.add(skill.lower())
    return list(found)

tech_skills = """
python
java
c++
javascript
typescript
html
css
sql
mongodb
mysql
postgresql
firebase
react
angular
vue
node.js
express
django
flask
spring boot
git
github
docker
kubernetes
aws
azure
gcp
linux
tensorflow
keras
pytorch
scikit-learn
pandas
numpy
opencv
matplotlib
seaborn
hadoop
spark
airflow
bash
rest api
graphql
redis
postgres
jupyter
vs code
tableau
power bi
bigquery
fastapi
langchain
transformers
huggingface
llm
prompt engineering
fine-tuning
streamlit
gradio
cv2
beautifulsoup
selenium
api integration
""".strip().split('\n')

def extract_info(text, skills_list):
    return {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "linkedin": extract_links(text)[0],
        "github": extract_links(text)[1],
        "skills": extract_skills(text, tech_skills),
    }

