# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Status

Spec-only. The full product spec is in `prd.md`. No implementation exists yet.

## What This Is

A local-first AI coding assistant built with LangGraph. It accepts a repository path and a natural-language task, then autonomously explores code, creates a plan, implements changes, runs tests, and iteratively repairs failures — producing a final diff and summary.

## Planned Tech Stack

- Python 3.11+, LangGraph, LangChain, Pydantic
- Package manager: `uv`
- Linter/formatter: `ruff` (line length 100, rules E/F/I/UP)
- OpenAI API as the LLM provider (provider abstraction recommended from the start)
- CLI entry point: `uv run python main.py --repo ./example_repo --task "..."`
- Test runner: pytest (with support for npm test, cargo test)
- Search: ripgrep (`rg`) for codebase traversal

## Commands

```bash
uv sync                        # install dependencies
uv run python main.py --repo ./example_repo --task "Add delete endpoint"
uv run pytest                  # run tests
uv run pytest tests/test_foo.py::test_bar  # run a single test
uv run ruff check app/         # lint
uv run ruff format app/        # format
```

## GitHub

Public repo under `github.com/pbrudny/coding-assistant`. When creating: `gh repo create coding-assistant --public`. Keep remote in sync when making changes.

## Architecture

The system is a `StateGraph` with six nodes wired in sequence, with a conditional retry edge from `evaluate` back to `implement`:

```
task_understand → codebase_search → planning → implement → test_runner → evaluate
                                                               ↑              ↓
                                                           repair_loop ← (retry)
```

Each node reads from and writes to a shared `AgentState` (TypedDict). Nodes must update only the fields they own.

### Node responsibilities (from PRD)

| Node | Input fields | Output fields |
|------|-------------|---------------|
| `understand` | `task` | `goal`, `likely_components`, `risk_level`, `requires_tests` |
| `search` | `repo_path`, `likely_components` | `relevant_files`, `context_snippets` |
| `planner` | `goal`, `context_snippets` | `implementation_plan`, `files_to_modify` |
| `implement` | `files_to_modify`, `implementation_plan` | `modified_files` |
| `test_runner` | `repo_path` | `test_results` (`success`, `stdout`, `stderr`, `failed_tests`) |
| `evaluate` | `test_results`, `iteration_count` | `evaluation` (`status`: success/retry/failed, `reason`) |

### State schema (from PRD)

```python
class AgentState(TypedDict):
    task: str
    repo_path: str
    relevant_files: list[str]
    implementation_plan: list[str]
    modified_files: list[str]
    test_results: dict
    evaluation: dict
    iteration_count: int
    final_summary: str
```

### Retry loop

`MAX_ITERATIONS = 3` (configurable). The evaluate node routes to `implement` again on `status == "retry"` (syntax errors, failing tests, missing implementation). It routes to finish on `success` or when the iteration limit is exceeded.

## Planned Directory Layout

```
app/
  graph.py          # StateGraph definition and edge wiring
  state.py          # AgentState TypedDict
  nodes/            # one file per node
  tools/            # filesystem.py, shell.py, search.py
  prompts/          # prompt templates
tests/
main.py             # CLI entry point
```

## Key Design Constraints (from PRD)

- No single giant agent node — each concern is its own LangGraph node.
- Context size must be bounded in the search node; never load entire repositories.
- All structured outputs use Pydantic models.
- State must remain JSON-serializable.
- Test runner must use timeouts and capture exit codes.
- LangSmith tracing is the recommended observability path.

## Database

PostgreSQL on Neon — project `coding-assistant` (ID: `nameless-scene-91344992`), database `neondb`, branch `main`.

Connect with `asyncpg` or `psycopg`. Use the pooled connection string for the app and the direct string for migrations:

- `CODING_ASSISTANT_DATABASE_URL` — pooled (PgBouncer, use for the app)
- `CODING_ASSISTANT_DATABASE_URL_DIRECT` — direct endpoint (use for migrations/DDL)

## Secrets and API Keys

All credentials are in `~/agenty/secrets/.env`. Keys relevant to this project:

| Key | Purpose |
|-----|---------|
| `OPENAI_API_KEY` | Primary LLM provider (OpenAI) |
| `ANTHROPIC_API_KEY` | Alternative LLM provider (Claude) |
| `LANGSMITH_API_KEY` | LangSmith tracing/observability |
| `CODING_ASSISTANT_DATABASE_URL` | Neon pooled connection string (app) |
| `CODING_ASSISTANT_DATABASE_URL_DIRECT` | Neon direct connection string (migrations) |

Load with `python-dotenv` or `pydantic-settings` pointing at `~/agenty/secrets/.env`. Never hardcode or print values.

## Deployment

Target: MIKR.US VPS managed by Coolify (see `~/agenty/loaded-context/my_vps.md` for full infrastructure details).

- **Coolify** at `https://dashboard.codewithpeter.com` — API token: `COOLIFY_TOKEN` in secrets
- **Routing**: Cloudflare Tunnel → Traefik → container; available subdomains under `*.codewithpeter.com`
- **Recommended pack**: `dockerfile` — nixpacks and `static` pack have known issues on this server
- Deployment pattern: `POST /applications/dockerfile` → set env vars → `GET /deploy?uuid=...` → poll until finished (see `~/agenty/loaded-context/coolify_api.md`)

## Observability

LangSmith tracing is the intended solution. Set `LANGCHAIN_TRACING_V2=true` and `LANGCHAIN_API_KEY` (same value as `LANGSMITH_API_KEY`) in the environment before running the agent.

## Out of Scope for V1

IDE plugins, git auto-commit, long-term memory, vector search, autonomous package installation.
