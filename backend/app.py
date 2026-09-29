"""FastAPI entry point for CareerAgent AI.

Defines the public REST API used by the React frontend and exposes the same
application through Mangum so it can run inside AWS Lambda.
"""
from __future__ import annotations
import os
from dotenv import load_dotenv
load_dotenv()  # Load local .env values; Lambda uses environment variables directly.

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from ai import analyze, interview
from models import AnalyzeRequest, ExtractCvRequest, InterviewRequest
from pdf_service import extract_pdf_text
from store import get, put

# Create one ASGI app that works both locally with Uvicorn and in AWS Lambda.
app = FastAPI(title="CareerAgent AI API", version="2.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=False,
    allow_methods=["*"], allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"ok": True, "language": "python", "provider": os.getenv("AI_PROVIDER", "mock")}

# Extract selectable text from an uploaded base64-encoded PDF.
@app.post("/cv/extract")
def extract_cv(req: ExtractCvRequest):
    try:
        text, s3_key = extract_pdf_text(req.filename, req.contentBase64)
        return {"text": text, "s3Key": s3_key}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

# Run CV/job matching, then persist the structured result for later retrieval.
@app.post("/analyze")
def run_analysis(req: AnalyzeRequest):
    if not req.cv.strip() or not req.job.strip():
        raise HTTPException(status_code=400, detail="cv and job are required")
    result = analyze(req.cv, req.job)
    put(result.id, "analysis", result.model_dump())
    return result

@app.get("/analysis/{analysis_id}")
def load_analysis(analysis_id: str):
    result = get(analysis_id, "analysis")
    if result is None:
        raise HTTPException(status_code=404, detail="not found")
    return result

# Evaluate one interview answer and generate the next adaptive follow-up question.
@app.post("/interview/evaluate")
def evaluate_interview(req: InterviewRequest):
    if not req.question.strip() or not req.answer.strip():
        raise HTTPException(status_code=400, detail="question and answer are required")
    return interview(req.question, req.answer, req.analysis)

# AWS Lambda handler: API Gateway events are translated into ASGI requests by Mangum.
handler = Mangum(app, lifespan="off")
