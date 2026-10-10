# Git workflow

## Scheme: one branch per feature + hunk review before every commit

Solo development. Every commit is reviewed by the owner **before it is made**: the owner inspects the working-tree diff in Hunk and approves it.

- `main` is always in a working state: the app runs, tests are green
- Every feature gets a branch off the up-to-date `main`
- Changes inside a branch are made in small logical chunks; before every commit — a review pause
- A finished branch is merged into `main` with `git merge --no-ff` — no PRs, no squash (every commit has already been reviewed)

## Language

- Commits and documentation: English
- Communication with the owner: Russian

## Branch naming

| Prefix | Example | Purpose |
|---------|--------|-----------|
| `feat/` | `feat/auth` | new functionality |
| `fix/` | `fix/session-expiry` | bug fix |
| `docs/` | `docs/mvp-plan` | documentation |
| `chore/` | `chore/deps` | infrastructure, dependencies |

## Commits

- Style: Conventional Commits — `type: description`
- One logical chunk of work = one commit
- Types: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`, `style`

Examples:

```
feat: add login form
fix: expire sessions after 30 days
test: cover auth flow
docs: describe LLM prompt strategy
```

## Single-commit cycle

1. The agent makes a change as one logical chunk in the working tree
2. **Pause.** The owner opens `hunk diff` in the project terminal and reviews the diff
   - The agent can drive the live session via `hunk session *`: navigation to important spots, inline explanatory comments (skill `.opencode/skills/hunk`)
3. Approval → the agent commits (`git add <files> && git commit`)
4. Notes → the agent fixes → `hunk diff` again → repeat until approved

## Branch cycle

1. `git checkout main && git pull`
2. `git checkout -b <type>/<name>`
3. Commit cycles (see above)
4. Feature done, tests and linter green: `git checkout main && git merge --no-ff <branch>`
5. `git push` (main and the branch); the branch can be deleted

## Rules

- Never commit without the owner's approval
- Tests and linter (`uv run pytest`, `uv run ruff check`) green before the review pause
- One logical chunk per commit — two topics in one diff means two cycles
- After a merge: update the progress checklist in [AGENTS.md](../AGENTS.md#progress)

## Roles

- **AI agent** (opencode): change → review pause → commit upon approval; drives the hunk session (navigation, explanations); merges the branch
- **Owner**: reviews every diff in the hunk TUI (`hunk diff`), approves or leaves notes
