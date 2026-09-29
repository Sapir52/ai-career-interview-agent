"""Pydantic request/response models shared by the Python API and AI layer."""
from typing import Literal
from pydantic import BaseModel, Field

SkillStatus = Literal["strong", "partial", "missing"]
Priority = Literal["High", "Medium", "Low"]

class Skill(BaseModel):
    name: str
    score: int = Field(ge=0, le=100)
    status: SkillStatus

class LearningItem(BaseModel):
    topic: str
    priority: Priority
    lessons: list[str]

class Analysis(BaseModel):
    id: str
    matchScore: int
    readiness: int
    role: str
    company: str
    strongSkills: list[str]
    missingSkills: list[str]
    transferableSkills: list[str]
    skills: list[Skill]
    insights: list[str]
    interviewFocus: list[str]
    learningPlan: list[LearningItem]

class Feedback(BaseModel):
    score: int = Field(ge=0, le=10)
    technicalAccuracy: int = Field(ge=0, le=10)
    clarity: int = Field(ge=0, le=10)
    depth: int = Field(ge=0, le=10)
    relevance: int = Field(ge=0, le=10)
    strengths: list[str]
    improvements: list[str]
    suggestedAnswer: str

class InterviewTurn(BaseModel):
    question: str
    feedback: Feedback
    followUp: str

class AnalyzeRequest(BaseModel):
    cv: str
    job: str

class InterviewRequest(BaseModel):
    question: str
    answer: str
    analysis: Analysis | None = None

class ExtractCvRequest(BaseModel):
    filename: str = "cv.pdf"
    contentBase64: str
