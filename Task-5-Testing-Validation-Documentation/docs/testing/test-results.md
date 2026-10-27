# Test Results - Task 5

Run date: 27 Oct 2026. Code under test: Task 4 zip as received.

## Summary
- 56 automated test cases. **56 of 56 pass with the proposed fixes applied.** On the Task 4 code as
  received, 50 pass and 6 report the 5 documented bugs (BUG-01 to BUG-05).
- The same results were reproduced on the tester's own Windows machine (Python 3.13):
  `Ran 56 tests ... OK (skipped=6)` on the original code, and the 4-domain mock run passed 4 of 4.
- Live-mode relevance/accuracy testing was not performed (no API keys) - see section 4.

## 1. Automated test suite

| Configuration | Tests run | Passed | Skipped (open known bugs) | Failed |
|---|---|---|---|---|
| Original Task 4 code | 56 | 50 | 6 (BUG-01 x2, BUG-02, BUG-03, BUG-04, BUG-05) | 0 |
| After `fixes/task4-fixes.patch`, run with `EXPECT_FIXES=1` | 56 | 56 | 0 | 0 |

Full logs: `results/unit-test-run.txt`.
Reading the first row: the 6 skipped tests are real bugs, not tests that were left out. Each one
checks the *correct* behaviour and fails on the original code (see `bug-report.md`).

## 2. Domain runs - mock mode (executed)
Command: `python scripts/run_domain_validation.py` (files in `results/validation_mock_*.md/json`).

| Case | Domain | Pipeline | Format | Sources | URL syntax | No duplicates | Time |
|---|---|---|---|---|---|---|---|
| EDTECH-01 | EdTech | PASS | PASS | PASS (2) | PASS | PASS | <0.1 s |
| HEALTH-01 | Healthcare | PASS | PASS | PASS (2) | PASS | PASS | <0.1 s |
| AGRI-01 | AgriTech | PASS | PASS | PASS (2) | PASS | PASS | <0.1 s |
| RETAIL-01 | RetailTech | PASS | PASS | PASS (2) | PASS | PASS | <0.1 s |

Conclusion: the orchestration, schemas and API work for all four domains. In mock mode the sources
are `example.com` placeholders and the analysis text is fixed, so **relevance and accuracy of
market and competitor findings could not be assessed in mock mode** (OBS-01, OBS-02).

## 3. Offline checks of the live code path (executed)
`tests/test_live_mode_mocked.py` runs the real live-mode code with fake Tavily/LLM clients. It
confirmed: the search query includes industry, location and "competitors"; results map correctly
into `SearchResult`; prompts contain the idea, the research URLs and the "do not invent" guard
rails; each agent's output is passed to the next agent; missing-key errors are clear. It also found
BUG-02, BUG-03 and BUG-04.

The runner's live-mode checks were exercised the same way with a deliberately bad fake answer
(an irrelevant source, an invented "87 %" / "Rs 4,500 crore" and an invented company
"FakeLearn Pvt"): the runner reported relevance 0.5 (FAIL), listed both statistics as ungrounded
(FAIL) and flagged the invented company for review, while correctly accepting BYJU'S and Vedantu
that were present in the fake source. This shows the checks work; it is **not** a result about
real search or LLM quality.

## 4. Scope and limitations
Live-mode validation (real Tavily search and a real LLM) was **not performed**, because real API
keys were not available. The relevance and accuracy of real market and competitor findings is
therefore not assessed in this report. The tooling is ready: with a configured `.env`
(`USE_MOCKS=false` plus the three keys), run

```
python scripts\run_domain_validation.py --check-urls
```

to check format, URL validity and reachability, relevance, and ungrounded statistics for all four
domains, and spot-check 3 competitors and 3 statistics per domain by hand.
