"""AI provider abstraction for analysis and mock-interview evaluation.

The module supports a deterministic free mock mode, local Ollama, and optional
Amazon Bedrock while keeping the rest of the backend provider-independent.
"""
from __future__ import annotations
import json
import os
import httpx
import boto3
from analysis_engine import deterministic_analysis
from models import Analysis, Feedback, InterviewTurn

# Provider is selected through configuration so no frontend code needs to change.
PROVIDER = os.getenv("AI_PROVIDER", "mock").lower()

def _extract_json(text: str) -> dict:
    # Models may wrap JSON in markdown; normalize the response before validation.
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:]
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end < 0:
        raise ValueError("Model did not return JSON")
    return json.loads(text[start:end+1])

def _ollama(prompt: str) -> str:
    url = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434").rstrip("/") + "/api/generate"
    payload = {"model": os.getenv("OLLAMA_MODEL", "llama3.2:3b"), "prompt": prompt, "stream": False, "format": "json"}
    with httpx.Client(timeout=90) as client:
        response = client.post(url, json=payload)
        response.raise_for_status()
        return response.json()["response"]

def _bedrock(prompt: str) -> str:
    client = boto3.client("bedrock-runtime", region_name=os.getenv("AWS_REGION", "us-east-1"))
    response = client.converse(
        modelId=os.getenv("BEDROCK_MODEL_ID", "amazon.nova-lite-v1:0"),
        messages=[{"role": "user", "content": [{"text": prompt}]}],
        inferenceConfig={"maxTokens": 1800, "temperature": 0.2},
    )
    return "".join(part.get("text", "") for part in response.get("output", {}).get("message", {}).get("content", []))

def call_model(prompt: str) -> str | None:
    # Return None in mock mode so callers use the deterministic free fallback.
    if PROVIDER == "ollama":
        return _ollama(prompt)
    if PROVIDER == "bedrock":
        return _bedrock(prompt)
    return None

def analyze(cv: str, job: str) -> Analysis:
    # Always build a valid fallback first; external model output can safely override it.
    fallback = deterministic_analysis(cv, job)
    raw = call_model(
        "You are a career interview preparation engine. Return ONLY valid JSON matching this object shape:\n"
        + fallback.model_dump_json()
        + "\nAnalyze the CV and job description. Scores are 0-100. Do not invent experience.\nCV:\n"
        + cv + "\nJOB:\n" + job
    )
    if not raw:
        return fallback
    try:
        merged = fallback.model_dump() | _extract_json(raw) | {"id": fallback.id}
        return Analysis.model_validate(merged)
    except Exception:
        return fallback

def interview(question: str, answer: str, analysis: Analysis | None = None) -> InterviewTurn:
    # Produce useful feedback even when no external LLM is configured.
    missing = analysis.missingSkills if analysis else []
    fallback = InterviewTurn(
        question=question,
        feedback=Feedback(
            score=8,
            technicalAccuracy=8,
            clarity=7,
            depth=7,
            relevance=9,
            strengths=["Clear structure", "Relevant technical context"],
            improvements=["Add a concrete trade-off", "Mention monitoring and failure handling"],
            suggestedAnswer=answer + " I would also explain the trade-offs, failure modes, observability and how the design scales.",
        ),
        followUp=(
            "How would you redesign this solution using AWS Lambda, S3 and DynamoDB?"
            if "AWS" in missing else
            "What trade-offs did you consider, and how would this design change at 100x traffic?"
        ),
    )
    raw = call_model(
        "Evaluate this interview answer. Return ONLY valid JSON matching this shape: "
        + fallback.model_dump_json()
        + "\nRole context: " + json.dumps(analysis.model_dump() if analysis else {})
        + "\nQuestion: " + question + "\nAnswer: " + answer
    )
    if not raw:
        return fallback
    try:
        merged = fallback.model_dump() | _extract_json(raw) | {"question": question}
        return InterviewTurn.model_validate(merged)
    except Exception:
        return fallback
