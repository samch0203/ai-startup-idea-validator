# Task 3: Web Search Agent

## 1. Project Overview

The Web Search Agent is part of the AI-Based Startup Idea Validator with Market Analysis Assistance project. It searches the web for information related to a startup idea to support market research, competitor discovery, and customer-needs analysis.

## 2. Features

- Generates four search queries from a startup idea.
- Integrates with the Tavily Search API.
- Retrieves website titles, URLs, content snippets, and relevance scores.
- Removes duplicate URLs from search results.
- Returns structured JSON.
- Supports multiple startup industries.
- Handles missing API keys, network errors, and partial search failures.
- Exposes the agent through a FastAPI endpoint.

## 3. Technology Stack

- Python 3
- FastAPI
- Uvicorn
- Tavily Search API
- Requests
- python-dotenv

## 4. Project Structure

```text
Task-3-Web-Search-Agent/
├── web_search_agent.py
├── main.py
├── requirements.txt
├── .env
├── .env.example
├── .gitignore
└── README.md
```

## 5. Installation

From the main repository directory, install the dependencies:

```bash
python -m pip install -r Task-3-Web-Search-Agent/requirements.txt
```

## 6. Environment Configuration

Obtain an API key from https://tavily.com/.

Create a `.env` file inside the Task-3-Web-Search-Agent directory:

```env
TAVILY_API_KEY=your_actual_api_key
```

Replace the placeholder with your own API key.

Never commit the `.env` file or expose the API key publicly.

## 7. Run the Web Search Agent

To run the standalone agent:

```bash
python Task-3-Web-Search-Agent/web_search_agent.py
```

Enter a startup idea when prompted.

## 8. Run the FastAPI Server

From the main repository directory, run:

```bash
python -m uvicorn --app-dir Task-3-Web-Search-Agent main:app --reload
```

Open the interactive API documentation:

http://127.0.0.1:8000/docs

### API Endpoint

**POST** `/api/web-search`

Example request:

```json
{
  "startup_idea": "An AI-powered platform that helps farmers detect crop diseases from plant images and recommends treatments."
}
```

The response contains the startup idea, generated queries, total result count, search results, failed queries, and status.

## 9. Testing

The agent was tested with startup ideas from three industries:

1. Agriculture — AI-based crop disease detection.
2. Healthcare — clinic discovery and appointment availability.
3. Education — affordable online tutoring.

Record the actual HTTP response codes and test outcomes before submission.

## 10. Error Handling

The implementation handles missing API credentials, failed search requests, timeouts, invalid responses, duplicate URLs, and partial query failures.

## 11. Limitations

Search results may be incomplete or outdated. The agent retrieves research evidence but does not independently verify market size, profitability, or direct competitor status.

## 12. Future Integration

The agent can be integrated with the main project orchestrator to provide market research results to downstream startup-analysis agents.
