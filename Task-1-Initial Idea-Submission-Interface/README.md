# Task 1: Startup Idea Submission Interface

Part of the AI-Based Startup Idea Validator with Market Analysis
Assistance project.

## Objective
Build the web interface where a founder submits a startup idea, validate
the input, connect the form to the backend, and show the validation
report returned by the multi-agent workflow.

## Features
- Idea form: name, description, industry, target customers, optional
  location, budget and relevant details
- Input validation with a clear message under each field
- Three one-click example ideas (EdTech, Healthcare, Agriculture)
- Progress panel while the six agents run
- Report page with SWOT matrix, source links, Download (.md) and Print
- Connected to the Task 4 backend (`POST /validate`)
- Optional live results from the Task 3 Web Search Agent
- Workspace page listing past ideas (saved in the browser)
- Clear messages for missing input, server errors, an unreachable
  server and unexpected replies
- Demo mode that works without any backend

## Technology Stack
- React 18
- Vite 5
- React Router 6
- Fetch API
- Node.js 18 or newer

## Project Structure
```text
Task-1-Idea-Submission-Interface/
  src/
    config.js            backend settings (edit this if the backend changes)
    samples.js           the three example ideas
    storage.js           saves ideas in the browser
    api/                 client.js, ideaApi.js, mock.js
    utils/               validation.js, reportMarkdown.js
    components/          IdeaForm, ReportSections, AgentList,
                         AnalyzingPanel, AdvisorChat, Markdownish, Layout
    pages/               SubmitIdeaPage, IdeaDetailPage, WorkspacePage
    App.jsx, main.jsx, index.css
  docs/
    idea-submission-interface.md
    screenshots/
  index.html
  package.json
  vite.config.js
  .env.example
  .gitignore
  README.md
```

## Setup
Run these from this project's root directory:

```powershell
npm install
copy .env.example .env
npm run dev
```

Open http://localhost:5173

On Windows PowerShell, if `npm` is blocked, run once:
`Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`

## Environment Variables
Set these in a local `.env` file. Restart `npm run dev` after changes.

| Variable | Default | Purpose |
|---|---|---|
| `VITE_USE_MOCK` | `false` | `true` shows sample data without any backend |
| `VITE_PROXY_TARGET` | `http://localhost:8000` | Where the Task 4 backend runs |
| `VITE_ENABLE_WEB_SEARCH` | `false` | `true` also calls the Task 3 Web Search Agent |
| `VITE_SEARCH_PROXY_TARGET` | `http://localhost:8001` | Where the Task 3 server runs |
| `VITE_API_URL` | empty | Full backend URL for deployed setups |

The frontend holds no API keys. LLM and Tavily keys belong in the
backend's own `.env`. Never commit `.env`.

## Running with the Backend
Start the Task 4 backend in a separate terminal:

```powershell
cd Task-4-Multi-Agent-Architecture
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Then run this frontend (`npm run dev`) with `VITE_USE_MOCK=false`.
Submitting the form sends `POST /validate`, and the backend terminal
shows `POST /validate ... 200 OK`.

The backend runs in its own mock mode by default (`USE_MOCKS=true`), so
the report contains placeholder text. For real analysis, set
`USE_MOCKS=false` and add the LLM and Tavily keys in the backend's `.env`.

### Optional: live web search (Task 3)
```powershell
cd Task-3-Web-Search-Agent
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8001
```
Add `TAVILY_API_KEY` to that folder's `.env`, set
`VITE_ENABLE_WEB_SEARCH=true` here, and restart `npm run dev`.

## API Contract
`POST /validate`

```json
{
  "name": "PrepMate AI",
  "description": "An AI mock interview platform for engineering students.",
  "target_market": "Final-year engineering students in India",
  "industry": "EdTech",
  "location": "India",
  "budget": "Rs. 3 lakh"
}
```
`location` and `budget` are left out when empty. The "Relevant details"
text is appended to `description`, because the backend has no field for it.

Response sections shown in the report: `startup_idea`,
`market_analysis`, `competitor_analysis`, `swot_and_risks`,
`mvp_recommendation`, `sources`, `final_summary`.

If the backend's endpoint or field names change, edit only
`src/config.js`.

## Error Handling
| Situation | What the user sees |
|---|---|
| Required field empty or too short | Message under the field; nothing is sent |
| Backend stopped or unreachable | "Could not reach the server..." |
| No reply within 2 minutes | "The server took too long to respond..." |
| Backend error (422, 500, 502) | The backend's message, or the status code |
| Reply is not JSON or has no report sections | "...not in the expected format" |
| Web search fails | The report still opens, with a short note |

The form keeps the user's answers after any error so they can retry.

## Testing
Automated browser tests passed 69 of 69 checks: validation, three ideas
from different industries, the request sent to the backend, every failure
case above, and phone-size screens. Details and screenshots are in
`docs/idea-submission-interface.md`.

Manual test: start the backend, then use the three example buttons
(EdTech, Healthcare, Agriculture) and submit each one.

## Scope
This folder implements the idea submission interface and its connection
to the Task 4 backend. Calling the Task 2 structured extraction and the
Task 3 Web Search Agent from the backend's orchestrator is handled in the
backend. Extra structured fields the backend adds to `startup_idea`
appear on the report page automatically. The advisor chat and
go-to-market section show a short note until the backend provides them.
