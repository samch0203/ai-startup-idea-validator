"""TC-LIVE: live-mode code paths, exercised offline with fake Tavily/LLM clients.

No network and no API keys are used. These tests prove the wiring (queries,
prompts, error handling, source handling). They do NOT prove the quality of
real search/LLM output - use scripts/run_domain_validation.py for that.
"""
import os
import unittest
from unittest import mock

from tests._bootstrap import known_bug, TASK5_ROOT  # noqa: F401
import json
from app import agents, orchestrator
from app.schemas import StartupIdea

IDEAS = json.loads((TASK5_ROOT / "test_data" / "startup_ideas.json").read_text(encoding="utf-8"))
IDEA = StartupIdea(**IDEAS[2]["idea"])  # AgriTech

LIVE_ENV = {"USE_MOCKS": "false", "TAVILY_API_KEY": "tvly-fake",
            "LLM_API_KEY": "sk-fake", "LLM_MODEL": "fake-model"}


class FakeTavily:
    results = [
        {"title": "AgriTech in India", "url": "https://example-agri.in/report",
         "content": "DeHaat and CropIn serve farmers across India."},
        {"title": "Soil sensors", "url": "https://agri-news.in/soil",
         "content": "Soil moisture sensors help farmers save water."},
    ]
    last_query = None

    def __init__(self, api_key=None):
        self.api_key = api_key

    def search(self, query, max_results=5):
        FakeTavily.last_query = query
        return {"results": FakeTavily.results}


class LiveModeTests(unittest.TestCase):
    def setUp(self):
        p = mock.patch.dict(os.environ, LIVE_ENV)
        p.start()
        self.addCleanup(p.stop)
        t = mock.patch.object(agents, "TavilyClient", FakeTavily)
        t.start()
        self.addCleanup(t.stop)
        FakeTavily.results = [
            {"title": "AgriTech in India", "url": "https://example-agri.in/report",
             "content": "DeHaat and CropIn serve farmers across India."},
            {"title": "Soil sensors", "url": "https://agri-news.in/soil",
             "content": "Soil moisture sensors help farmers save water."},
        ]

    # ---- search agent ----------------------------------------------------
    def test_live01_search_query_contains_idea_context(self):
        agents.web_search_agent(IDEA)
        q = FakeTavily.last_query.lower()
        for word in ("agritech", "india", "competitors"):
            self.assertIn(word, q)

    def test_live02_search_results_are_converted_to_schema(self):
        res = agents.web_search_agent(IDEA)
        self.assertEqual([r.url for r in res],
                         ["https://example-agri.in/report", "https://agri-news.in/soil"])

    def test_live03_missing_tavily_key_gives_clear_error(self):
        with mock.patch.dict(os.environ, {"TAVILY_API_KEY": ""}):
            with self.assertRaises(RuntimeError) as cm:
                agents.web_search_agent(IDEA)
        self.assertIn("TAVILY_API_KEY", str(cm.exception))

    @known_bug("BUG-02", "search results with empty/invalid URLs are passed through as sources")
    def test_live04_results_with_invalid_urls_are_dropped(self):
        FakeTavily.results = [
            {"title": "No url", "url": "", "content": "x"},
            {"title": "Bad scheme", "url": "javascript:alert(1)", "content": "x"},
            {"title": "Good", "url": "https://good.in/a", "content": "ok"},
        ]
        res = agents.web_search_agent(IDEA)
        self.assertEqual([r.url for r in res], ["https://good.in/a"])

    def test_live05_missing_title_gets_default(self):
        FakeTavily.results = [{"url": "https://a.in/x", "content": "c"}]
        self.assertEqual(agents.web_search_agent(IDEA)[0].title, "Untitled")

    # ---- LLM agents ------------------------------------------------------
    def test_live06_missing_llm_key_gives_clear_error(self):
        with mock.patch.dict(os.environ, {"LLM_API_KEY": ""}):
            with self.assertRaises(RuntimeError) as cm:
                agents.ask_llm("sys", "user")
        self.assertIn("LLM_API_KEY", str(cm.exception))

    def test_live07_competitor_prompt_contains_research_and_idea(self):
        sources = agents.web_search_agent(IDEA)
        with mock.patch.object(agents, "ask_llm", return_value="ok") as llm:
            agents.competitor_analysis_agent(IDEA, sources)
        system, user = llm.call_args[0]
        self.assertIn("Do not claim a company", system)
        self.assertIn("KisanSense", user)
        self.assertIn("https://example-agri.in/report", user)
        self.assertIn("DeHaat", user)

    def test_live08_market_prompt_forbids_invented_statistics(self):
        sources = agents.web_search_agent(IDEA)
        with mock.patch.object(agents, "ask_llm", return_value="ok") as llm:
            agents.market_analysis_agent(IDEA, sources)
        self.assertIn("Do not invent statistics", llm.call_args[0][0])

    def test_live09_full_pipeline_with_fake_llm(self):
        with mock.patch.object(agents, "ask_llm", side_effect=lambda s, u: f"LLM:{s[:20]}"):
            report = orchestrator.run_validation_workflow(IDEA)
        self.assertEqual(len(report.sources), 2)
        for section in (report.market_analysis, report.competitor_analysis,
                        report.swot_and_risks):
            self.assertIsInstance(section["analysis"], str)
        self.assertIn("recommendation", report.mvp_recommendation)
        self.assertTrue(report.final_summary.startswith("LLM:"))

    def test_live10_llm_receives_previous_agent_outputs(self):
        prompts = []
        def fake(system, user):
            prompts.append(user)
            return "ANALYSIS_TEXT"
        with mock.patch.object(agents, "ask_llm", side_effect=fake):
            orchestrator.run_validation_workflow(IDEA)
        # prompts order: market, competitor, swot, mvp, report
        self.assertIn("ANALYSIS_TEXT", prompts[2])   # swot sees market+competitor
        self.assertIn("ANALYSIS_TEXT", prompts[3])   # mvp sees market+swot
        self.assertEqual(prompts[4].count("ANALYSIS_TEXT") >= 4, True)  # report sees all

    @known_bug("BUG-03", "with zero search results the LLM is still asked to analyse (hallucination risk)")
    def test_live11_no_search_results_does_not_call_llm_for_analysis(self):
        FakeTavily.results = []
        with mock.patch.object(agents, "ask_llm", return_value="made up competitors") as llm:
            out_m = agents.market_analysis_agent(IDEA, [])
            out_c = agents.competitor_analysis_agent(IDEA, [])
        llm.assert_not_called()
        self.assertIn("evidence_limit", out_m)
        self.assertIn("evidence_limit", out_c)

    def test_obs03_live_output_shape_differs_from_mock_shape(self):
        """Documents OBS-03: live agents return {'analysis': <free text>} while
        mock agents return structured keys. Front-end must handle both."""
        sources = agents.web_search_agent(IDEA)
        with mock.patch.object(agents, "ask_llm", return_value="text"):
            live = agents.market_analysis_agent(IDEA, sources)
        with mock.patch.dict(os.environ, {"USE_MOCKS": "true"}):
            mocked = agents.market_analysis_agent(IDEA, [])
        self.assertEqual(list(live), ["analysis"])
        self.assertNotEqual(set(live), set(mocked))


class UseMocksFlagTests(unittest.TestCase):
    def _flag(self, value):
        with mock.patch.dict(os.environ, {"USE_MOCKS": value}):
            return agents.use_mocks()

    def test_flag01_documented_values(self):
        self.assertTrue(self._flag("true"))
        self.assertTrue(self._flag("TRUE"))
        self.assertFalse(self._flag("false"))
        self.assertFalse(self._flag("False"))

    def test_flag02_default_is_mock(self):
        env = {k: v for k, v in os.environ.items() if k != "USE_MOCKS"}
        with mock.patch.dict(os.environ, env, clear=True):
            self.assertTrue(agents.use_mocks())

    @known_bug("BUG-04", "USE_MOCKS=1 / ' true' / 'yes' silently switches to LIVE mode")
    def test_flag03_truthy_variants_stay_in_mock_mode(self):
        for v in ("1", "yes", " true", "true "):
            self.assertTrue(self._flag(v), f"USE_MOCKS={v!r} should stay in mock mode")

    def test_flag04_explicit_false_variants_enable_live(self):
        for v in ("false", "0", "no"):
            self.assertFalse(self._flag(v), f"USE_MOCKS={v!r} should enable live mode")


if __name__ == "__main__":
    unittest.main()
