from fastapi import FastAPI, HTTPException

from app.schemas import StartupIdea, ValidationReport
from app.orchestrator import run_validation_workflow

app = FastAPI(
    title="AI-Based Startup Idea Validator",
    description="Multi-agent startup idea analysis prototype",
    version="0.1.0",
)


@app.get("/")
def home():
    return {
        "message": "Startup Idea Validator API is running.",
        "docs": "/docs",
        "validation_endpoint": "/validate",
    }


@app.post("/validate", response_model=ValidationReport)
def validate_startup(idea: StartupIdea):
    try:
        return run_validation_workflow(idea)
    except Exception as exc:
        # Keep internal error details out of the API response.
        print(f"Validation workflow error: {exc}")
        raise HTTPException(
            status_code=502,
            detail="The validation workflow failed. Check the backend terminal.",
        ) from exc
