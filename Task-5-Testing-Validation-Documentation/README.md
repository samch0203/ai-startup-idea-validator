# Task 5: Testing, Validation and Documentation

Part of the AI-Based Startup Idea Validator with Market Analysis Assistance project.
Tests the Task 4 multi-agent pipeline.

**Quick summary: see [TASK5-SUMMARY.md](TASK5-SUMMARY.md).**

## What this folder contains
```text
tests/                       automated tests (56 test cases)
  test_schema_validation.py    input validation
  test_pipeline.py             4 domains end to end, agent order, data hand-over
  test_live_mode_mocked.py     live-mode code paths with fake Tavily/LLM (no keys needed)
  test_api.py                  FastAPI endpoint behaviour
  test_validation_checks.py    self-tests of the checking helpers
  _bootstrap.py                finds the Task 4 code; `known_bug` marker
scripts/
  run_domain_validation.py     runs the 4 domain ideas and checks format, URLs, relevance, grounding
  validation_checks.py         the reusable checks
test_data/startup_ideas.json   EdTech, Healthcare, AgriTech, RetailTech test ideas
docs/testing/
  test-plan.md                 scope, approach, pass criteria, all test cases
  test-results.md              results and the live-mode template to fill in
  bug-report.md                5 bugs + 4 observations, with fixes
  bugs-and-fixes-simple.md     simple guide: what, where, how to fix, how to check
fixes/task4-fixes.patch        fixes for the 5 bugs (apply to the Task 4 code)
results/                       saved run outputs (unit test log, mock domain run)
requirements-dev.txt
```

## How to run
Put this folder next to the Task 4 folder (or anywhere, then set `VALIDATOR_APP_PATH`):
```text
repo/
  Task-4-Multi-Agent-Architecture/
  Task-5-Testing-Validation-Documentation/
```

PowerShell:
```powershell
cd Task-4-Multi-Agent-Architecture
.\.venv\Scripts\Activate.ps1
pip install -r ..\Task-5-Testing-Validation-Documentation\requirements-dev.txt

cd ..\Task-5-Testing-Validation-Documentation
python -m unittest discover -s tests -t . -v        # automated tests, no API keys needed
python scripts\run_domain_validation.py             # 4 domains, mock mode
```
If the Task 4 folder has a different name or location:
`$env:VALIDATOR_APP_PATH = "C:\path\to\Task-4-Multi-Agent-Architecture"`

`pytest` also works: `pip install pytest` then `pytest tests`.

### Expected result on the original Task 4 code
`Ran 56 tests ... OK (skipped=6)`. The 6 skipped tests are open bugs (BUG-01 to BUG-05).

### Apply the fixes and re-test
```powershell
cd ..\Task-4-Multi-Agent-Architecture
git apply ..\Task-5-Testing-Validation-Documentation\fixes\task4-fixes.patch
cd ..\Task-5-Testing-Validation-Documentation
$env:EXPECT_FIXES = "1"
python -m unittest discover -s tests -t .            # expected: Ran 56 tests ... OK
```
Tell the Task 4 owner before changing their files; the patch is a suggestion.

### Live-mode validation (needs real API keys - not performed)
With a configured `.env` (`USE_MOCKS=false`, `LLM_API_KEY`, `LLM_MODEL`, `TAVILY_API_KEY`) run
`python scripts\run_domain_validation.py --check-urls`. Never commit `.env` or API keys.

## Status
| Item | Status |
|---|---|
| Automated tests, mock + offline live wiring | Done, results documented |
| Bugs found / fixes | 5 bugs documented, patch provided and verified against the tests |
| Live-mode relevance/accuracy testing | Not performed (no API keys); runner script provided |
