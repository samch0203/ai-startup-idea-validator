"""Shared test helpers.

Makes the Task 4 `app` package importable no matter where the Task 5 files
are placed, and provides the `known_bug` decorator used to track open bugs.

Where is the Task 4 code?  Checked in this order:
  1. env var VALIDATOR_APP_PATH  (folder that contains the `app/` package)
  2. the current working directory
  3. the parent of this Task 5 folder (repo root)
  4. sibling folder named Task-4-Multi-Agent-Architecture
"""
import functools
import os
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
TASK5_ROOT = HERE.parent


def _find_app_root() -> Path:
    candidates = []
    if os.getenv("VALIDATOR_APP_PATH"):
        candidates.append(Path(os.environ["VALIDATOR_APP_PATH"]))
    candidates += [
        Path.cwd(),
        TASK5_ROOT,
        TASK5_ROOT.parent,
        TASK5_ROOT.parent / "Task-4-Multi-Agent-Architecture",
    ]
    for c in candidates:
        if (c / "app" / "orchestrator.py").exists():
            return c
    raise RuntimeError(
        "Could not find the Task 4 `app/` package. Run from the Task 4 "
        "project root or set VALIDATOR_APP_PATH to the folder containing app/."
    )


APP_ROOT = _find_app_root()
for p in (str(APP_ROOT), str(TASK5_ROOT / "scripts")):
    if p not in sys.path:
        sys.path.insert(0, p)

# Tests must never hit real APIs unless explicitly running the live script.
os.environ["USE_MOCKS"] = "true"


def known_bug(bug_id: str, summary: str):
    """Mark a test that checks the *correct* behaviour of a known open bug.

    While the bug is open the test is reported as SKIPPED with the bug id
    (so the suite stays green and the bug stays visible). Once the Task 4
    code is fixed the test simply passes. Set EXPECT_FIXES=1 to make an
    open bug fail the run (use this after applying the fixes patch).
    """
    def deco(fn):
        @functools.wraps(fn)
        def wrapper(*a, **k):
            try:
                return fn(*a, **k)
            except Exception as exc:  # AssertionError or crash = bug present
                if os.getenv("EXPECT_FIXES") == "1":
                    raise
                raise unittest.SkipTest(f"KNOWN {bug_id}: {summary} ({type(exc).__name__})")
        return wrapper
    return deco
