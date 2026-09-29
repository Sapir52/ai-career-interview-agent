"""Small smoke tests for the deterministic analysis and interview flows."""
from analysis_engine import deterministic_analysis
from ai import interview

CV = "Python Vue Firebase Google Cloud Gemini OpenAI machine learning NLP computer vision"
JOB = "Nexora Labs AI Native Software Engineer. Python AWS SQL system design LLM Docker."

def test_analysis():
    result = deterministic_analysis(CV, JOB)
    assert result.company == "Nexora Labs"
    assert result.matchScore >= 55
    assert "Python" in result.strongSkills

def test_interview_mock():
    result = interview("Tell me about your backend", "I built APIs with Python.")
    assert result.feedback.score >= 0
    assert result.followUp
