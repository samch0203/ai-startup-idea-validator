from app.agents import (
    web_search_agent,
    market_analysis_agent,
    competitor_analysis_agent,
    swot_risk_agent,
    mvp_recommendation_agent,
    report_generation_agent,
)
from app.schemas import StartupIdea, ValidationReport


def run_validation_workflow(idea: StartupIdea) -> ValidationReport:
    """Run the startup validation workflow from beginning to end."""

    # Agent 1: Gather relevant search results.
    search_results = web_search_agent(idea)

    # Agent 2: Analyze market demand and opportunities.
    market_analysis = market_analysis_agent(idea, search_results)

    # Agent 3: Examine competitors and alternatives.
    competitor_analysis = competitor_analysis_agent(
        idea, search_results
    )

    # Agent 4: Identify SWOT and business risks.
    swot_and_risks = swot_risk_agent(
        idea, market_analysis, competitor_analysis
    )

    # Agent 5: Recommend a minimum viable product.
    mvp_recommendation = mvp_recommendation_agent(
        idea, market_analysis, swot_and_risks
    )

    # Agent 6: Prepare the final summary.
    final_summary = report_generation_agent(
        idea,
        market_analysis,
        competitor_analysis,
        swot_and_risks,
        mvp_recommendation,
    )

    # Return a structured report to the API.
    return ValidationReport(
        startup_idea=idea,
        market_analysis=market_analysis,
        competitor_analysis=competitor_analysis,
        swot_and_risks=swot_and_risks,
        mvp_recommendation=mvp_recommendation,
        sources=search_results,
        final_summary=final_summary,
    )
