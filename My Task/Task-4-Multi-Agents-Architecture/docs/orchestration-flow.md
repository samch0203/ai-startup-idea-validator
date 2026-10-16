# Orchestration Flow

## Input
The user submits a startup idea containing:
- Startup name
- Description
- Target market
- Industry
- Location
- Budget

## Execution Sequence

1. The API validates the startup idea using the StartupIdea schema.
2. The orchestrator invokes the Web Search Agent.
3. Search results are stored as structured SearchResult objects.
4. The Market Analysis Agent receives the idea and search results.
5. The Competitor Analysis Agent receives the idea and search results.
6. The SWOT and Risk Agent receives both analysis outputs.
7. The MVP Recommendation Agent receives the market analysis and risks.
8. The Report Generation Agent receives the complete analysis.
9. The orchestrator assembles a ValidationReport.
10. FastAPI returns the report to the caller.

## Error Handling
The API returns an error response if the workflow fails. The backend
terminal contains the underlying error for debugging.

## Test Mode
Mock mode can test orchestration without API keys. Mock results are
illustrative only and must not be presented as verified market research.

