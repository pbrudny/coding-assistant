import argparse
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path.home() / "agenty" / "secrets" / ".env")


def main() -> None:
    parser = argparse.ArgumentParser(description="Local agentic coding assistant")
    parser.add_argument("--repo", required=True, help="Path to the target repository")
    parser.add_argument("--task", required=True, help="Natural language task description")
    args = parser.parse_args()

    print(f"Repo: {args.repo}")
    print(f"Task: {args.task}")


if __name__ == "__main__":
    main()
