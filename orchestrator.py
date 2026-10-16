from app.schemas import IdeaSubmission, ValidationReport
from app.services.idea_extraction import extract_structured_idea
from app.services.web_search import search_startup_idea
from app.agents import run_analysis_agents


def run_validation_workflow(submission: IdeaSubmission) -> ValidationReport:
    """Coordinate extraction, search, analysis agents, and final report."""
    structured_idea = extract_structured_idea(submission)
    search_report = search_startup_idea(structured_idea)
    analysis = run_analysis_agents(structured_idea, search_report)
    return ValidationReport(
        structured_idea=structured_idea,
        search_report=search_report,
        analysis=analysis,
    )
