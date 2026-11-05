"""The published sheet is the only task file in this demo."""

from pathlib import Path

from fdagym.agents.baseline import load_split
from fdagym.questions import parse_question

ROOT = Path(__file__).resolve().parents[2]
PUBLIC = ROOT / "data" / "tasks" / "public.jsonl"
FIXTURE = ROOT / "tests" / "tasks" / "fixtures" / "fda_gym_public.jsonl"


def test_public_sheet_is_its_own_split():
    assert PUBLIC.is_file()
    assert PUBLIC.read_bytes() == FIXTURE.read_bytes()
    tasks = load_split("public")
    assert len(tasks) == 93
    assert [task["id"] for task in tasks] == [f"FG-{9101 + offset:04d}" for offset in range(93)]
    assert {task["split"] for task in tasks} == {"public"}
    assert {task["type"] for task in tasks} <= {"compare", "sponsor_hop"}
    for task in tasks:
        parse_question(task["question"])
