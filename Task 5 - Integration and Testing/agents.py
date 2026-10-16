import os
from app.schemas import AgentAnalysis, SearchReport, StructuredIdea


def _llm_json(system_prompt: str, payload: str) -> str:
    api_key = os.getenv("LLM_API_KEY")
    model = os.getenv("LLM_MODEL")
    if not api_key or not model:
        raise RuntimeError("Live analysis requires LLM_API_KEY and LLM_MODEL in .env.")
    from openai import OpenAI

    options = {"api_key": api_key}
    if os.getenv("LLM_BASE_URL"):
        options["base_url"] = os.getenv("LLM_BASE_URL")
    client = OpenAI(**options)
    response = client.chat.completions.create(
        model=model,
        temperature=0.2,
        response_format={"type": "json_object"},
        messages=[{"role": "system", "content": system_prompt},
                  {"role": "user", "content": payload}],
    )
    content = response.choices[0].message.content
    if not content:
        raise ValueError("LLM returned an empty analysis response.")
    return content


def run_analysis_agents(idea: StructuredIdea, search: SearchReport) -> AgentAnalysis:
    """Initial agent analysis stage. Live mode uses LLM; mock mode is transparent."""
    if os.getenv("USE_MOCKS", "true").lower() == "true":
        return AgentAnalysis(
            market_analysis={
                "assessment": "Requires validation with customers and verified sources.",
                "target_customers": idea.target_customers,
                "opportunities_to_test": ["Interview prospective customers", "Test a landing page"],
                "evidence_status": "Mock mode; no verified market data used.",
            },
            competitor_analysis={
                "direct_competitors": "Not verified in mock mode",
                "indirect_alternatives": "Identify alternatives customers currently use",
                "questions": ["What differentiates the idea?", "Why would customers switch?"],
            },
            swot_and_risks={
                "strengths": ["A defined target customer can guide testing"],
                "weaknesses": ["Demand and costs are not yet validated"],
                "opportunities": ["Test a focused solution with early users"],
                "threats": ["Competition and low willingness to pay"],
                "risks": ["Customer demand", "Technical feasibility", "Financial sustainability"],
            },
            mvp_recommendation={
                "features": idea.key_features[:3],
                "validation_steps": ["Interview 10 potential customers", "Prototype the core workflow", "Measure interest before scaling"],
                "note": "Illustrative recommendations; validate with users.",
            },
            final_summary=(
                f"Preliminary prototype report for {idea.name}. This is not proof of viability. "
                "Validate demand, willingness to pay, competitors, costs, and feasibility."
            ),
        )

    import json
    payload = json.dumps({"idea": idea.model_dump(), "search_report": search.model_dump()}, ensure_ascii=False)
    raw = _llm_json(
        "You are a cautious startup research analyst. Return valid JSON with keys market_analysis, "
        "competitor_analysis, swot_and_risks, mvp_recommendation, final_summary. Use the supplied "
        "sources only as leads; distinguish evidence from assumptions and never invent statistics.",
        payload,
    )
    try:
        data = json.loads(raw)
        return AgentAnalysis.model_validate(data)
    except Exception as exc:
        raise ValueError("LLM returned an invalid analysis JSON structure.") from exc
