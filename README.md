# Job FAQ Chatbot Backend

A semantic FAQ chatbot backend using FastAPI, sentence-transformers (MiniLM), and spaCy. This backend matches user questions to a dynamic list of FAQs using semantic similarity and provides accurate, context-aware answers. The FAQ data is loaded from a JSON file for easy updates and future integration with databases like Supabase.

---

## Features

- **Semantic FAQ Matching:** Uses BERT (all-MiniLM-L6-v2) for high-accuracy question matching.
- **Preprocessing:** Utilizes spaCy for lemmatization and stopword removal.
- **Dynamic FAQs:** FAQs are loaded from a JSON file (`faqs.json`).
- **REST API:** Exposes a `/ask` endpoint for chatbot integration.
- **Fallback Responses:** Returns a default message if no FAQ matches above the similarity threshold.

---

## File Structure

```
.
├── main.py           # FastAPI app with /ask endpoint
├── model.py          # FAQMatcher class (BERT + spaCy logic)
├── faqs.json         # Dynamic FAQ data
├── requirements.txt  # Python dependencies
└── README.md         # Project documentation
```

---

## Setup Instructions

### 1. Clone the Repository

```
git clone <your-repo-url>
cd job-faq-chatbot
```

### 2. Create and Activate a Virtual Environment

```
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 4. Run the FastAPI Server

```
uvicorn main:app --reload
```

The server will be available at `http://127.0.0.1:8000`.

---

## Usage

### API Endpoint: `/ask`

- **Method:** POST
- **Request Body:**
  ```json
  { "question": "How do I reset my password?" }
  ```
- **Response:**
  - If a match is found:
    ```json
    {
      "answer": "Click on 'Forgot password' at login and follow the instructions sent to your email.",
      "score": 0.89,
      "matched": true
    }
    ```
  - If no match is found:
    ```json
    {
      "answer": "Sorry, I couldn't find an answer to your question. Please contact support.",
      "score": 0.45,
      "matched": false
    }
    ```

### Example with `curl`:

```
curl -X POST "http://127.0.0.1:8000/ask" -H "Content-Type: application/json" -d '{"question": "How do I reset my password?"}'
```

---

## Customizing FAQs

- Edit `faqs.json` to add, remove, or update FAQ entries.
- Each entry should have a `question` and an `answer` field.
- Restart the server after modifying `faqs.json` to reload the data.

---

## How It Works

- User question is preprocessed (lemmatized, stopwords removed) using spaCy.
- Both user question and FAQ questions are embedded using BERT (MiniLM).
- Cosine similarity is computed between the user question and all FAQ questions.
- The answer with the highest similarity above the threshold (default 0.7) is returned.
- If no match is above the threshold, a fallback message is returned.

---

## Future Directions

- **Supabase Integration:** Replace `faqs.json` with dynamic database queries.
- **Admin Panel:** Add UI for managing FAQs.
- **Job Matching:** Extend backend to support job recommendations.
- **Frontend Integration:** Connect with a Next.js chatbot UI.

---

## License

MIT
