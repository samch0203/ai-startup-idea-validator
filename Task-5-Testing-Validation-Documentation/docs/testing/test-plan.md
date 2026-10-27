# Test Plan - Task 5: Testing, Validation and Documentation

Project: AI-Based Startup Idea Validator with Market Analysis Assistance
Component under test: Task 4 multi-agent pipeline (`app/`: schemas, agents, orchestrator, FastAPI)
Tester: Member 5

## 1. Objectives
1. Test the agents with startup ideas from different domains (EdTech, Healthcare, AgriTech, RetailTech).
2. Verify the relevance and accuracy of market and competitor findings.
3. Check source URLs, output formats and pipeline execution.
4. Document test cases, results, bugs and fixes.

## 2. Test environment
| Item | Value |
|---|---|
| Code under test | Task 4 zip (`Task-4-Multi-Agent-Architecture`), unmodified |
| Python | 3.12 (project venv) / 3.13 (test machine) |
| Framework | FastAPI + Pydantic v2, OpenAI-compatible LLM client, Tavily search |
| Test framework | Python `unittest` (also runs under `pytest`) - no extra dependencies except `httpx` for the API tests |
| Modes | **Mock mode** (`USE_MOCKS=true`, default) and **live mode** (`USE_MOCKS=false`, real keys) |

## 3. Approach - three layers
| Layer | What it proves | How | Needs keys? |
|---|---|---|---|
| A. Automated unit/integration tests (`tests/`) | Code logic, wiring, schemas, API behaviour, error handling | `python -m unittest discover -s tests -t .` | No |
| B. Live-mode tests with fake clients (`tests/test_live_mode_mocked.py`) | Real code paths for Tavily/LLM (queries, prompts, source handling, errors) without internet | Fake `TavilyClient` / `ask_llm` | No |
| C. Domain validation runner (`scripts/run_domain_validation.py`) | Quality of *real* output: format, URL validity/reachability, relevance, ungrounded statistics and company names | Runs the 4 domain ideas through the real pipeline | **Yes** for live mode |

Layer A and B prove the system works correctly. Only layer C in live mode can show whether the
market/competitor findings are *relevant and accurate*; mock mode returns fixed placeholder text
by design (see OBS-01).

## 4. Test data
Four startup ideas in `test_data/startup_ideas.json`, one per domain, each with a keyword list
(for relevance checks) and a list of well-known competitors (for a sanity check).

| ID | Domain | Startup | Idea |
|---|---|---|---|
| EDTECH-01 | EdTech | VidyaBuddy | Vernacular AI tutor for Class 8-10 CBSE students |
| HEALTH-01 | Healthcare | CareLoop | Remote monitoring for elderly diabetes/hypertension patients |
| AGRI-01 | AgriTech | KisanSense | Soil-moisture sensors + irrigation alerts for small farmers |
| RETAIL-01 | RetailTech | ShelfSmart | Inventory/demand forecasting for kirana stores |

## 5. Pass criteria for real (live) output
| Check | Rule | Type |
|---|---|---|
| Format | All 7 report sections present; 4 analysis sections non-empty objects; summary non-empty; JSON-serialisable | automatic |
| Sources present | at least 1 source | automatic |
| URL syntax | every source is an http(s) URL | automatic |
| Not placeholders | no `example.com` links (live mode only) | automatic |
| URL reachable | HTTP 2xx/3xx (401/403/429 accepted as "site blocks bots") - option `--check-urls` | automatic |
| Relevance | >= 60 % of sources contain at least one domain keyword | automatic (heuristic) |
| Statistics grounded | every %, currency or crore/million/billion figure in the analysis also appears in a source | automatic (heuristic) |
| Competitor names grounded | company names in the competitor analysis appear in the sources | **manual review** of the flagged list |
| Accuracy | spot-check 3 competitors + 3 statistics per domain by opening the cited URL | **manual** (checklist in `test-results.md`) |

## 6. Test case catalogue
Result column = result on the **original Task 4 code**. "Open bug" cases check the *correct*
behaviour and are reported as SKIPPED with the bug id until the bug is fixed.

### 6.1 Input validation (`tests/test_schema_validation.py`)
| ID | Test | Expected | Result |
|---|---|---|---|
| SCH-01 | Valid idea | Accepted; defaults location=India, budget="Not specified" | Pass |
| SCH-02 | Each required field missing | ValidationError | Pass |
| SCH-03 | Too-short name/description/market/industry | ValidationError | Pass |
| SCH-04 | Wrong type (number for name) | ValidationError | Pass |
| SCH-05 | Hindi (Unicode) text | Accepted | Pass |
| SCH-06 | Description of 15 spaces | Rejected | **Open bug BUG-01** |
| SCH-07 | Name of 3 spaces | Rejected | **Open bug BUG-01** |

### 6.2 Domain and pipeline execution (`tests/test_pipeline.py`)
| ID | Test | Expected | Result |
|---|---|---|---|
| DOM-01 | All 4 domains run end to end | Valid `ValidationReport`, format check clean | Pass |
| DOM-02 | Report echoes submitted idea | name/industry equal input | Pass |
| DOM-03 | Final summary names the startup | name in summary | Pass |
| DOM-04 | Market analysis uses target market | `target_customers` == input | Pass |
| DOM-05 | Sources labelled with domain | domain in source titles | Pass |
| DOM-06 | Mock output is honest | says "mock" / "not proof" | Pass |
| PIPE-01 | Agent order and data hand-over | search -> market -> competitor -> SWOT -> MVP -> report, each receives the right inputs | Pass |
| PIPE-02 | One agent raises | pipeline stops, later agents not called | Pass |
| PIPE-03 | Two runs in a row | no data leaks between runs | Pass |
| OBS-01 | Mock competitor output across domains | documents that it is identical | Pass (observation) |
| OBS-02 | Mock source URLs | valid syntax but all `example.com` placeholders | Pass (observation) |

### 6.3 Live-mode wiring with fake clients (`tests/test_live_mode_mocked.py`)
| ID | Test | Expected | Result |
|---|---|---|---|
| LIVE-01 | Search query | contains industry, location, "competitors" | Pass |
| LIVE-02 | Tavily results -> `SearchResult` | titles/urls/content mapped | Pass |
| LIVE-03 | Missing Tavily key | clear `RuntimeError` naming the variable | Pass |
| LIVE-04 | Results with empty / `javascript:` URL | dropped from sources | **Open bug BUG-02** |
| LIVE-05 | Result without title | title "Untitled" | Pass |
| LIVE-06 | Missing LLM key | clear `RuntimeError` | Pass |
| LIVE-07 | Competitor prompt | contains idea, research URLs, "do not claim" guard | Pass |
| LIVE-08 | Market prompt | contains "Do not invent statistics" | Pass |
| LIVE-09 | Full pipeline with fake LLM | all sections filled, 2 sources | Pass |
| LIVE-10 | Data hand-over to LLM | SWOT/MVP/report prompts contain earlier outputs | Pass |
| LIVE-11 | Zero search results | LLM must NOT be asked to "analyse" nothing | **Open bug BUG-03** |
| OBS-03 | Live vs mock output shape | documents that shapes differ | Pass (observation) |
| FLAG-01 | `USE_MOCKS` true/false | correct mode | Pass |
| FLAG-02 | `USE_MOCKS` unset | mock mode | Pass |
| FLAG-03 | `USE_MOCKS=1`, `yes`, `" true"` | stay in mock mode | **Open bug BUG-04** |
| FLAG-04 | `USE_MOCKS=false/0/no` | live mode | Pass |

### 6.4 API (`tests/test_api.py`)
| ID | Test | Expected | Result |
|---|---|---|---|
| API-01 | `GET /` | 200 + endpoint info | Pass |
| API-02 | `POST /validate` for each domain | 200, JSON, matches `ValidationReport` | Pass |
| API-03 | Missing field | 422 naming the field | Pass |
| API-04 | Empty body | 422 | Pass |
| API-05 | Malformed JSON | 422 | Pass |
| API-06 | Wrong method / unknown route | 405 / 404 | Pass |
| API-07 | Workflow crash | 502, secret not in response | Pass |
| API-07b | Workflow crash | secret not printed in server log | **Open bug BUG-05** |
| API-08 | Live mode without keys | 502 | Pass |
| API-09 | Unicode payload | 200, name preserved | Pass |
| API-10 | ~46 000-character description | 200 | Pass |
| API-11 | `/openapi.json`, `/docs` | 200 | Pass |

### 6.5 Checker self-tests (`tests/test_validation_checks.py`)
URL syntax, placeholder detection, duplicate/empty sources, relevance score, ungrounded
statistics (invented 87 % / Rs 4,500 crore are caught, a sourced $5 billion is not), ungrounded
company names, report-format checker. These prove the validation script can detect bad output.

## 7. Out of scope
Load/performance testing, security penetration testing, front-end testing (not in Task 4),
LLM answer quality beyond the grounding heuristics above.
