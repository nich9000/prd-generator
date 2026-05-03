# prd-generator

> Turn a one-line product idea into a structured PRD — title, problem, target user, success metrics, user stories, acceptance criteria, EARS requirements, risks — in one CLI call.

```bash
prd "Customers who abandon a cart should get a one-tap recovery flow next time they open the app"
```

Outputs a polished markdown PRD that's actually reviewable, not generic AI fluff. See [`examples/sample_prd.md`](examples/sample_prd.md) for a real run-through.

## Why

Generic "write me a PRD" prompts produce mush — vague metrics, no error paths, requirements written as "the system should be fast." This tool runs five focused agents, each owning a section, with explicit rules about what's testable, what's measurable, and what counts as a real risk vs. a platitude.

It's the natural next step from [`ears-spec-agent`](https://github.com/nich9000/ears-spec-agent), which transforms tickets *into* EARS specs. `prd-generator` zooms out: it owns the PRD around those specs.

## Architecture

```
       one-liner
           │
           ▼
   ┌───────────────┐
   │    Framer     │  →  title, problem, target_user, success_metrics
   └───────┬───────┘
           │
           ▼
   ┌───────────────┐
   │ Story Writer  │  →  user stories (P0/P1/P2, happy + edge)
   └───────┬───────┘
           │
           ▼
   ┌───────────────────┐
   │ Acceptance Writer │ →  Given/When/Then, incl. negative paths
   └─────────┬─────────┘
             │
             ▼
   ┌───────────────┐
   │  EARS Author  │  →  ubiquitous / event / state / unwanted / optional
   └───────┬───────┘
           │
           ▼
   ┌───────────────┐        ┌──────────────┐
   │ Risk Auditor  │   ────►│  PRD object  │ ──►  to_markdown() / to_json()
   └───────────────┘        └──────────────┘
```

Each agent has its own system prompt in `src/prd_generator/prompts/system.py` — diff and tweak independently.

## Installation

Requires Python 3.10+.

```bash
git clone https://github.com/nich9000/prd-generator
cd prd-generator
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
cp .env.example .env                                  # then add your ANTHROPIC_API_KEY
```

## Usage

**CLI**

```bash
# print to stdout
prd "Sellers should see at-a-glance which listings are losing rank week over week"

# write to a file
prd -o specs/seller-rank-watch.md "Sellers should see..."

# raw JSON (e.g. for piping into other tools)
prd --json "..." > prd.json
```

**Python**

```python
from prd_generator import generate_prd

prd = generate_prd("Customers should be able to refund a digital download")
print(prd.to_markdown())
print(prd.success_metrics)         # ['...', '...']
print(len(prd.ears_specs))         # int
```

## What you get

Every PRD includes:

- **Framing** — title, restated problem, target user, 3-5 measurable success metrics (each with a number).
- **User stories** — 4-8 stories in role/goal/benefit form with P0/P1/P2 priority, including at least one error/edge path.
- **Acceptance criteria** — Given/When/Then per story, including a negative case.
- **EARS requirements** — translated from acceptance criteria into EARS templates so engineers get unambiguous "shall" statements.
- **Risks** — specific failure modes (technical + GTM), each with severity and mitigation.
- **Out of scope** + **Open questions** — kept separate from requirements so reviewers know what's still being decided.

## Testing

```bash
pytest                           # schema/render tests, no API key needed
ruff check src tests             # lint
```

The pipeline itself isn't unit-tested against the live API by default (the CI bill would hurt). Add an integration test file in `tests/` if you want to exercise it end-to-end.

## Config

Set in `.env` or your shell:

| Variable | Default | Notes |
|---|---|---|
| `ANTHROPIC_API_KEY` | *required* | from console.anthropic.com |
| `PRD_MODEL` | `claude-sonnet-4-6` | any Anthropic chat model |
| `PRD_MAX_TOKENS` | `4096` | per-agent cap |

## Roadmap

- `--review` mode: run a critic agent over the generated PRD and surface gaps.
- Pluggable templates (engineering-heavy, design-heavy, GTM-heavy).
- Optional vector-store grounding ("write the PRD in the voice of our existing PRDs").
- Tiny Next.js demo so recruiters without an API key can play with it.

## License

MIT.
