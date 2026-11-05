# FDA-Gym (public demo)

A **tool-use RL environment** over a frozen [openFDA](https://open.fda.gov/) snapshot. An agent answers a regulatory question by calling tools, then `submit_answer`. The grader scores the answer **and** the trace, so a memorized fact with a fake citation does not pay.

This repository is the **recruiter / public demo**. The published sheet is 93 questions, `FG-9101`–`FG-9193`, in [`data/tasks/public/`](data/tasks/public/). Freeze version: `2026-10-15` (`drug/label`, `drug/event`, `drug/drugsfda`). Gzip bodies are not in this clone; pytest uses JSON fixtures unless you supply a freeze.

It is not a hidden exam. Use **this** repo as the public link. Do not treat any other GitHub copy of FDA-Gym as a private holdout.

## Quickstart (offline, no GPU, no API keys)

Python 3.11+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync --group dev
uv run pytest -q
```

That is the smoke run. It never calls live openFDA or an LLM. Tests marked for a DiskSnapshot freeze skip when `data/snapshots/2026-10-15/` is absent.

Score a Chat Completions model on the published sheet (needs `OPENROUTER_API_KEY` in `.env` **and** a local `2026-10-15` freeze):

```bash
cp .env.example .env
export FDAGYM_SNAPSHOT_DIR=/path/to/snapshots   # directory that contains 2026-10-15/
uv run python scripts/eval_chat.py --model openrouter/qwen/qwen-2.5-7b-instruct --run-id public-eval
```

Import the installed wheel without a git checkout:

```bash
uv build --wheel
uv venv /tmp/fdagym-wheel && uv pip install --python /tmp/fdagym-wheel/bin/python dist/*.whl
cd /tmp && /tmp/fdagym-wheel/bin/python -c "import fdagym, fdagym.env, fdagym.rewards"
```

The wheel does not ship a freeze. Point at one with `FDAGYM_SNAPSHOT_DIR`, or run `python -m fdagym.openfda` to locate/verify a freeze you already have.

## Why a grader this strict

A model that already knows the answer can still fail if it does not retrieve the evidence. A model that guesses one of three drugs can still fail if the comparison is not in the trace. That is the point.

Total: `0.60 * correctness + 0.25 * citation + 0.10 * format + 0.05 * efficiency`. Every score includes `grader_version`. **Current grader: v5.**

| Term | Pays when |
| --- | --- |
| format | `submit_answer` matches the schema. Invalid format forces correctness to 0. |
| citation | cited `id` appeared in this trajectory, `field` is in `gold_citations`, quote fuzzy-matches ≥ 0.9. Quotes < 4 characters never count. |
| correctness | format is 1, at least one citation is valid, the answer matches gold, **and** the hop / compare proof is in the trace. |
| efficiency | only when correctness > 0. Distinct `(tool, arguments)` pairs. Repeated identical calls are free. |

`compare` pays correctness only when every named drug was queried (so unique/none is visible) and a valid citation is about the deciding drug. One tool call and a short quote from `results` is not enough.

### Shortcuts the v5 suite catches

From `tests/rewards/test_public_attacks.py` (grader v5; runs when a `2026-10-15` freeze is present):

| Attack | Score |
| --- | --- |
| Honest oracle (every `oracle_call`, gold answer, gold citations) | **93 / 93** pass |
| One-call compare guess (first `oracle_call` + generic quote + gold or first-named drug) | **0 / 50** |
| One-call sponsor-hop (same attack on `sponsor_hop`) | **0 / 43** |
| Quitter (`unknown`, no citations) | **0 / 93** |
| FG-9101: one FAERS call on abacavir, quote `"PAIN"`, answer `"pravastatin"` | correctness **0** (citation can still be 1) |

## Tools

The model does not send a raw search string. Each call takes a drug name, a section, a year, an application number, or a sponsor name.

| Tool | What it returns |
| --- | --- |
| `search_drug_label` | Label summaries for one generic name. `has_section` keeps labels that contain that section. |
| `get_label_section` | One section of a label that `search_drug_label` already returned in this episode. |
| `query_adverse_events` | FAERS reports for one generic name. `top_reactions` lists MedDRA terms. `count` returns how many reports match. |
| `search_approvals` | Drugs@FDA records. Pass exactly one of `generic_name`, `application_number`, or `sponsor_name`. Generic-name search returns a summary page; products and original submissions come from a second `application_number` call. |
| `submit_answer` | Ends the episode. The answer is one string, number, or boolean, or `NOT_FOUND`, plus up to 8 citations. |

`FDAEnv` is a tool-use environment, not a Gymnasium env. `reset(task_id)` returns `{question, tools}`. `step(action)` returns `(observation, reward, done, info)`. Reward stays 0.0 until the episode ends.

## Dashboard

```bash
cd web && npm install && npm run dev
```

Open [http://localhost:3000](http://localhost:3000). The overview reads the jsonl files in `web/public/results/`. The shipped fixture uses fictional drugs.

## What this repo contains

| Path | Role |
| --- | --- |
| `fdagym/` | Env, tools, grader, snapshot reader, packaged JSON schemas |
| `data/tasks/public/` | Published eval (93 tasks, one file each) |
| `data/snapshots/` | Exam-universe name lists; gzip freeze is optional and not shipped |
| `web/` | Optional B1 trajectory viewer |
| `tests/` | Offline pytest (env, grader, public-sheet attacks when a freeze is present) |

openFDA records are United States government work. See [openFDA terms of service](https://open.fda.gov/terms/). Names, application numbers, and label text in the task files come from that source. Code is MIT.

MIT license. See [LICENSE](LICENSE).
