#!/usr/bin/env python3
"""Run the startup-validator pipeline on ideas from several domains and check
the output (format, source URLs, relevance, grounding, timing).

Usage (from the Task 4 project root, or set VALIDATOR_APP_PATH):

    # Mock mode (default, no keys needed) - checks pipeline + format only
    python Task-5-Testing-Validation-Documentation/scripts/run_domain_validation.py

    # Live mode - checks real search/LLM output. Needs .env with real keys:
    #   USE_MOCKS=false  LLM_API_KEY=...  LLM_MODEL=...  TAVILY_API_KEY=...
    python .../run_domain_validation.py --check-urls

Options:
    --ideas FILE      JSON file with test ideas (default: test_data/startup_ideas.json)
    --only ID         run just one case id, e.g. AGRI-01 (repeatable)
    --check-urls      send a real HTTP request to every source URL (needs internet)
    --min-relevance X minimum share of sources that must match domain keywords (default 0.6)
    --out DIR         where to write results (default: results/)

Exit code is 0 only when every case passes every *applicable* check.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
TASK5_ROOT = HERE.parent
sys.path.insert(0, str(HERE))


def _find_app_root() -> Path:
    cands = []
    if os.getenv("VALIDATOR_APP_PATH"):
        cands.append(Path(os.environ["VALIDATOR_APP_PATH"]))
    cands += [Path.cwd(), TASK5_ROOT, TASK5_ROOT.parent,
              TASK5_ROOT.parent / "Task-4-Multi-Agent-Architecture"]
    for c in cands:
        if (c / "app" / "orchestrator.py").exists():
            return c
    sys.exit("Cannot find the Task 4 `app/` package. Run from the Task 4 root "
             "or set VALIDATOR_APP_PATH.")


APP_ROOT = _find_app_root()
sys.path.insert(0, str(APP_ROOT))
os.chdir(APP_ROOT)  # so python-dotenv finds the .env of the Task 4 project

import validation_checks as vc  # noqa: E402
from app import agents, orchestrator  # noqa: E402
from app.schemas import StartupIdea  # noqa: E402


def timed_agents() -> dict[str, float]:
    """Wrap each agent so we can report how long it took."""
    timings: dict[str, float] = {}
    for name in ("web_search_agent", "market_analysis_agent", "competitor_analysis_agent",
                 "swot_risk_agent", "mvp_recommendation_agent", "report_generation_agent"):
        original = getattr(orchestrator, name)

        def make(fn, label):
            def inner(*a, **k):
                t0 = time.perf_counter()
                try:
                    return fn(*a, **k)
                finally:
                    timings[label] = round(time.perf_counter() - t0, 2)
            return inner

        setattr(orchestrator, name, make(original, name))
    return timings


def run_case(case: dict, mock_mode: bool, args, timings: dict) -> dict:
    result = {"id": case["id"], "domain": case["domain"], "name": case["idea"]["name"],
              "checks": {}, "notes": [], "error": None}
    timings.clear()
    t0 = time.perf_counter()
    try:
        report = orchestrator.run_validation_workflow(StartupIdea(**case["idea"]))
    except Exception as exc:  # noqa: BLE001
        result["error"] = f"{type(exc).__name__}: {exc}"
        result["checks"]["pipeline_ran"] = False
        return result
    result["total_seconds"] = round(time.perf_counter() - t0, 2)
    result["agent_seconds"] = dict(timings)
    data = json.loads(report.model_dump_json())
    result["report"] = data
    result["checks"]["pipeline_ran"] = True

    # 1. output format
    problems = vc.check_report_format(data)
    result["checks"]["format"] = not problems
    result["notes"] += [f"format: {p}" for p in problems]

    # 2. source URLs
    info = vc.check_sources(data["sources"])
    result["source_info"] = info
    result["checks"]["sources_present"] = info["count"] > 0
    result["checks"]["urls_valid_syntax"] = not info["invalid_urls"]
    result["checks"]["no_duplicate_urls"] = not info["duplicate_urls"]
    if mock_mode:
        result["notes"].append("urls: placeholder example.com links are EXPECTED in mock mode")
    else:
        result["checks"]["urls_not_placeholder"] = not info["placeholder_urls"]
    if args.check_urls and not mock_mode:
        reach = {}
        for s in data["sources"]:
            ok, detail = vc.check_url_reachable(s["url"])
            reach[s["url"]] = {"ok": ok, "detail": detail}
        result["url_reachability"] = reach
        result["checks"]["urls_reachable"] = all(v["ok"] for v in reach.values()) if reach else False

    # 3. relevance + grounding (only meaningful with real data)
    if mock_mode:
        result["notes"].append("relevance/grounding: skipped in mock mode (no real research)")
    else:
        score = vc.relevance_score(data["sources"], case["domain_keywords"])
        result["relevance_score"] = round(score, 2)
        result["checks"]["sources_relevant"] = score >= args.min_relevance
        comp = data["competitor_analysis"]
        mkt = data["market_analysis"]
        result["ungrounded_statistics"] = vc.ungrounded_statistics(
            [mkt, comp, data["final_summary"]], data["sources"])
        result["ungrounded_company_names"] = vc.ungrounded_company_names(
            comp, data["sources"], case["idea"]["name"])
        result["checks"]["no_ungrounded_statistics"] = not result["ungrounded_statistics"]
        # names are only a *warning*: needs a human to review
        if result["ungrounded_company_names"]:
            result["notes"].append(
                "review: company names not found in sources -> "
                + ", ".join(result["ungrounded_company_names"][:15]))
        text = json.dumps(comp).lower()
        hint_hits = [h for h in case.get("expected_competitors_hint", []) if h.lower() in text]
        result["expected_competitors_mentioned"] = hint_hits
    return result


def write_markdown(results: list[dict], mode: str, path: Path) -> None:
    lines = [f"# Domain validation run - {mode.upper()} mode",
             f"Run at: {dt.datetime.now().isoformat(timespec='seconds')}", ""]
    all_checks = sorted({c for r in results for c in r["checks"]})
    lines += ["| Case | Domain | " + " | ".join(all_checks) + " | Time (s) |",
              "|---|---|" + "|".join(["---"] * len(all_checks)) + "|---|"]
    for r in results:
        cells = []
        for c in all_checks:
            v = r["checks"].get(c)
            cells.append("n/a" if v is None else ("PASS" if v else "FAIL"))
        lines.append(f"| {r['id']} | {r['domain']} | " + " | ".join(cells)
                     + f" | {r.get('total_seconds', '-')} |")
    lines.append("")
    for r in results:
        lines.append(f"## {r['id']} - {r['name']} ({r['domain']})")
        if r["error"]:
            lines.append(f"- **Pipeline error:** `{r['error']}`")
        for k in ("relevance_score", "expected_competitors_mentioned",
                  "ungrounded_statistics", "ungrounded_company_names"):
            if k in r:
                lines.append(f"- {k}: {r[k]}")
        for n in r["notes"]:
            lines.append(f"- {n}")
        for u, v in r.get("url_reachability", {}).items():
            lines.append(f"- URL {'OK' if v['ok'] else 'BAD'} ({v['detail']}): {u}")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ideas", default=str(TASK5_ROOT / "test_data" / "startup_ideas.json"))
    ap.add_argument("--only", action="append")
    ap.add_argument("--check-urls", action="store_true")
    ap.add_argument("--min-relevance", type=float, default=0.6)
    ap.add_argument("--out", default=str(TASK5_ROOT / "results"))
    args = ap.parse_args()

    cases = json.loads(Path(args.ideas).read_text(encoding="utf-8"))
    if args.only:
        cases = [c for c in cases if c["id"] in args.only]
        if not cases:
            sys.exit("No matching case ids.")

    mock_mode = agents.use_mocks()
    mode = "mock" if mock_mode else "live"
    print(f"Mode: {mode.upper()}   cases: {len(cases)}")
    timings = timed_agents()

    results = []
    for case in cases:
        print(f"- {case['id']:<10} {case['domain']:<11}", end=" ", flush=True)
        r = run_case(case, mock_mode, args, timings)
        failed = [k for k, v in r["checks"].items() if v is False]
        print("PASS" if not failed and not r["error"] else f"FAIL {failed or r['error']}")
        results.append(r)

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    json_path = out / f"validation_{mode}_{stamp}.json"
    md_path = out / f"validation_{mode}_{stamp}.md"
    json_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    write_markdown(results, mode, md_path)
    print(f"\nWrote {md_path}\n      {json_path}")

    bad = [r for r in results if r["error"] or any(v is False for v in r["checks"].values())]
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
