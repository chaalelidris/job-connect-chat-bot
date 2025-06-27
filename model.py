import spacy
from sentence_transformers import SentenceTransformer
import numpy as np
import pdfplumber
import docx
from supabase import create_client, Client
import os
from typing import Optional
import json

# =========================
# FAQ MATCHER
# =========================
class FAQMatcher:
    def __init__(self, faq_path="faqs.json"):
        self.faq_path = faq_path
        self.faqs = self.load_faqs()
        self.nlp = spacy.load("en_core_web_sm", disable=["ner", "parser"])
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.questions = [faq["question"] for faq in self.faqs]
        self.answers = [faq["answer"] for faq in self.faqs]
        self.question_embeddings = self.encode_questions(self.questions)

    def load_faqs(self):
        with open(self.faq_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def preprocess(self, text):
        doc = self.nlp(text.lower())
        tokens = [token.lemma_ for token in doc if not token.is_stop and not token.is_punct]
        return " ".join(tokens)

    def encode_questions(self, questions):
        processed = [self.preprocess(q) for q in questions]
        return self.model.encode(processed)

    def match(self, user_question, threshold=0.7):
        user_processed = self.preprocess(user_question)
        user_embedding = self.model.encode([user_processed])
        similarities = np.dot(self.question_embeddings, user_embedding[0])
        best_idx = int(np.argmax(similarities))
        best_score = similarities[best_idx]
        if best_score >= threshold:
            return self.answers[best_idx], float(best_score)
        else:
            return None, float(best_score)

# =========================
# RESUME ANALYZER
# =========================
# Load NLP models for resume analysis
nlp = spacy.load("en_core_web_sm")
bert_model = SentenceTransformer('all-MiniLM-L6-v2')

def extract_text_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        return " ".join([page.extract_text() for page in pdf.pages if page.extract_text()])

def extract_text_from_docx(docx_path):
    doc = docx.Document(docx_path)
    return " ".join([para.text for para in doc.paragraphs])

def extract_skills(text):
    doc = nlp(text)
    # Use spaCy NER for skills (custom NER can be added for better results)
    skills = [ent.text for ent in doc.ents if ent.label_ == "SKILL"]
    return list(set(skills))

def analyze_resume(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        text = extract_text_from_pdf(file_path)
    elif ext == ".docx":
        text = extract_text_from_docx(file_path)
    else:
        raise ValueError("Unsupported file type")
    skills = extract_skills(text)
    return {
        "text": text,
        "skills": skills
    }

# =========================
# JOB MATCHER
# =========================
# Supabase setup
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Optional[Client] = None
if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_embedding(text):
    return bert_model.encode([text])[0]

def fetch_jobs_from_supabase():
    if not supabase:
        return []
    response = supabase.table("jobs").select("id, title, description, requirements").execute()
    return response.data if response.data else []

def find_matching_jobs(cv_text, top_n=5, threshold=0.4):
    jobs = fetch_jobs_from_supabase()
    if not jobs:
        return []
    cv_embedding = get_embedding(cv_text)
    # Compute job embeddings and similarities
    for job in jobs:
        job_embedding = get_embedding(job.get("description", ""))
        job["similarity"] = float(np.dot(cv_embedding, job_embedding))
    # Filter by threshold
    jobs_filtered = [job for job in jobs if job["similarity"] >= threshold]
    # Sort by similarity
    jobs_sorted = sorted(jobs_filtered, key=lambda x: x["similarity"], reverse=True)
    return jobs_sorted[:top_n] 