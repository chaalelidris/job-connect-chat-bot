import json
import spacy
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

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
        similarities = cosine_similarity(user_embedding, self.question_embeddings)[0]
        best_idx = int(np.argmax(similarities))
        best_score = similarities[best_idx]
        if best_score >= threshold:
            return self.answers[best_idx], float(best_score)
        else:
            return None, float(best_score) 