"""TC-CHK: unit tests for the checking helpers used to judge real output."""
import unittest

from tests._bootstrap import TASK5_ROOT  # noqa: F401
import validation_checks as vc

SOURCES = [
    {"title": "Indian EdTech market", "url": "https://a.in/x",
     "content": "BYJU'S and Vedantu lead. The market is worth $5 billion with 20% growth."},
    {"title": "Farm sensors", "url": "https://b.in/y", "content": "Soil sensors help farmers."},
]


class UrlChecks(unittest.TestCase):
    def test_valid_urls(self):
        for u in ("https://a.in/x", "http://www.site.com/a?b=1"):
            self.assertTrue(vc.is_valid_http_url(u), u)

    def test_invalid_urls(self):
        for u in ("", "ftp://a.in", "javascript:alert(1)", "https://", "https://localhost",
                  "not a url", None):
            self.assertFalse(vc.is_valid_http_url(u), u)

    def test_placeholder_detection(self):
        self.assertTrue(vc.is_placeholder_url("https://example.com/market-research"))
        self.assertFalse(vc.is_placeholder_url("https://economictimes.com/a"))

    def test_check_sources_flags_problems(self):
        info = vc.check_sources([
            {"url": "https://a.in/x", "content": "ok"},
            {"url": "https://a.in/x", "content": ""},
            {"url": "", "content": "ok"},
        ])
        self.assertEqual(info["invalid_urls"], [""])
        self.assertEqual(info["duplicate_urls"], ["https://a.in/x"])
        self.assertEqual(len(info["empty_content"]), 1)


class RelevanceAndGrounding(unittest.TestCase):
    def test_relevance_score(self):
        self.assertEqual(vc.relevance_score(SOURCES, ["farmer"]), 0.5)
        self.assertEqual(vc.relevance_score(SOURCES, ["market", "farmer"]), 1.0)
        self.assertEqual(vc.relevance_score([], ["x"]), 0.0)

    def test_ungrounded_statistics_detects_invented_numbers(self):
        analysis = "The market is worth $5 billion, but will reach 87% adoption and ₹4,500 crore."
        flagged = vc.ungrounded_statistics(analysis, SOURCES)
        self.assertTrue(any("87" in f for f in flagged), flagged)
        self.assertTrue(any("4,500" in f for f in flagged), flagged)
        self.assertFalse(any("5 billion" in f for f in flagged), flagged)

    def test_small_plain_numbers_are_not_flagged(self):
        self.assertEqual(vc.ungrounded_statistics("Interview 10 customers and list 3 risks", SOURCES), [])

    def test_ungrounded_company_names(self):
        analysis = "Direct competitors: BYJU'S and Vedantu. Also FakeLearn Pvt competes."
        flagged = vc.ungrounded_company_names(analysis, SOURCES)
        self.assertTrue(any("FakeLearn" in f for f in flagged), flagged)
        self.assertFalse(any("Vedantu" in f for f in flagged), flagged)


class FormatChecks(unittest.TestCase):
    def test_good_report(self):
        rep = {k: {"a": 1} for k in ("market_analysis", "competitor_analysis",
                                      "swot_and_risks", "mvp_recommendation")}
        rep.update(startup_idea={}, sources=[], final_summary="text")
        self.assertEqual(vc.check_report_format(rep), [])

    def test_bad_report(self):
        probs = vc.check_report_format({"market_analysis": {}, "final_summary": " "})
        self.assertTrue(any("missing section" in p for p in probs))
        self.assertTrue(any("market_analysis must be" in p for p in probs))
        self.assertTrue(any("final_summary" in p for p in probs))


if __name__ == "__main__":
    unittest.main()
