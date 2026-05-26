import tempfile
from pathlib import Path

from app.tools.filesystem import list_dir, read_file, write_file
from app.tools.shell import run_command


def test_write_and_read_file():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "sub" / "file.txt"
        write_file(path, "hello")
        assert read_file(path) == "hello"


def test_list_dir():
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "a.py").write_text("")
        (Path(tmp) / "sub").mkdir()
        (Path(tmp) / "sub" / "b.py").write_text("")
        entries = list_dir(tmp)
        assert "a.py" in entries
        assert "sub/" in entries
        assert "sub/b.py" in entries


def test_run_command_success():
    result = run_command(["echo", "hi"])
    assert result.success
    assert "hi" in result.stdout


def test_run_command_failure():
    result = run_command(["false"])
    assert not result.success


def test_run_command_timeout():
    result = run_command(["sleep", "10"], timeout=1)
    assert not result.success
    assert "timed out" in result.stderr
