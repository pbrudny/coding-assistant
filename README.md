# coding-assistant

A local-first AI coding assistant built with LangGraph. Give it a repository path and a natural-language task — it explores the codebase, creates an implementation plan, modifies files, runs tests, and iteratively repairs failures until it produces a working patch.

## How it works

```
understand → codebase_search → planner → implement → test_runner → evaluate
                                                            ↑              ↓
                                                        (retry loop) ← status=retry
```

Each stage is a discrete LangGraph node with typed state. The repair loop retries up to 3 times on test failures, passing the previous error output back to the implementation node.

## Requirements

- Python 3.11+
- [uv](https://docs.astral.sh/uv/)
- OpenAI API key

## Setup

```bash
git clone https://github.com/pbrudny/coding-assistant
cd coding-assistant
uv sync
```

Set your API keys in a `.env` file (or `~/agenty/secrets/.env`):

```env
OPENAI_API_KEY=sk-...
LANGSMITH_API_KEY=lsv2_...   # optional, enables LangSmith tracing
```

## Usage

```bash
uv run python main.py --repo ./path/to/repo --task "Add a DELETE /users/{id} endpoint"
```

The agent prints progress for each node and a final summary:

```
Starting agent on repo: ./my-fastapi-project
Task: Add a DELETE /users/{id} endpoint

[understand] done
  goal: Add a DELETE endpoint that removes a user by ID
  risk: low
[codebase_search] done
  files found: ['routes/users.py', 'services/user_service.py']
[planner] done
  - Add DELETE route in routes/users.py
  - Implement delete_user in user_service.py
  - Add test in tests/test_users.py
[implement] done
  modified: ['routes/users.py', 'services/user_service.py', 'tests/test_users.py']
[test_runner] done
  success: True  failed: []
[evaluate] done
  status: success  reason: All tests passed

--- SUMMARY ---
Task completed successfully in 1 iteration(s).
Modified files: routes/users.py, services/user_service.py, tests/test_users.py
```

## Configuration

| Environment variable | Default | Description |
|---|---|---|
| `OPENAI_API_KEY` | — | Required. OpenAI API key |
| `ANTHROPIC_API_KEY` | — | Optional. Alternative LLM provider |
| `LANGSMITH_API_KEY` | — | Optional. Enables LangSmith tracing |
| `CODING_ASSISTANT_MODEL` | `gpt-4o` | Model to use |
| `CODING_ASSISTANT_MAX_ITERATIONS` | `3` | Max repair loop iterations |

## Development

```bash
uv run pytest                            # run all tests
uv run pytest tests/test_tools.py::test_write_and_read_file  # single test
uv run ruff check app/                   # lint
uv run ruff format app/                  # format
```

## Project structure

```
app/
  config.py       # pydantic-settings config
  state.py        # AgentState TypedDict
  graph.py        # StateGraph wiring
  nodes/          # one module per LangGraph node
  tools/          # filesystem, shell, search utilities
  prompts/        # system prompt templates
tests/
main.py           # CLI entry point
```
