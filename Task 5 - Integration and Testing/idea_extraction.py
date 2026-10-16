import json
import os
from app.schemas import IdeaSubmission, StructuredIdea


def _mock_extract(submission: IdeaSubmission) -> StructuredIdea:
    """Deterministic extraction for local tests; not an LLM result."""
    description = submission.idea_description.strip()
    first_sentence = description.split(".")[0].strip()
    problem = (
        f"Potential problem to validate for {submission.target_customers}: "
        f"{first_sentence[:350]}"
    )
    solution = (
        f"Develop a focused {submission.industry} solution for "
        f"{submission.target_customers}, based on this idea: {description[:500]}"
    )
    details = submission.relevant_details.strip()
    features = [
        "Core workflow addressing the primary customer problem",
        "Simple onboarding and user input",
        "Feedback and outcome tracking",
    ]
    if details:
        features.append(f"Consider user-provided requirement: {details[:180]}")
    name = " ".join(description.split()[:5]).strip(".,:;!? ") or "Startup Idea"
    return StructuredIdea(
        name=name[:80],
        problem_statement=problem,
        proposed_solution=solution,
        target_customers=submission.target_customers,
        industry=submission.industry,
        key_features=features,
        original_description=description,
        location=submission.location,
        budget=submission.budget,
        relevant_details=details,
    )


def extract_structured_idea(submission: IdeaSubmission) -> StructuredIdea:
    """Extract structured fields using an LLM, or mock extraction in test mode."""
    if os.getenv("USE_MOCKS", "true").lower() == "true":
        return _mock_extract(submission)

    api_key = os.getenv("LLM_API_KEY")
    model = os.getenv("LLM_MODEL")
    if not api_key or not model:
        raise RuntimeError("Live extraction requires LLM_API_KEY and LLM_MODEL in .env.")

    from openai import OpenAI

    options = {"api_key": api_key}
    base_url = os.getenv("LLM_BASE_URL")
    if base_url:
        options["base_url"] = base_url
    client = OpenAI(**options)

    prompt = {
        "idea_description": submission.idea_description,
        "industry": submission.industry,
        "target_customers": submission.target_customers,
        "location": submission.location,
        "budget": submission.budget,
        "relevant_details": submission.relevant_details,
    }
    response = client.chat.completions.create(
        model=model,
        temperature=0.2,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": (
                    "Extract a startup idea into valid JSON with keys: name, "
                    "problem_statement, proposed_solution, target_customers, industry, "
                    "key_features (array of strings). Use only information provided; "
                    "do not invent market statistics. Return JSON only."
                ),
            },
            {"role": "user", "content": json.dumps(prompt)},
        ],
    )
    content = response.choices[0].message.content
    if not content:
        raise ValueError("LLM returned an empty extraction response.")
    try:
        data = json.loads(content)
        # Keep source form values authoritative for fields explicitly entered by user.
        data["target_customers"] = submission.target_customers
        data["industry"] = submission.industry
        data["original_description"] = submission.idea_description
        data["location"] = submission.location
        data["budget"] = submission.budget
        data["relevant_details"] = submission.relevant_details
        if not isinstance(data.get("key_features"), list):
            raise ValueError("key_features must be a JSON array.")
        return StructuredIdea.model_validate(data)
    except (json.JSONDecodeError, TypeError) as exc:
        raise ValueError("LLM returned invalid JSON for startup idea extraction.") from exc
