from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError
from dotenv import load_dotenv

from app.schemas import IdeaSubmission
from app.services.idea_extraction import extract_structured_idea
from app.services.web_search import search_startup_idea
from app.orchestrator import run_validation_workflow

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent
app = FastAPI(
    title="AI-Based Startup Idea Validator",
    description="Milestone 1: idea submission, structured extraction, web search, and orchestration",
    version="1.0.0",
)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


@app.get("/")
def home():
    return FileResponse(BASE_DIR / "static" / "index.html")


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "startup-idea-validator"}


@app.post("/api/extract")
def extract_endpoint(submission: IdeaSubmission):
    try:
        return extract_structured_idea(submission).model_dump()
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:
        print(f"Idea extraction error: {exc}")
        raise HTTPException(status_code=502, detail="Idea extraction failed. Check backend logs.") from exc


@app.post("/api/search")
def search_endpoint(submission: IdeaSubmission):
    try:
        idea = extract_structured_idea(submission)
        return search_startup_idea(idea).model_dump()
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:
        print(f"Web search error: {exc}")
        raise HTTPException(status_code=502, detail="Web search failed. Check backend logs.") from exc


@app.post("/api/validate")
def validate_endpoint(submission: IdeaSubmission):
    try:
        return run_validation_workflow(submission).model_dump()
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:
        print(f"Validation workflow error: {exc}")
        raise HTTPException(status_code=502, detail="Validation workflow failed. Check backend logs.") from exc
