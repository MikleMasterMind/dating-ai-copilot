# AGENTS.md

Instructions for AI agents (opencode) working on dating-ai-copilot. Read this file at the start of every session.

## Project

An AI assistant for dating app chats: the user pastes a conversation → gets 3 reply options (flirty / playful / sincere) with a "why it works" explanation. Full specification: [docs/mvp-plan.md](docs/mvp-plan.md).

## Stack

Python 3.12+ / FastAPI / SQLAlchemy 2.0 async (SQLite, aiosqlite) / LangChain (langchain-openai, gpt-4o-mini, with_structured_output) / Jinja2 + HTMX + Tailwind CDN / uv / ruff / pytest.

## Commands

```
uv sync                                   # dependencies
uv run pytest                             # tests
uv run ruff check .                       # linter
uv run uvicorn app.main:app --reload      # server (http://localhost:8000)
```

## Working rules

1. Git process — strictly per [docs/git-workflow.md](docs/git-workflow.md): branch off `main` → small commits → `--no-ff` merge (no PRs, no squash)
2. **Before every commit — a review pause for the owner.** Make a change → stop → the owner reviews `hunk diff` → approval → commit. Never commit without approval.
3. Hunk review: the interactive session is the owner's TUI (`hunk diff`, `hunk show`). Never launch the TUI yourself. Drive the live session via `hunk session *` (navigation to important spots, explanatory comments) — skill `.opencode/skills/hunk/SKILL.md`
4. Commits: Conventional Commits, English (`feat: add login form`), one logical chunk per commit
5. Documentation: English. Communication with the owner: Russian
6. Docstrings are required for classes and functions; no code comments unless requested
7. Tests and linter green before the review pause
8. After merging a branch, update the checklist below; at the end of a session, fill in the "Where we stopped" section

## Progress

Status format: `[ ]` not started → `[~]` branch in progress → `[x]` merged.

- [x] Branch 1 `docs/mvp-plan` — hunk skill, README, docs/, AGENTS.md
- [x] Branch 2 `feat/scaffold` — pyproject, config, app factory, health check
- [ ] Branch 3 `feat/db-models` — SQLAlchemy models User, Session, Generation
- [ ] Branch 4 `feat/auth` — register/login/logout, current_user, tests
- [ ] Branch 5 `feat/llm` — LangChain service + structured output, mocked tests
- [ ] Branch 6 `feat/generate` — POST /api/generate, saving generations, tests
- [ ] Branch 7 `feat/ui` — Jinja2/HTMX: landing, login/register, form, results partial
- [ ] Branch 8 `feat/history` — /history page

## Where we stopped

- Done: `feat/scaffold` merged into `main` with `--no-ff`: pyproject + uv.lock (minimal deps — the rest of the stack arrives via `uv add` in branches 3–7), .gitignore, pydantic-settings config + .env.example, app factory with `include_router`, GET /health in app/routes/health.py, health test, README quick start. Owner's review decision: route definitions live in `app/routes/`
- Next: Branch 3 `feat/db-models` — `uv add "sqlalchemy[asyncio]" aiosqlite`, app/db.py (async engine, session factory, create_all), User/Session/Generation models
