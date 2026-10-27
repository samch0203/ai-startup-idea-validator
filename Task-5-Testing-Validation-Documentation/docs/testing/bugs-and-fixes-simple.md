# Bugs Found in Task 4 - Simple Guide (what, where, how to fix, how to check)

Short version: the Task 4 pipeline **works** for all four domains (EdTech, Healthcare, AgriTech,
RetailTech). Testing found **5 small issues**. Each has a fix, and each fix is checked by an
automated test. Full details: `bug-report.md`. A ready-made patch with all fixes:
`../../fixes/task4-fixes.patch`.

| # | Problem in one line | File | Line (original code) |
|---|---|---|---|
| BUG-01 | A name/description made only of spaces is accepted | `app/schemas.py` | 6-8 |
| BUG-02 | Search results with a missing/invalid link are listed as sources | `app/agents.py` | 80-82 |
| BUG-03 | AI is asked to analyse even when the search found nothing | `app/agents.py` | 92 and 118 |
| BUG-04 | `USE_MOCKS=1` or `yes` silently switches to live mode | `app/agents.py` | 14-15 |
| BUG-05 | Secret API keys can be printed in the server console | `app/main.py` | 29 |

---

## BUG-01 - Blank input accepted
**What happens:** `"description": "               "` (only spaces) passes validation, so the whole
pipeline runs on an empty idea.
**Fix** (`app/schemas.py`): trim spaces before the length check.
```python
from pydantic import BaseModel, ConfigDict, Field

class StartupIdea(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)   # <- add this line
    name: str = Field(..., min_length=2, description="Startup name")
    ...
```

## BUG-02 - Bad links in sources
**What happens:** if the search tool returns an item with `url: ""`, it still appears in the
report's `sources`.
**Fix** (`app/agents.py`): add a small helper and skip bad results.
```python
from urllib.parse import urlparse

def _is_valid_http_url(url: str) -> bool:
    parsed = urlparse((url or "").strip())
    return parsed.scheme in ("http", "https") and "." in parsed.netloc

# inside web_search_agent, in the loop over response.get("results", []):
    if not _is_valid_http_url(item.get("url", "")):
        continue
```

## BUG-03 - AI asked to analyse when there is no research
**What happens:** in live mode, if the search returns zero results, `market_analysis_agent` and
`competitor_analysis_agent` still call the AI with empty research, so it can invent competitors
and numbers.
**Fix** (`app/agents.py`): in both agents, right before the live `return {"analysis": ask_llm(...)}`:
```python
    if not search_results:
        return {
            "analysis": "No web research was found, so no analysis was attempted.",
            "evidence_limit": "No search results; nothing to analyse.",
        }
```

## BUG-04 - `USE_MOCKS` setting is fragile
**What happens:** the code is `os.getenv("USE_MOCKS", "true").lower() == "true"`, so only the exact
word `true` keeps mock mode. `1`, `yes` or `true ` (with a space) go to live mode and use real API
credits.
**Fix** (`app/agents.py`):
```python
def use_mocks() -> bool:
    value = os.getenv("USE_MOCKS", "true").strip().lower()
    return value not in {"false", "0", "no", "off"}
```

## BUG-05 - Keys can appear in the console log
**What happens:** `print(f"Validation workflow error: {exc}")` prints the whole error text, which
can contain an API key (for example an "incorrect API key: sk-..." message).
**Fix** (`app/main.py`):
```python
import re
_SECRET_PATTERN = re.compile(r"(sk-|tvly-)[A-Za-z0-9_\-]+|(api[_-]?key[=:]\s*)\S+", re.I)

def _redact(message: str) -> str:
    return _SECRET_PATTERN.sub("[REDACTED]", message)

# in the except block:
print(f"Validation workflow error: {type(exc).__name__}: {_redact(str(exc))}")
```

---

## Easiest way to apply all 5 fixes
Instead of typing the code above, apply the ready patch (PowerShell, from the repo folder):
```powershell
cd "Task-4-Multi-Agent-Architecture"
git apply "..\Task-5-Testing-Validation-Documentation\fixes\task4-fixes.patch"
```

## How to check (run the tests)
```powershell
cd "..\Task-5-Testing-Validation-Documentation"
python -m unittest discover -s tests -t . -v
```
| Situation | Expected result |
|---|---|
| Original Task 4 code | `Ran 56 tests ... OK (skipped=6)` - the 6 skipped tests are the 5 bugs |
| After the fixes (run `$env:EXPECT_FIXES = "1"` first) | `Ran 56 tests ... OK` - nothing skipped |

## Message you can send to the Task 4 owner
> Hi! I tested your Task 4 pipeline. It works for all 4 domains (EdTech, Healthcare, AgriTech,
> RetailTech). I found 5 small issues (input check, source links, no-search-results case, USE_MOCKS
> setting, and keys in the log) and made a patch with fixes. It is in
> `Task-5-Testing-Validation-Documentation/fixes/task4-fixes.patch`, and
> `docs/testing/bugs-and-fixes-simple.md` explains each one. Can you review and apply it?
