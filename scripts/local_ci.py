"""Run the same project commands locally; this does not emulate GitHub Actions."""

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--branch", choices=["development", "main"], required=True)
    args = parser.parse_args()
    actual = subprocess.check_output(
        ["git", "branch", "--show-current"], cwd=ROOT, text=True
    ).strip()
    if actual != args.branch:
        raise SystemExit(f"Check out branch {args.branch} first; current branch: {actual}")
    environment = "production" if args.branch == "main" else "development"
    print(f"LOCAL RUN branch={args.branch} environment={environment}", flush=True)
    commands = [
        ["-m", "ruff", "check", "."],
        ["scripts/verify_workflows.py"],
        ["-m", "unittest", "discover", "-s", "tests", "-v"],
        ["scripts/build.py", "--branch", args.branch,
         "--output", f"dist/{args.branch}"],
        ["scripts/deploy.py", "--artifact", f"dist/{args.branch}/app.pyz",
         "--environment", environment, "--target", f".deploy/{environment}"],
    ]
    for command in commands:
        print("STAGE " + " ".join(command), flush=True)
        subprocess.run([sys.executable, *command], cwd=ROOT, check=True)
    print(f"LOCAL RUN PASS branch={args.branch}", flush=True)


if __name__ == "__main__":
    main()
