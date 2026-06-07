#!/usr/bin/env python3
"""Run the provided challenge validator without relying on a shell-quoted path."""
from pathlib import Path
import importlib.util
import sys


VALIDATOR_PATH = Path(r"c:\Hackathon\[PUB] India_runs_data_and_ai_challenge\India_runs_data_and_ai_challenge\validate_submission.py")


def main():
    if len(sys.argv) != 2:
        print("Usage: validate_local.py <submission.csv>")
        sys.exit(1)

    spec = importlib.util.spec_from_file_location("challenge_validator", VALIDATOR_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)

    errors = module.validate_submission(sys.argv[1])
    if errors:
        print(f"Validation failed ({len(errors)} issue(s)):\n")
        for e in errors:
            print(f"- {e}")
        sys.exit(1)

    print("Submission is valid.")


if __name__ == "__main__":
    main()
