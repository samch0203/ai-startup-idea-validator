
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from web_search_agent import run_web_search_agent

app = FastAPI(
    title="Startup Idea Web Search Agent",
    description=(
        "Search for market trends, potential competitors, "
        "and customer needs related to startup ideas."
    ),
    version="1.0.0",
)


class StartupIdeaRequest(BaseModel):
    startup_idea: str = Field(
        ...,
        min_length=10,
        max_length=2000,
        description="Description of the proposed startup idea.",
    )


@app.get("/")
def home():
    return {
        "message": "Startup Web Search Agent API is running!",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "running"}


@app.post("/api/web-search")
def web_search(request: StartupIdeaRequest):
    idea = request.startup_idea.strip()

    if len(idea) < 10:
        raise HTTPException(
            status_code=422,
            detail="Please provide a more detailed startup idea.",
        )

    try:
        result = run_web_search_agent(idea)
        return result

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    except RuntimeError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="An unexpected server error occurred.",
        ) from exc
