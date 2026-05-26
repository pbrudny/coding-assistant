import re
from pathlib import Path

from app.state import AgentState
from app.tools.shell import run_command

TEST_TIMEOUT = 120


def _detect_test_command(repo_path: str) -> list[str]:
    root = Path(repo_path)
    if (root / "pyproject.toml").exists() or (root / "pytest.ini").exists():
        return ["pytest", "--tb=short", "-q"]
    if (root / "package.json").exists():
        return ["npm", "test", "--", "--watchAll=false"]
    if (root / "Cargo.toml").exists():
        return ["cargo", "test"]
    return ["pytest", "--tb=short", "-q"]


def _extract_failed_tests(stdout: str, stderr: str) -> list[str]:
    failed: list[str] = []
    for line in (stdout + stderr).splitlines():
        if re.match(r"FAILED ", line):
            failed.append(line.split("FAILED ", 1)[1].strip())
    return failed


def test_runner(state: AgentState) -> dict:
    repo_path = state["repo_path"]
    cmd = _detect_test_command(repo_path)

    result = run_command(cmd, cwd=repo_path, timeout=TEST_TIMEOUT)

    return {
        "test_results": {
            "success": result.success,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "failed_tests": _extract_failed_tests(result.stdout, result.stderr),
        }
    }
