from pathlib import Path


def read_file(path: str | Path) -> str:
    return Path(path).read_text(encoding="utf-8", errors="replace")


def write_file(path: str | Path, content: str) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")


def list_dir(path: str | Path, max_depth: int = 2) -> list[str]:
    root = Path(path)
    results: list[str] = []

    def _walk(current: Path, depth: int) -> None:
        if depth > max_depth:
            return
        for entry in sorted(current.iterdir()):
            if entry.name.startswith("."):
                continue
            relative = str(entry.relative_to(root))
            results.append(relative + ("/" if entry.is_dir() else ""))
            if entry.is_dir():
                _walk(entry, depth + 1)

    _walk(root, 0)
    return results
