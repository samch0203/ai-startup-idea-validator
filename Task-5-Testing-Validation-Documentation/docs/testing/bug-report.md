# Bug Report and Fixes - Task 5

All bugs were found by running the Task 4 code as received (no changes). Every bug has an
automated test in `tests/` that fails (shown as SKIPPED "KNOWN BUG-xx") on the original code and
passes after `fixes/task4-fixes.patch` is applied. Severity: High / Medium / Low.

## Summary
| ID | Title | Severity | File | Status |
|---|---|---|---|---|
| BUG-01 | Whitespace-only text passes input validation | Medium | `app/schemas.py` | Fix provided, verified |
| BUG-02 | Search results with empty/invalid URLs become "sources" | Medium | `app/agents.py` | Fix provided, verified |
| BUG-03 | LLM asked to analyse when search returned nothing | High | `app/agents.py` | Fix provided, verified |
| BUG-04 | `USE_MOCKS=1` / `yes` / `" true"` silently switches to live mode | Medium | `app/agents.py` | Fix provided, verified |
| BUG-05 | API keys can be written to the server log | High | `app/main.py` | Fix provided, verified |

| ID | Observation (design limitation, not changed by the patch) |
|---|---|
| OBS-01 | Mock mode returns identical competitor text for every domain |
| OBS-02 | Mock source URLs are `example.com` placeholders |
| OBS-03 | Live output shape differs from mock output shape |
| OBS-04 | No explicit timeouts/retries; every failure becomes HTTP 502 |

---

## BUG-01 - Whitespace-only text passes input validation  (Medium)
- **Test:** SCH-06, SCH-07
- **Steps:** `POST /validate` with `"description": "               "` (15 spaces) or `"name": "   "`.
- **Expected:** 422 validation error.
- **Actual:** Accepted (`min_length` counts spaces), so a blank idea runs the whole pipeline (and in
  live mode spends search/LLM credits on nothing).
- **Fix:** `model_config = ConfigDict(str_strip_whitespace=True)` on `StartupIdea` so text is
  trimmed before the length check.
- **Verification:** SCH-06 and SCH-07 pass after the patch.

## BUG-02 - Search results with empty/invalid URLs become sources  (Medium)
- **Test:** LIVE-04
- **Steps:** Tavily returns an item with `url: ""` or `url: "javascript:alert(1)"`.
- **Expected:** Item is dropped; every source in the report is a checkable http(s) link.
- **Actual:** `item.get("url", "")` is copied into the report unchanged, so the report can list a
  source with no link (or a non-http link which a front end might render as a clickable link).
- **Fix:** `_is_valid_http_url()` helper; results without a valid http(s) URL are skipped.
- **Verification:** LIVE-04 passes after the patch.

## BUG-03 - LLM asked to analyse when search returned nothing  (High)
- **Test:** LIVE-11
- **Steps:** Live mode, Tavily returns `{"results": []}` (rare niche query, API quota, etc.).
- **Expected:** No competitor/market "findings" are invented; the report says no research was found.
- **Actual:** `market_analysis_agent` and `competitor_analysis_agent` still call the LLM with
  `Research: []`. The model can then produce plausible-looking competitors and statistics with no
  evidence, which is the exact risk the system prompts try to prevent.
- **Fix:** If `search_results` is empty, both agents return an explicit "No web research was
  found" message plus `evidence_limit`, without calling the LLM.
- **Verification:** LIVE-11 passes after the patch (LLM mock asserted "not called").

## BUG-04 - `USE_MOCKS` parsing silently enables live mode  (Medium)
- **Test:** FLAG-03
- **Steps:** Put `USE_MOCKS=1`, `USE_MOCKS=yes`, `USE_MOCKS=True ` (trailing space) or
  `USE_MOCKS= true` in `.env`.
- **Expected:** Mock mode (the documented safe default).
- **Actual:** `use_mocks()` is `value.lower() == "true"`; anything else is treated as *live*, so a
  typo or a different "true" spelling sends real API calls and uses paid credits (or fails with
  confusing "missing key" errors).
- **Fix:** Trim and lower-case; live mode only for explicit `false`, `0`, `no`, `off`.
- **Verification:** FLAG-03 passes; FLAG-01/02/04 still pass.

## BUG-05 - API keys can be written to the server log  (High)
- **Test:** API-07b (API-07 shows the HTTP response itself is safe)
- **Steps:** Make the LLM/search client raise an error whose text contains the key, e.g. an
  authentication error message such as `Incorrect API key provided: sk-...`.
- **Expected:** Nothing secret in console/log output.
- **Actual:** `main.py` does `print(f"Validation workflow error: {exc}")`, printing the full
  exception text. Server logs are often shared in screenshots, tickets or hosting dashboards.
- **Fix:** Log `ExceptionType: message` with keys redacted by `_redact()` (patterns `sk-...`,
  `tvly-...`, `api_key=...`).
- **Verification:** API-07b passes after the patch; the HTTP response is unchanged (502, generic text).

---

## Observations (not changed by the patch - for the team to decide)

### OBS-01 - Mock competitor analysis is identical for every domain
`competitor_analysis_agent` in mock mode returns the same dictionary whatever the idea. This is
intentional ("not verified") but means mock mode **cannot** show domain relevance. Relevance and
accuracy must be tested in live mode with `scripts/run_domain_validation.py`.

### OBS-02 - Mock sources are placeholders
Mock URLs are `https://example.com/...`. They are valid in syntax, but a report generated in mock
mode must never be shown to end users as real research. The runner script marks this as expected in
mock mode and *fails* the "not placeholder" check in live mode.

### OBS-03 - Live output shape differs from mock output shape
Mock agents return structured keys (`potential_demand`, `opportunities`, `strengths`, ...). Live
agents return a single free-text field (`{"analysis": "..."}` / `{"recommendation": "..."}`). A front
end that renders the mock keys will show nothing useful in live mode. **Recommendation:** ask the
LLM for JSON with the same keys as mock mode, or document both shapes for the UI team (Task 4 owner).

### OBS-04 - No explicit timeouts/retries; every failure is HTTP 502
Neither the OpenAI nor the Tavily client is given a timeout or retry setting (library defaults
apply), so a slow provider can hold a request for a long time. Every exception - including
"API key not configured" (a server configuration problem, more like 500/503) - returns 502 with
the same generic message. Acceptable for a prototype; worth improving before deployment.

### Housekeeping note for the Git upload
The Task 4 zip contains a Windows `.venv/` (about 23 MB) and `__pycache__/`. They are already
listed in `.gitignore`, but check `git status` before committing; never upload `.venv/` or `.env`.
