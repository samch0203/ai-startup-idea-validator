import os
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI
from tavily import TavilyClient

from app.schemas import SearchResult, StartupIdea

load_dotenv()


def use_mocks() -> bool:
    return os.getenv("USE_MOCKS", "true").lower() == "true"


def ask_llm(system_prompt: str, user_prompt: str) -> str:
    """Call an OpenAI-compatible LLM when mock mode is disabled."""
    api_key = os.getenv("LLM_API_KEY")
    model = os.getenv("LLM_MODEL")

    if not api_key or not model:
        raise RuntimeError(
            "Set LLM_API_KEY and LLM_MODEL in your .env file."
        )

    client_options: dict[str, Any] = {"api_key": api_key}
    base_url = os.getenv("LLM_BASE_URL")
    if base_url:
        client_options["base_url"] = base_url

    client = OpenAI(**client_options)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
    )

    return response.choices[0].message.content or ""


def web_search_agent(idea: StartupIdea) -> list[SearchResult]:
    """Agent 1: Find relevant information on the web."""
    if use_mocks():
        return [
            SearchResult(
                title=f"Market research for {idea.industry}",
                url="https://example.com/market-research",
                content=(
                    f"Placeholder research for {idea.industry} "
                    f"in {idea.location}. Replace this with verified "
                    "web research before making business decisions."
                ),
            ),
            SearchResult(
                title=f"Customer trends for {idea.target_market}",
                url="https://example.com/customer-trends",
                content=(
                    f"Placeholder customer research for "
                    f"{idea.target_market}."
                ),
            ),
        ]

    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise RuntimeError("Set TAVILY_API_KEY in your .env file.")

    client = TavilyClient(api_key=api_key)
    query = (
        f"{idea.industry} market trends {idea.target_market} "
        f"{idea.location} competitors"
    )
    response = client.search(query=query, max_results=5)

    results = []
    for item in response.get("results", []):
        results.append(
            SearchResult(
                title=item.get("title", "Untitled"),
                url=item.get("url", ""),
                content=item.get("content", ""),
            )
        )
    return results


def market_analysis_agent(
    idea: StartupIdea, search_results: list[SearchResult]
) -> dict[str, Any]:
    """Agent 2: Assess market demand and opportunities."""
    if use_mocks():
        return {
            "potential_demand": "Requires customer validation",
            "target_customers": idea.target_market,
            "opportunities": [
                "Interview potential customers",
                "Test demand with a landing page",
            ],
            "evidence_limit": "Mock mode; no verified market data used.",
        }

    return {
        "analysis": ask_llm(
            "You are a market research analyst. Separate evidence "
            "from assumptions. Do not invent statistics.",
            f"Startup idea: {idea.model_dump_json()}\n"
            f"Research: {[r.model_dump() for r in search_results]}\n"
            "Analyze demand, customer needs, trends, and uncertainties.",
        )
    }


def competitor_analysis_agent(
    idea: StartupIdea, search_results: list[SearchResult]
) -> dict[str, Any]:
    """Agent 3: Identify competitors and alternatives."""
    if use_mocks():
        return {
            "direct_competitors": "Not yet verified",
            "indirect_competitors": "Existing alternatives customers use",
            "differentiation_questions": [
                "What problem is solved better?",
                "Why would customers switch?",
            ],
            "evidence_limit": "Mock mode; competitor names not verified.",
        }

    return {
        "analysis": ask_llm(
            "You are a competitor research analyst. Do not claim a company "
            "is a competitor unless the supplied research supports it.",
            f"Idea: {idea.model_dump_json()}\n"
            f"Research: {[r.model_dump() for r in search_results]}\n"
            "Identify direct and indirect competitors, positioning, "
            "and differentiation opportunities.",
        )
    }


def swot_risk_agent(
    idea: StartupIdea,
    market_analysis: dict[str, Any],
    competitor_analysis: dict[str, Any],
) -> dict[str, Any]:
    """Agent 4: Assess SWOT and important risks."""
    if use_mocks():
        return {
            "strengths": ["A defined target customer can guide testing"],
            "weaknesses": ["Demand and costs are not yet validated"],
            "opportunities": ["Test a focused solution with early users"],
            "threats": ["Competition and low willingness to pay"],
            "risks": [
                "Customer demand risk",
                "Technical feasibility risk",
                "Financial sustainability risk",
            ],
        }

    return {
        "analysis": ask_llm(
            "You are a startup risk analyst. Be specific and distinguish "
            "known facts from hypotheses.",
            f"Idea: {idea.model_dump_json()}\n"
            f"Market analysis: {market_analysis}\n"
            f"Competitor analysis: {competitor_analysis}\n"
            "Provide SWOT and key risks with suggested mitigations.",
        )
    }


def mvp_recommendation_agent(
    idea: StartupIdea,
    market_analysis: dict[str, Any],
    swot_and_risks: dict[str, Any],
) -> dict[str, Any]:
    """Agent 5: Recommend a minimum viable product (MVP)."""
    if use_mocks():
        return {
            "mvp_features": [
                "One core feature solving the main customer problem",
                "Simple onboarding",
                "A feedback collection mechanism",
            ],
            "validation_plan": [
                "Interview 10 potential customers",
                "Build a clickable prototype",
                "Measure interest before scaling",
            ],
            "success_metric": "Set a measurable target after initial interviews",
        }

    return {
        "recommendation": ask_llm(
            "You are a lean startup product advisor. Recommend the smallest "
            "testable product, not a full-scale application.",
            f"Idea: {idea.model_dump_json()}\n"
            f"Market analysis: {market_analysis}\n"
            f"Risks: {swot_and_risks}\n"
            "Recommend MVP features, validation experiments, and measurable "
            "success criteria.",
        )
    }


def report_generation_agent(
    idea: StartupIdea,
    market_analysis: dict[str, Any],
    competitor_analysis: dict[str, Any],
    swot_and_risks: dict[str, Any],
    mvp_recommendation: dict[str, Any],
) -> str:
    """Agent 6: Produce a readable summary of the analysis."""
    if use_mocks():
        return (
            f"Preliminary validation for {idea.name}: "
            "This is an initial hypothesis, not proof of business viability. "
            "Validate customer demand, willingness to pay, competitors, "
            "costs, and technical feasibility before investing."
        )

    return ask_llm(
        "You are a startup report writer. Be concise and transparent about "
        "uncertainty. Never invent evidence or claim that an idea is proven.",
        f"Idea: {idea.model_dump_json()}\n"
        f"Market: {market_analysis}\n"
        f"Competitors: {competitor_analysis}\n"
        f"SWOT and risks: {swot_and_risks}\n"
        f"MVP: {mvp_recommendation}\n"
        "Write an executive summary with findings, uncertainties, and "
        "recommended next steps.",
    )

