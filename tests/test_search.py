import tempfile
from pathlib import Path

from app.tools.search import find_files, read_snippet


def test_find_files_matches_content():
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "users.py").write_text("def delete_user(): pass")
        (Path(tmp) / "routes.py").write_text("router = Router()")
        found = find_files(tmp, ["delete_user"])
        assert any("users.py" in f for f in found)


def test_read_snippet_truncates():
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "big.py"
        p.write_text("\n".join(f"line {i}" for i in range(100)))
        snippet = read_snippet("big.py", tmp, max_lines=5)
        assert "line 0" in snippet
        assert "more lines" in snippet


def test_read_snippet_missing_file():
    with tempfile.TemporaryDirectory() as tmp:
        result = read_snippet("nonexistent.py", tmp)
        assert result == ""
