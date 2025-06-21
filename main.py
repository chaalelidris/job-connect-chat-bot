from fastapi import FastAPI
from pydantic import BaseModel
from model import FAQMatcher

app = FastAPI()
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