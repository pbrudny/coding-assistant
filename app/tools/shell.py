import subprocess
from dataclasses import dataclass


@dataclass
class CommandResult:
    stdout: str
    stderr: str
    returncode: int

    @property
    def success(self) -> bool:
        return self.returncode == 0


def run_command(
    cmd: list[str],
    cwd: str | None = None,
    timeout: int = 60,
) -> CommandResult:
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return CommandResult(
            stdout=result.stdout,
            stderr=result.stderr,
            returncode=result.returncode,
        )
    except subprocess.TimeoutExpired:
        return CommandResult(stdout="", stderr=f"Command timed out after {timeout}s", returncode=1)
    except FileNotFoundError as e:
        return CommandResult(stdout="", stderr=str(e), returncode=1)
