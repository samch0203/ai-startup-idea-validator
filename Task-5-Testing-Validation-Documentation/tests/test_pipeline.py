"""TC-PIPE / TC-DOM: pipeline execution for each startup domain (mock mode)."""
import json
import unittest
from pathlib import Path
from unittest import mock

from tests._bootstrap import TASK5_ROOT  # noqa: F401  (sets sys.path)
from app import orchestrator
from app.schemas import StartupIdea, ValidationReport
import validation_checks as vc

IDEAS = json.loads((TASK5_ROOT / "test_data" / "startup_ideas.json").read_text(encoding="utf-8"))


class DomainPipelineTests(unittest.TestCase):
    def test_dom01_all_domains_run_end_to_end(self):
        for case in IDEAS:
            with self.subTest(case=case["id"], domain=case["domain"]):
                idea = StartupIdea(**case["idea"])
                report = orchestrator.run_validation_workflow(idea)
                self.assertIsInstance(report, ValidationReport)
                data = json.loads(report.model_dump_json())
                self.assertEqual(vc.check_report_format(data), [])

    def test_dom02_report_echoes_the_submitted_idea(self):
        for case in IDEAS:
            with self.subTest(case=case["id"]):
                report = orchestrator.run_validation_workflow(StartupIdea(**case["idea"]))
                self.assertEqual(report.startup_idea.name, case["idea"]["name"])
                self.assertEqual(report.startup_idea.industry, case["domain"])

    def test_dom03_final_summary_mentions_startup_name(self):
        for case in IDEAS:
            with self.subTest(case=case["id"]):
                report = orchestrator.run_validation_workflow(StartupIdea(**case["idea"]))
                self.assertIn(case["idea"]["name"], report.final_summary)

    def test_dom04_market_analysis_uses_the_target_market(self):
        for case in IDEAS:
            with self.subTest(case=case["id"]):
                report = orchestrator.run_validation_workflow(StartupIdea(**case["idea"]))
                self.assertEqual(report.market_analysis["target_customers"],
                                 case["idea"]["target_market"])

    def test_dom05_sources_are_labelled_with_the_domain(self):
        for case in IDEAS:
            with self.subTest(case=case["id"]):
                report = orchestrator.run_validation_workflow(StartupIdea(**case["idea"]))
                titles = " ".join(s.title for s in report.sources)
                self.assertIn(case["domain"], titles)

    def test_dom06_mock_output_is_honest_about_being_unverified(self):
        """Mock mode must never present itself as verified market data."""
        report = orchestrator.run_validation_workflow(StartupIdea(**IDEAS[0]["idea"]))
        self.assertIn("mock", report.market_analysis["evidence_limit"].lower())
        self.assertIn("mock", report.competitor_analysis["evidence_limit"].lower())
        self.assertIn("not proof", report.final_summary.lower())


class OrchestrationOrderTests(unittest.TestCase):
    """The agents must run in the documented order and pass data forward."""

    def test_pipe01_order_and_data_handover(self):
        idea = StartupIdea(**IDEAS[0]["idea"])
        calls = []
        real = {n: getattr(orchestrator, n) for n in (
            "web_search_agent", "market_analysis_agent", "competitor_analysis_agent",
            "swot_risk_agent", "mvp_recommendation_agent", "report_generation_agent")}

        def spy(name):
            def inner(*args, **kwargs):
                calls.append((name, args))
                return real[name](*args, **kwargs)
            return inner

        patches = [mock.patch.object(orchestrator, n, spy(n)) for n in real]
        for p in patches:
            p.start()
        try:
            report = orchestrator.run_validation_workflow(idea)
        finally:
            for p in patches:
                p.stop()

        self.assertEqual([c[0] for c in calls], [
            "web_search_agent", "market_analysis_agent", "competitor_analysis_agent",
            "swot_risk_agent", "mvp_recommendation_agent", "report_generation_agent"])

        by_name = {n: a for n, a in calls}
        # market and competitor agents receive the search results
        self.assertEqual(by_name["market_analysis_agent"][1], report.sources)
        self.assertEqual(by_name["competitor_analysis_agent"][1], report.sources)
        # SWOT receives both analyses
        self.assertEqual(by_name["swot_risk_agent"][1], report.market_analysis)
        self.assertEqual(by_name["swot_risk_agent"][2], report.competitor_analysis)
        # MVP receives market analysis + SWOT
        self.assertEqual(by_name["mvp_recommendation_agent"][1], report.market_analysis)
        self.assertEqual(by_name["mvp_recommendation_agent"][2], report.swot_and_risks)
        # report agent receives all five outputs
        self.assertEqual(len(by_name["report_generation_agent"]), 5)

    def test_pipe02_failure_in_one_agent_stops_pipeline(self):
        idea = StartupIdea(**IDEAS[0]["idea"])
        with mock.patch.object(orchestrator, "swot_risk_agent", side_effect=RuntimeError("boom")), \
             mock.patch.object(orchestrator, "mvp_recommendation_agent") as mvp:
            with self.assertRaises(RuntimeError):
                orchestrator.run_validation_workflow(idea)
            mvp.assert_not_called()

    def test_pipe03_repeated_runs_are_independent(self):
        a = orchestrator.run_validation_workflow(StartupIdea(**IDEAS[0]["idea"]))
        b = orchestrator.run_validation_workflow(StartupIdea(**IDEAS[2]["idea"]))
        self.assertNotEqual(a.startup_idea.name, b.startup_idea.name)
        self.assertNotIn(IDEAS[0]["idea"]["name"], b.final_summary)


class MockModeFindingsTests(unittest.TestCase):
    """Documented limitations of mock mode (see bug-report OBS-xx)."""

    def test_obs01_mock_competitor_analysis_is_identical_across_domains(self):
        outs = [json.dumps(orchestrator.run_validation_workflow(
            StartupIdea(**c["idea"])).competitor_analysis, sort_keys=True) for c in IDEAS]
        # Documents current behaviour: mock mode cannot show domain relevance.
        self.assertEqual(len(set(outs)), 1)

    def test_obs02_mock_sources_are_placeholder_urls(self):
        report = orchestrator.run_validation_workflow(StartupIdea(**IDEAS[0]["idea"]))
        info = vc.check_sources([s.model_dump() for s in report.sources])
        self.assertEqual(info["invalid_urls"], [])
        self.assertEqual(len(info["placeholder_urls"]), len(report.sources))


if __name__ == "__main__":
    unittest.main()
