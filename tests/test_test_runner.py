import tempfile
from pathlib import Path

from app.nodes.test_runner import _detect_test_command, _extract_failed_tests


def test_detect_pytest_from_pyproject():
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "pyproject.toml").write_text("[project]")
        cmd = _detect_test_command(tmp)
        assert cmd[0] == "pytest"


def test_detect_npm_from_package_json():
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "package.json").write_text("{}")
        cmd = _detect_test_command(tmp)
        assert cmd[0] == "npm"


def test_extract_failed_tests():
    stdout = "FAILED tests/test_foo.py::test_bar - AssertionError\nPASSED tests/test_ok.py::test_ok"
    failed = _extract_failed_tests(stdout, "")
    assert failed == ["tests/test_foo.py::test_bar - AssertionError"]


def test_extract_failed_tests_empty():
    assert _extract_failed_tests("1 passed", "") == []
