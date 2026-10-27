"""TC-API: FastAPI endpoint behaviour (mock mode)."""
import contextlib
import io
import json
import os
import unittest
from unittest import mock

from tests._bootstrap import TASK5_ROOT, known_bug  # noqa: F401

try:
    from fastapi.testclient import TestClient
    from app.main import app
    from app.schemas import ValidationReport
    HAVE_CLIENT = True
except Exception as exc:  # httpx missing etc.
    HAVE_CLIENT = False
    SKIP_REASON = f"fastapi TestClient unavailable: {exc}"

IDEAS = json.loads((TASK5_ROOT / "test_data" / "startup_ideas.json").read_text(encoding="utf-8"))


@unittest.skipUnless(HAVE_CLIENT, "fastapi TestClient unavailable (pip install httpx)")
class ApiTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_api01_home(self):
        r = self.client.get("/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["validation_endpoint"], "/validate")

    def test_api02_validate_each_domain(self):
        for case in IDEAS:
            with self.subTest(case=case["id"]):
                r = self.client.post("/validate", json=case["idea"])
                self.assertEqual(r.status_code, 200, r.text)
                self.assertTrue(r.headers["content-type"].startswith("application/json"))
                ValidationReport.model_validate(r.json())  # response matches schema

    def test_api03_missing_field_returns_422(self):
        bad = {k: v for k, v in IDEAS[0]["idea"].items() if k != "industry"}
        r = self.client.post("/validate", json=bad)
        self.assertEqual(r.status_code, 422)
        self.assertEqual(r.json()["detail"][0]["loc"][-1], "industry")

    def test_api04_empty_body_returns_422(self):
        self.assertEqual(self.client.post("/validate", json={}).status_code, 422)

    def test_api05_invalid_json_returns_422(self):
        r = self.client.post("/validate", content="{not json",
                             headers={"content-type": "application/json"})
        self.assertEqual(r.status_code, 422)

    def test_api06_wrong_method_and_unknown_route(self):
        self.assertEqual(self.client.get("/validate").status_code, 405)
        self.assertEqual(self.client.get("/nope").status_code, 404)

    def test_api07_workflow_error_returns_502_without_leaking_details(self):
        secret = "sk-SECRET-123"
        with mock.patch("app.main.run_validation_workflow",
                        side_effect=RuntimeError(f"auth failed key={secret}")):
            r = self.client.post("/validate", json=IDEAS[0]["idea"])
        self.assertEqual(r.status_code, 502)
        self.assertNotIn(secret, r.text)

    @known_bug("BUG-05", "full exception text (which can contain API keys) is printed to the server log")
    def test_api07b_secrets_are_not_written_to_server_log(self):
        secret = "sk-SECRET-123"
        buf = io.StringIO()
        with mock.patch("app.main.run_validation_workflow",
                        side_effect=RuntimeError(f"auth failed key={secret}")), \
             contextlib.redirect_stdout(buf):
            self.client.post("/validate", json=IDEAS[0]["idea"])
        self.assertNotIn(secret, buf.getvalue())

    def test_api08_missing_keys_in_live_mode_returns_502(self):
        env = {"USE_MOCKS": "false", "TAVILY_API_KEY": "", "LLM_API_KEY": ""}
        with mock.patch.dict(os.environ, env):
            r = self.client.post("/validate", json=IDEAS[0]["idea"])
        self.assertEqual(r.status_code, 502)

    def test_api09_unicode_payload(self):
        idea = {**IDEAS[0]["idea"], "name": "शिक्षा साथी",
                "description": "ग्रामीण छात्रों के लिए एआई शिक्षक ऐप"}
        r = self.client.post("/validate", json=idea)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["startup_idea"]["name"], "शिक्षा साथी")

    def test_api10_large_description_is_handled(self):
        idea = {**IDEAS[0]["idea"], "description": "AI tutor for students. " * 2000}
        self.assertEqual(self.client.post("/validate", json=idea).status_code, 200)

    def test_api11_openapi_docs_available(self):
        self.assertEqual(self.client.get("/openapi.json").status_code, 200)
        self.assertEqual(self.client.get("/docs").status_code, 200)


if __name__ == "__main__":
    unittest.main()
