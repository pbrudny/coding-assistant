Product Requirements Document (PRD)
Project Title

Local Agentic Coding Assistant

Built with:

LangGraph
Python
Local repository tooling
LLM-powered planning + implementation loop
1. Overview

The goal is to build a local-first AI coding assistant capable of:

Understanding a software engineering task
Exploring a local codebase
Creating an implementation plan
Modifying code
Running tests
Evaluating failures
Iteratively fixing issues
Producing a final patch/diff

This system should demonstrate practical agentic workflow patterns using LangGraph rather than acting as a simple chatbot.

The project is intended as:

a learning vehicle for LangGraph
a foundation for future advanced coding agents
an extensible local developer tool
2. Goals
Primary Goals
Learn graph-based agent orchestration
Implement reliable multi-step workflows
Demonstrate iterative repair loops
Use structured state management
Integrate real developer tooling
Secondary Goals
Create clean modular architecture
Enable future multi-agent expansion
Support observability/debugging
Maintain deterministic execution flow
3. Non-Goals (V1)

The following are explicitly out of scope for V1:

Cloud deployment
Autonomous internet browsing
IDE plugin integration
Multi-user support
Automatic git commits
Long-term memory
Embedding/vector database search
Autonomous package installation
Production-grade security sandboxing
Fully autonomous repository-wide refactors
4. Core User Story

As a developer,
I want to provide a coding task and local repository,
so that the assistant can implement changes, run tests, and propose a working patch automatically.

5. Example Workflow
Input

Repository:

./my-fastapi-project

Task:

Add endpoint for deleting users
Expected Flow
Agent analyzes task
Searches relevant files
Creates implementation plan
Modifies source files
Adds/updates tests
Runs test suite
Detects failures
Attempts repair loop
Produces final diff + summary
6. High-Level Architecture
User Task
    ↓
Task Understanding Node
    ↓
Codebase Search Node
    ↓
Planning Node
    ↓
Implementation Node
    ↓
Test Runner Node
    ↓
Evaluation Node
   ↙         ↘
Repair Loop   Finish
7. Functional Requirements
7.1 Task Understanding Node
Responsibilities
Parse natural language request
Extract implementation goals
Infer likely affected areas
Assess complexity/risk
Input
{
    "task": str
}
Output
{
    "goal": str,
    "likely_components": list[str],
    "risk_level": str,
    "requires_tests": bool
}
Requirements
Must use structured output
Must produce deterministic schema
Should avoid hallucinating file names
7.2 Codebase Search Node
Responsibilities
Search repository for relevant files
Identify existing patterns
Retrieve implementation context
Initial Search Strategy

Use:

ripgrep (rg)
directory traversal
filename heuristics
Example Operations
rg "user"
rg "router"
rg "delete"
Output
{
    "relevant_files": list[str],
    "context_snippets": list[str]
}
Requirements
Must limit context size
Must avoid loading entire repository
Should prioritize nearby related files
7.3 Planning Node
Responsibilities
Generate ordered implementation plan
Identify files requiring modification
Describe intended changes
Output Example
{
    "steps": [
        "Add DELETE route",
        "Implement controller logic",
        "Add unit tests"
    ],
    "files_to_modify": [
        "routes/users.py",
        "services/user_service.py",
        "tests/test_users.py"
    ]
}
Requirements
Plan must be explicit and ordered
Plans should remain concise
Avoid speculative large refactors
7.4 Implementation Node
Responsibilities
Read target files
Modify code
Generate updated content
Capabilities

V1:

full-file rewrite allowed

Future:

AST-aware editing
patch-based editing
Requirements
Preserve formatting when possible
Avoid unrelated edits
Track modified files in state
7.5 Test Runner Node
Responsibilities
Execute repository test commands
Capture output
Detect failures
Supported Commands

Examples:

pytest
npm test
cargo test
Output
{
    "success": bool,
    "stdout": str,
    "stderr": str,
    "failed_tests": list[str]
}
Requirements
Timeouts required
Capture exit codes
Handle command failures gracefully
7.6 Evaluation Node
Responsibilities

Determine:

Did tests pass?
Is implementation acceptable?
Should retry occur?
Decision Output
{
    "status": "success" | "retry" | "failed",
    "reason": str
}
Retry Conditions

Retry if:

syntax errors
failing tests
missing implementation

Do not retry if:

iteration limit exceeded
repository corrupted
unsupported task detected
7.7 Repair Loop
Responsibilities
Use test failures as feedback
Attempt corrective implementation
Requirements
Maximum retry count configurable
Previous failures available in state
Loop must terminate safely

Default:

MAX_ITERATIONS = 3
8. State Management

Use strongly typed shared state.

Example State Schema
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
Requirements
State must remain serializable
Each node updates only necessary fields
Avoid hidden mutable global state
9. LangGraph Requirements
Must Use
StateGraph
Conditional edges
Cyclic retry loop
Typed state
Modular nodes
Avoid
Single giant agent node
Monolithic prompts
Infinite loops
Hidden implicit transitions
10. Tooling Requirements
Required Tools
Filesystem Tools

Capabilities:

read file
write file
list directories
Shell Tool

Capabilities:

execute tests
run grep
inspect repository
Search Tool

Initial:

ripgrep-based

Future:

semantic retrieval
11. Observability
Logging Requirements

Log:

node execution
tool calls
state transitions
retry attempts
failures
Recommended

Use:

LangSmith tracing
12. CLI Interface
Example Usage
python main.py \
  --repo ./example_repo \
  --task "Add delete user endpoint"
Output
execution logs
final summary
generated diff
test results
13. Suggested Repository Structure
project/
│
├── app/
│   ├── graph.py
│   ├── state.py
│   ├── nodes/
│   │   ├── understand.py
│   │   ├── search.py
│   │   ├── planner.py
│   │   ├── implement.py
│   │   ├── test_runner.py
│   │   └── evaluate.py
│   │
│   ├── tools/
│   │   ├── filesystem.py
│   │   ├── shell.py
│   │   └── search.py
│   │
│   └── prompts/
│
├── tests/
│
├── main.py
│
├── requirements.txt
│
└── README.md
14. Technical Stack
Core
Python 3.11+
LangGraph
LangChain
Pydantic
LLM Provider

Initial:

OpenAI API

Provider abstraction recommended.

15. Success Criteria

V1 is successful if the system can:

Accept a repository + task
Identify relevant files
Modify code correctly
Run tests automatically
Retry at least once on failure
Produce final working patch for simple tasks
16. Example Tasks for Validation
Easy
Add endpoint
Rename variable
Add logging
Medium
Add middleware
Introduce validation
Add unit tests
Hard (stretch)
Multi-file refactor
Database migration
Async conversion
