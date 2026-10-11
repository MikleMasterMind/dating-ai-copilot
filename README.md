# dating-ai-copilot

An AI assistant for dating app chats: paste a conversation — get 3 reply options in different tones with an explanation of why each one works.

## MVP

- Login + password authentication — user contexts are stored separately
- Paste a conversation (text) + optional platform and goal
- 3 reply options: flirty / playful / sincere — each with a "why it works" note and a copy button
- Generation history per user

Out of MVP scope: request limits, payments, screenshots, CI.

## Stack

| Layer | Technologies |
|------|-----------|
| Backend | Python 3.12+, FastAPI, SQLAlchemy 2.0 (async, SQLite) |
| LLM | LangChain + langchain-openai, gpt-4o-mini, structured output |
| Auth | login + password (pwdlib / argon2), DB sessions + httpOnly cookie |
| Frontend | Jinja2 + HTMX + Tailwind (CDN), served by FastAPI |
| Tooling | uv, ruff, pytest, hunk (commit review) |

## Run

```
uv sync                                   # dependencies
uv run uvicorn app.main:app --reload      # http://localhost:8000
```

Checks: `uv run pytest`, `uv run ruff check .`

Current status: [AGENTS.md](AGENTS.md#progress).

## Documentation

All project documentation is written in English.

- [docs/mvp-plan.md](docs/mvp-plan.md) — MVP specification
- [docs/git-workflow.md](docs/git-workflow.md) — git process and hunk review
- [AGENTS.md](AGENTS.md) — instructions for AI agents and the progress checklist
