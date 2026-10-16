import os
from fastapi.testclient import TestClient

os.environ["USE_MOCKS"] = "true"

from app.main import app
from app.schemas import IdeaSubmission
from app.services.idea_extraction import extract_structured_idea
from app.services.web_search import search_startup_idea
from app.orchestrator import run_validation_workflow

client = TestClient(app)

SAMPLES = [
    IdeaSubmission(
        idea_description="An app that connects restaurants with customers to sell surplus food at lower prices.",
        industry="Food Technology", target_customers="Restaurants and budget-conscious consumers", location="Pune, India"
    ),
    IdeaSubmission(
        idea_description="A platform that helps small clinics send appointment reminders and manage patient queues.",
        industry="Healthcare Technology", target_customers="Small clinics and patients", location="India"
    ),
    IdeaSubmission(
        idea_description="A service that helps apartment residents track electricity usage and reduce energy waste.",
        industry="Clean Energy", target_customers="Apartment residents and housing societies", location="Maharashtra, India"
    ),
]


def test_three_sample_ideas_complete_mock_workflow():
    for submission in SAMPLES:
        idea = extract_structured_idea(submission)
        assert idea.problem_statement
        assert idea.proposed_solution
        assert idea.industry == submission.industry
        assert isinstance(idea.key_features, list)
        search = search_startup_idea(idea)
        assert set(search.queries) == {"market_trends", "customer_problems", "competitors"}
        assert search.total_results >= 1
        assert search.live_search is False
        report = run_validation_workflow(submission)
        assert report.structured_idea.target_customers == submission.target_customers
        assert report.analysis.final_summary


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_validation_endpoint():
    response = client.post("/api/validate", json=SAMPLES[0].model_dump())
    assert response.status_code == 200
    data = response.json()
    assert "structured_idea" in data
    assert "search_report" in data
    assert "analysis" in data


def test_required_fields_validation():
    response = client.post("/api/validate", json={"industry": "Food Tech"})
    assert response.status_code == 422
