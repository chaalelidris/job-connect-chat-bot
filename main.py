from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from model import FAQMatcher, analyze_resume
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

# Enable CORS for all origins and methods
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

faq_matcher = FAQMatcher(faq_path="faqs.json")

class AskRequest(BaseModel):
    question: str

class AskResponse(BaseModel):
    answer: str
    score: float
    matched: bool

@app.post("/ask", response_model=AskResponse)
async def ask_faq(req: AskRequest):
    answer, score = faq_matcher.match(req.question)
    if answer:
        return AskResponse(answer=answer, score=score, matched=True)
    else:
        return AskResponse(
            answer="Sorry, I couldn't find an answer to your question. Please contact support.",
            score=score,
            matched=False
        )

@app.post("/upload_resume")
async def upload_resume(file: UploadFile = File(...)):
    # Save uploaded file
    filename = file.filename or "resume.pdf"
    ext = os.path.splitext(filename)[1].lower()
    temp_path = f"temp_resume{ext}"
    with open(temp_path, "wb") as f:
        f.write(await file.read())
    # Analyze resume using the file path
    from model import find_matching_jobs
    resume_data = analyze_resume(temp_path)
    os.remove(temp_path)
    best_matches = find_matching_jobs(resume_data["text"])
    return {"resume_data": resume_data, "best_matches": best_matches} 