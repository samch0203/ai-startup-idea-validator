"""TC-SCH: input validation of the StartupIdea schema."""
import unittest

from tests._bootstrap import known_bug
from pydantic import ValidationError
from app.schemas import StartupIdea

VALID = dict(
    name="VidyaBuddy",
    description="An AI tutor app for school students in India.",
    target_market="Class 8-10 students",
    industry="EdTech",
)


class SchemaTests(unittest.TestCase):
    def test_sch01_valid_idea_gets_defaults(self):
        idea = StartupIdea(**VALID)
        self.assertEqual(idea.location, "India")
        self.assertEqual(idea.budget, "Not specified")

    def test_sch02_missing_required_fields_rejected(self):
        for field in ("name", "description", "target_market", "industry"):
            data = {k: v for k, v in VALID.items() if k != field}
            with self.subTest(missing=field):
                with self.assertRaises(ValidationError):
                    StartupIdea(**data)

    def test_sch03_too_short_values_rejected(self):
        cases = {"name": "A", "description": "too short", "target_market": "x", "industry": "y"}
        for field, bad in cases.items():
            with self.subTest(field=field):
                with self.assertRaises(ValidationError):
                    StartupIdea(**{**VALID, field: bad})

    def test_sch04_wrong_types_rejected(self):
        with self.assertRaises(ValidationError):
            StartupIdea(**{**VALID, "name": 12345})

    def test_sch05_unicode_input_accepted(self):
        idea = StartupIdea(**{**VALID, "name": "शिक्षा साथी",
                              "description": "ग्रामीण छात्रों के लिए एआई शिक्षक ऐप"})
        self.assertEqual(idea.name, "शिक्षा साथी")

    @known_bug("BUG-01", "whitespace-only text passes min_length validation")
    def test_sch06_whitespace_only_description_rejected(self):
        with self.assertRaises(ValidationError):
            StartupIdea(**{**VALID, "description": " " * 15})

    @known_bug("BUG-01", "whitespace-only text passes min_length validation")
    def test_sch07_whitespace_only_name_rejected(self):
        with self.assertRaises(ValidationError):
            StartupIdea(**{**VALID, "name": "   "})


if __name__ == "__main__":
    unittest.main()
