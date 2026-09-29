"""Deterministic CV-to-job matching engine used by the free/mock AI mode.

It extracts known skills, detects transferable experience, calculates a match
score, and creates interview and learning-plan recommendations without an API.
"""
from __future__ import annotations
import re
import uuid
from models import Analysis, Skill, LearningItem

# Portfolio-sized vocabulary used for deterministic skill extraction.
KNOWN = [
    "Python", "JavaScript", "TypeScript", "React", "Vue", "Node.js", "AWS", "Lambda", "S3",
    "DynamoDB", "SQS", "SQL", "Docker", "Kubernetes", "System Design", "REST", "GraphQL", "LLM",
    "RAG", "OpenAI", "Gemini", "Firebase", "Google Cloud", "Machine Learning", "NLP", "Computer Vision"
]

ALIASES: dict[str, list[str]] = {
    "AWS": ["aws", "amazon web services"],
    "Lambda": ["lambda", "serverless"],
    "S3": ["s3", "object storage"],
    "DynamoDB": ["dynamodb", "nosql"],
    "SQS": ["sqs", "queue", "message queue"],
    "SQL": ["sql", "postgres", "postgresql", "mysql"],
    "LLM": ["llm", "large language model", "openai", "gemini", "bedrock"],
    "RAG": ["rag", "retrieval augmented generation", "embeddings", "vector"],
    "System Design": ["system design", "architecture", "scalability", "distributed"],
    "Machine Learning": ["machine learning", "ml"],
    "Google Cloud": ["google cloud", "gcp"],
    "Node.js": ["node.js", "nodejs", "node "],
}

def has(text: str, skill: str) -> bool:
    # Match canonical skill names through common aliases and related terminology.
    low = text.lower()
    return any(alias in low for alias in ALIASES.get(skill, [skill.lower()]))

def clean_role(job: str) -> str:
    for line in job.splitlines():
        if re.search(r"engineer|developer|software|backend|\bai\b", line, re.I):
            return line.strip()[:80]
    return "AI Native Software Engineer"

def deterministic_analysis(cv: str, job: str) -> Analysis:
    # Compare requested job skills with CV evidence and classify each requirement.
    cv_skills = [skill for skill in KNOWN if has(cv, skill)]
    job_skills = [skill for skill in KNOWN if has(job, skill)]
    demanded = job_skills or ["Python", "AWS", "LLM", "System Design", "SQL", "Docker"]

    skills: list[Skill] = []
    for name in demanded[:12]:
        if name in cv_skills:
            skills.append(Skill(name=name, score=92, status="strong"))
            continue
        transferable = (
            (name == "AWS" and (has(cv, "Google Cloud") or has(cv, "Firebase")))
            or (name == "React" and has(cv, "Vue"))
            or (name == "DynamoDB" and has(cv, "Firebase"))
        )
        skills.append(Skill(name=name, score=62 if transferable else 35, status="partial" if transferable else "missing"))

    strong = [s.name for s in skills if s.status == "strong"]
    missing = [s.name for s in skills if s.status == "missing"]
    partial = [s.name for s in skills if s.status == "partial"]
    denominator = max(1, len(skills))
    match = round((len(strong) + len(partial) * 0.55) / denominator * 100)
    match = max(55, match)

    return Analysis(
        id=str(uuid.uuid4()),
        matchScore=match,
        readiness=max(52, min(92, match - 4)),
        role=clean_role(job),
        company="Nexora Labs" if "nexora labs" in job.lower() else "Target Company",
        strongSkills=strong,
        missingSkills=missing,
        transferableSkills=partial,
        skills=skills,
        insights=[
            "Your AI and software engineering background maps well to the role.",
            f"Transferable experience can help bridge: {', '.join(partial)}." if partial else "Most core requirements are already represented in your CV.",
            f"Prioritize interview preparation for: {', '.join(missing[:3])}." if missing else "Focus on depth, trade-offs and system design explanations.",
        ],
        interviewFocus=list(dict.fromkeys(["AI/LLM Integration", "System Design", "Backend Architecture", *missing[:2]])),
        learningPlan=[
            LearningItem(topic="AWS Fundamentals", priority="High" if "AWS" in missing else "Medium", lessons=["IAM basics", "Lambda", "API Gateway", "S3", "DynamoDB", "CloudWatch"]),
            LearningItem(topic="System Design", priority="High", lessons=["scalability", "queues", "caching", "idempotency", "observability"]),
            LearningItem(topic="LLM Engineering", priority="Medium", lessons=["structured outputs", "RAG", "evaluation", "guardrails", "cost/latency trade-offs"]),
            LearningItem(topic="SQL & Data", priority="High" if "SQL" in missing else "Low", lessons=["joins", "indexes", "transactions", "schema design"]),
        ],
    )
