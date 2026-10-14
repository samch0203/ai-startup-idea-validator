from typing import Any
from pydantic import BaseModel, Field


class StartupIdea(BaseModel):
    name: str = Field(..., min_length=2, description="Startup name")
    description: str = Field(..., min_length=10)
    target_market: str = Field(..., min_length=2)
    industry: str = Field(..., min_length=2)
    location: str = "India"
    budget: str = "Not specified"


class SearchResult(BaseModel):
    title: str
    url: str
    content: str


class ValidationReport(BaseModel):
    startup_idea: StartupIdea
    market_analysis: dict[str, Any]
    competitor_analysis: dict[str, Any]
    swot_and_risks: dict[str, Any]
    mvp_recommendation: dict[str, Any]
    sources: list[SearchResult]
    final_summary: str

