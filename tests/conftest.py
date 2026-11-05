"""Skip DiskSnapshot freeze tests when the optional 2026-10-15 bodies are absent."""

from pathlib import Path

import pytest

FREEZE = Path(__file__).resolve().parents[1] / "data" / "snapshots" / "2026-10-15"


def pytest_configure(config):
    config.addinivalue_line("markers", "needs_freeze: requires data/snapshots/2026-10-15 gzip bodies")


def pytest_collection_modifyitems(config, items):
    if (FREEZE / "manifest.jsonl").is_file():
        return
    skip = pytest.mark.skip(reason="optional 2026-10-15 freeze not bundled in the public demo")
    for item in items:
        if "needs_freeze" in item.keywords:
            item.add_marker(skip)
