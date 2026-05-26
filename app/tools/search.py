import subprocess
from pathlib import Path

MAX_SNIPPETS = 20
MAX_SNIPPET_LINES = 10

SKIP_DIRS = {".git", "__pycache__", ".venv", "node_modules", "dist", "build", ".mypy_cache"}
TEXT_EXTENSIONS = {
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".go",
    ".rs",
    ".java",
    ".rb",
    ".php",
    ".c",
    ".cpp",
    ".h",
    ".cs",
    ".sh",
    ".md",
    ".toml",
    ".yaml",
    ".yml",
    ".json",
    ".env",
    ".txt",
    ".sql",
}


def _iter_text_files(repo_path: str):
    for p in Path(repo_path).rglob("*"):
        if any(skip in p.parts for skip in SKIP_DIRS):
            continue
        if p.is_file() and p.suffix in TEXT_EXTENSIONS:
            yield p


def _rg_available() -> bool:
    try:
        result = subprocess.run(["rg", "--version"], capture_output=True, timeout=3)
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def grep(pattern: str, repo_path: str, file_glob: str = "*.py") -> list[str]:
    if _rg_available():
        result = subprocess.run(
            ["rg", "--no-heading", "-n", "-g", file_glob, pattern, "."],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=15,
        )
        if result.returncode == 0:
            return result.stdout.strip().splitlines()[:MAX_SNIPPETS]

    # Python fallback
    matches: list[str] = []
    for p in _iter_text_files(repo_path):
        try:
            for i, line in enumerate(p.read_text(errors="replace").splitlines(), 1):
                if pattern.lower() in line.lower():
                    rel = str(p.relative_to(repo_path))
                    matches.append(f"{rel}:{i}:{line.rstrip()}")
                    if len(matches) >= MAX_SNIPPETS:
                        return matches
        except OSError:
            continue
    return matches


def find_files(repo_path: str, patterns: list[str]) -> list[str]:
    """Return paths of files that contain or match any of the given keyword patterns."""
    found: set[str] = set()

    for p in _iter_text_files(repo_path):
        rel = str(p.relative_to(repo_path))
        # Match filename
        if any(pat.lower() in rel.lower() for pat in patterns):
            found.add(rel)
            continue
        # Match content
        try:
            text = p.read_text(errors="replace").lower()
            if any(pat.lower() in text for pat in patterns):
                found.add(rel)
        except OSError:
            continue
        if len(found) >= MAX_SNIPPETS:
            break

    return sorted(found)[:MAX_SNIPPETS]


def read_snippet(file_path: str, repo_path: str, max_lines: int = MAX_SNIPPET_LINES) -> str:
    full_path = Path(repo_path) / file_path
    if not full_path.exists():
        return ""
    lines = full_path.read_text(encoding="utf-8", errors="replace").splitlines()
    preview = lines[:max_lines]
    suffix = f"\n... ({len(lines) - max_lines} more lines)" if len(lines) > max_lines else ""
    return "\n".join(preview) + suffix
