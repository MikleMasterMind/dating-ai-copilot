# MVP plan: dating-ai-copilot

## Goal

An AI assistant for dating app chats. The user pastes a conversation → gets 3 reply options in different tones with a short "why it works" explanation.

## User flow

1. `/` — guests see a landing page with login/register forms
2. Register or log in with a login and password
3. Workspace: pick or create a conversation (platform: Tinder / Bumble / Telegram / other, match name, initial match description), paste or type in messages; each message has a sender ("me" / "match") and an editable time (defaults to "now")
4. Optional goal (get a date / keep the conversation going) → submit → spinner → 3 cards: tone, text, "why it works", copy button
5. `/history` — the user's generation history; stored conversations give the coach full prior context with message times

## MVP scope

**Included:**

- Auth by login + password, sessions
- 3 reply options per generation (flirty / playful / sincere)
- Stored conversations: messages with sender and per-message time, fed to the coach prompt as context
- Saving generations per user and a history page
- Text-only conversation input

**Excluded (possible extensions):**

- Request limits and monetization
- Screenshot uploads
- Prompt personalization based on the user's other conversations (style learning across chats)
- CI and automated checks

## Stack

| Layer | Choice |
|------|-------|
| Backend | Python 3.12+, FastAPI, uvicorn |
| DB | SQLite via SQLAlchemy 2.0 (async, aiosqlite) |
| LLM | LangChain + langchain-openai: ChatOpenAI (gpt-4o-mini), with_structured_output |
| Auth | pwdlib (argon2) password hashing; session — token in DB + httpOnly cookie |
| Frontend | Jinja2 + HTMX, Tailwind via CDN; served by FastAPI |
| Tooling | uv, ruff, pytest, hunk |

## Project structure

```
app/
├── main.py          # app factory, static/templates, include routers
├── config.py        # pydantic-settings: OPENAI_API_KEY, OPENAI_MODEL, DATABASE_URL
├── db.py            # async engine, session factory, init (create_all)
├── models.py        # User, Session, Conversation, Message, Generation
├── auth.py          # pwdlib hashing, register/login/logout, current_user dependency
├── llm.py           # ChatOpenAI + structured output, dating-coach prompt
├── routes/
│   ├── pages.py     # GET pages (Jinja2)
│   └── api.py       # POST /api/generate (HTMX)
templates/
├── base.html
├── landing.html
├── login.html
├── register.html
├── index.html       # workspace form
├── history.html
└── partials/_suggestions.html
static/              # htmx.min.js, app.js (copy-to-clipboard)
tests/
docs/
.opencode/skills/hunk/   # skill for driving hunk review sessions
```

## Data model

```python
class User:
    id: int (pk)
    login: str (unique)
    password_hash: str
    description: str | None     # user's self-description for the coach
    created_at: datetime

class Session:
    id: int (pk)
    token: str (unique, urlsafe)
    user_id: FK(User)
    created_at: datetime

class Conversation:
    id: int (pk)
    user_id: FK(User)
    platform: str | None
    match_name: str | None
    match_description: str | None   # initial description of the chat partner
    created_at: datetime

class Message:
    id: int (pk)
    conversation_id: FK(Conversation)
    sender: str             # "me" | "match"
    text: str
    sent_at: datetime | None   # per-message time, editable in the UI
    created_at: datetime

class Generation:
    id: int (pk)
    user_id: FK(User)
    conversation_id: FK(Conversation)
    goal: str | None
    result_json: str       # serialized Suggestions
    created_at: datetime
```

- Conversations are persisted: messages keep the sender and per-message `sent_at` (editable in the UI), so the prompt gets full prior context with timing.
- `platform` describes the conversation, `goal` — a single reply request.
- `User.description` and `Conversation.match_description` feed the coach prompt context about both sides.
- Sessions do not expire in the MVP.
- No Alembic in the MVP: `create_all` on app startup.

## LangChain

```python
from typing import Literal

from pydantic import BaseModel, Field

class ReplySuggestion(BaseModel):
    tone: Literal["flirty", "playful", "sincere"]
    text: str = Field(description="A ready-to-send reply option")
    why: str = Field(description="One sentence: why it works")

class Suggestions(BaseModel):
    suggestions: list[ReplySuggestion]
```

- `ChatOpenAI(model="gpt-4o-mini", temperature=0.8)` — model from config
- `.with_structured_output(Suggestions)` — guaranteed structure without manual JSON parsing
- System prompt: a dating-chat coach; replies in Russian; takes the conversation context (messages with senders and times), user self-description, match description, platform and goal into account
- The LLM call is isolated in `app/llm.py` — easy to mock in tests

## API

| Method | Path | Purpose |
|-------|------|-----------|
| GET | `/` | landing (guest) or workspace page (logged in) |
| GET / POST | `/register` | registration form |
| GET / POST | `/login` | login form |
| POST | `/logout` | log out |
| POST | `/api/generate` | HTMX form: chat, platform?, goal? → partial `_suggestions.html` |
| GET | `/history` | the user's generation history |

## Work plan: branches

One branch per feature. One logical chunk per commit, hunk-reviewed before committing (see [git-workflow.md](git-workflow.md)). Merge into `main` — `merge --no-ff`.

| # | Branch | Contents |
|---|-------|-----------|
| 1 | `docs/mvp-plan` | hunk skill in the project, README, docs/, AGENTS.md |
| 2 | `feat/scaffold` | pyproject (uv), config, app factory, health check, ruff/pytest setup |
| 3 | `feat/db-models` | db.py, User/Session/Conversation/Message/Generation models, create_all |
| 4 | `feat/auth` | register/login/logout, current_user, tests |
| 5 | `feat/llm` | LangChain service + structured output, mocked tests |
| 6 | `feat/generate` | POST /api/generate, saving Conversation/Message/Generation, tests |
| 7 | `feat/ui` | templates + HTMX: landing, login/register, conversation form with editable message times, results partial |
| 8 | `feat/history` | /history page |

## Testing

- pytest + httpx AsyncClient
- Auth flow: register → login → logout → access to protected pages
- `/api/generate`: endpoint contract with a mocked LLM service (FakeListChatModel / monkeypatch)
- Models: creation, FK relations

## Configuration (.env)

```
OPENAI_API_KEY=...
OPENAI_MODEL=gpt-4o-mini
DATABASE_URL=sqlite+aiosqlite:///./app.db
```
