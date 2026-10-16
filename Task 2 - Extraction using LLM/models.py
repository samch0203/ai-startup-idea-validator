"""
Pydantic Data Models for Startup Idea Submission and Multi-Agent Orchestration.
Project: AI Startup Idea Validator (Task 2 Update)
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class RawStartupSubmission(BaseModel):
    """Raw input received from user interface submission form."""
    startup_name: Optional[str] = Field(default="My Startup", description="Startup or product name")
    description: str = Field(..., description="Raw description of the startup idea and core problem")
    target_customers: Optional[str] = Field(default="", description="Target audience or user segment")
    industry: Optional[str] = Field(default="", description="Industry or primary market sector")
    geography: Optional[str] = Field(default="Global", description="Geographic focus")
    monetization_hypothesis: Optional[str] = Field(default=None, description="Proposed business model")
    known_competitors: Optional[str] = Field(default=None, description="Competitors recognized by the founder")


class StructuredIdeaOutput(BaseModel):
    """
    Standardized schema required by Task 2:
    - problem_statement
    - proposed_solution
    - target_customers
    - industry
    - key_features
    """
    idea_name: Optional[str] = Field(default="Startup Idea", description="Name or title of the startup")
    problem_statement: str = Field(..., description="Core problem or pain point identified")
    proposed_solution: str = Field(..., description="The proposed product or solution addressing the problem")
    target_customers: str = Field(..., description="Primary user archetype or customer segment")
    industry: str = Field(..., description="Primary industry or business sector")
    key_features: List[str] = Field(..., description="List of key capabilities, features, or components")
    
    # Metadata and reliability fields
    extraction_source: str = Field(default="LLM", description="Source of extraction: 'LLM_GEMINI', 'LLM_OPENAI', or 'FALLBACK_RULE_BASED'")
    status: str = Field(default="success", description="Status of the extraction: 'success' or 'partial'")


class CustomerPersona(BaseModel):
    """Structured customer persona profile for downstream agents."""
    role: str = Field(..., description="Primary title or archetype of the decision maker / buyer")
    firmographic: str = Field(..., description="Company size, revenue, fleet count, or demographics")
    core_pain_point: str = Field(..., description="Primary friction or acute headache experienced")
    urgency_level: str = Field(..., description="'High (Painkiller)', 'Medium (Efficiency)', or 'Low (Vitamin)'")


class StructuredStartupIdea(BaseModel):
    """Complete representation used across the multi-agent pipeline."""
    idea_id: str = Field(..., description="Unique session identifier")
    idea_name: str = Field(..., description="Normalized startup name")
    tagline: str = Field(..., description="One-sentence elevator pitch")
    primary_industry: str = Field(..., description="Standardized industry taxonomy")
    secondary_industry: Optional[str] = Field(None, description="Secondary or intersectional sector")
    target_geography: str = Field(default="Global", description="Target region")
    
    # Core Task 2 Fields
    problem_statement: str = Field(..., description="Clear, quantified pain point")
    proposed_solution: str = Field(..., description="The proposed product or solution")
    target_customers: str = Field(..., description="Target customer segment")
    industry: str = Field(..., description="Industry vertical")
    key_features: List[str] = Field(default_factory=list, description="Key features of the MVP")
    
    # Downstream Agent Seeding
    monetization_model: str = Field(default="B2B SaaS Subscription", description="Revenue engine archetype")
    pricing_hypothesis: Optional[str] = Field(None, description="Estimated price point and ROI rationale")
    search_keywords: List[str] = Field(default_factory=list, description="Keywords for web retrieval")
    search_queries: List[str] = Field(default_factory=list, description="Targeted queries for Tavily Search Agent")
