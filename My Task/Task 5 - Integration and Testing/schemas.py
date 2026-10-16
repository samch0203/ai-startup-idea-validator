from typing import Any
from pydantic import BaseModel, Field, ConfigDict


class IdeaSubmission(BaseModel):
    """Raw form input submitted by the user."""
    model_config = ConfigDict(str_strip_whitespace=True)

    idea_description: str = Field(..., min_length=20, max_length=5000)
    industry: str = Field(..., min_length=2, max_length=120)
    target_customers: str = Field(..., min_length=2, max_length=500)
    location: str = Field(default="India", min_length=2, max_length=120)
    budget: str = Field(default="Not specified", max_length=120)
    relevant_details: str = Field(default="", max_length=2000)


class StructuredIdea(BaseModel):
    name: str = "Untitled Startup"
    problem_statement: str
    proposed_solution: str
    target_customers: str
    industry: str
    key_features: list[str] = Field(default_factory=list)
    original_description: str
    location: str = "India"
    budget: str = "Not specified"
    relevant_details: str = ""


class SearchFinding(BaseModel):
    category: str
    query: str
    title: str
    url: str
    content: str
    score: float | None = None


class SearchReport(BaseModel):
    queries: dict[str, str]
    market_results: list[SearchFinding]
    competitor_results: list[SearchFinding]
    total_results: int
    live_search: bool
    message: str


class AgentAnalysis(BaseModel):
    market_analysis: dict[str, Any]
    competitor_analysis: dict[str, Any]
    swot_and_risks: dict[str, Any]
    mvp_recommendation: dict[str, Any]
    final_summary: str


class ValidationReport(BaseModel):
    structured_idea: StructuredIdea
    search_report: SearchReport
    analysis: AgentAnalysis
