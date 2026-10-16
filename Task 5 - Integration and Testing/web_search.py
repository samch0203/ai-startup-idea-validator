
import os

from app.schemas import SearchFinding, SearchReport, StructuredIdea


def generate_search_queries(idea: StructuredIdea) -> dict[str, str]:
    """Generate focused searches from the structured startup idea."""
    return {
        "market_trends": (
            f"{idea.industry} market trends customer demand and growth "
            f"in {idea.location} for {idea.target_customers}"
        ),
        "customer_problems": (
            f"{idea.target_customers} pain points unmet needs and solutions "
            f"in {idea.industry} {idea.location}"
        ),
        "competitors": (
            f"companies products competitors and alternatives in {idea.industry} "
            f"serving {idea.target_customers} in {idea.location}"
        ),
    }


def _mock_findings(query: str, category: str) -> list[SearchFinding]:
    """Return clearly labeled placeholders for development."""
    return [
        SearchFinding(
            category=category,
            query=query,
            title=f"Mock {category.lower()} research result",
            url="https://example.com/research-placeholder",
            content=(
                "Illustrative placeholder only. Enable live search and configure "
                "Tavily to retrieve real sources; do not treat this as market evidence."
            ),
            score=None,
        )
    ]


def _run_query(
    client,
    query: str,
    category: str,
    max_results: int = 4,
) -> list[SearchFinding]:
    """Run one Tavily search and normalize its results."""
    response = client.search(
        query=query,
        search_depth="basic",
        max_results=max_results,
    )

    findings = []

    for item in response.get("results", []):
        findings.append(
            SearchFinding(
                category=category,
                query=query,
                title=item.get("title") or "Untitled result",
                url=item.get("url") or "",
                content=item.get("content") or "No content snippet provided.",
                score=item.get("score"),
            )
        )

    return findings


def search_startup_idea(idea: StructuredIdea) -> SearchReport:
    """Search live web sources or return mock findings for development."""
    queries = generate_search_queries(idea)

    # Live search has its own switch, independent of LLM mock mode.
    live_search_enabled = (
        os.getenv("USE_LIVE_SEARCH", "false").strip().lower() == "true"
    )

    if not live_search_enabled:
        market = (
            _mock_findings(queries["market_trends"], "Market Trends")
            + _mock_findings(queries["customer_problems"], "Customer Demand")
        )
        competitors = _mock_findings(
            queries["competitors"],
            "Competitors",
        )

        return SearchReport(
            queries=queries,
            market_results=market,
            competitor_results=competitors,
            total_results=len(market) + len(competitors),
            live_search=False,
            message=(
                "Mock search mode: placeholder results only; "
                "no live web search was performed."
            ),
        )

    api_key = os.getenv("TAVILY_API_KEY", "").strip()

    if not api_key:
        raise RuntimeError(
            "Live search is enabled but TAVILY_API_KEY is missing. "
            "Add it to your .env file and restart the application."
        )

    from tavily import TavilyClient

    client = TavilyClient(api_key=api_key)

    market = (
        _run_query(client, queries["market_trends"], "Market Trends")
        + _run_query(client, queries["customer_problems"], "Customer Demand")
    )

    competitors = _run_query(
        client,
        queries["competitors"],
        "Competitors",
    )

    total = len(market) + len(competitors)

    return SearchReport(
        queries=queries,
        market_results=market,
        competitor_results=competitors,
        total_results=total,
        live_search=True,
        message=(
            "Live search completed. Results are research leads, not independently "
            "verified business conclusions. Review source pages before relying on them."
        ),
    )
