# Task 4: Multi-Agent Architecture and Orchestration

Part of the AI-Based Startup Idea Validator with Market Analysis
Assistance project.

## Objective
Design and implement a multi-agent workflow that coordinates startup
idea research, market analysis, competitor analysis, SWOT and risk
assessment, MVP recommendations, and report generation.

## Features
- Defined responsibilities for six agents
- Structured startup idea and search-result schemas
- Sequential workflow orchestration
- FastAPI validation endpoint
- Mock mode for testing without API keys
- Optional live web search and LLM integration
- Architecture and orchestration documentation

## Technology Stack
- Python
- FastAPI
- Pydantic
- OpenAI-compatible LLM client
- Tavily Search API
- python-dotenv

## Project Structure
```text
app/
  __init__.py
  schemas.py
  agents.py
  orchestrator.py
  main.py
docs/
  architecture.md
  orchestration-flow.md
requirements.txt
.env.example
.gitignore
README.md
```

## Setup

Create and activate a virtual environment, then install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Run the API from this project's root directory:

```powershell
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs to test the endpoint.

## Mock Mode
Mock mode is enabled by default. It verifies the workflow without
external API credentials. Results are examples, not validated market
facts.

## Live Mode
Configure a local `.env` file using `.env.example` as a guide.
Set `USE_MOCKS=false` and provide valid LLM and Tavily credentials.
Never commit `.env` or API keys.

## Scope
This folder implements the initial multi-agent orchestration prototype.
Integration with the team's complete application will be handled
separately.
