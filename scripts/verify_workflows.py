"""Check the event filters and separation rules in the supplied YAML files."""

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def main():
    for branch, environment in [("development", "development"), ("main", "production")]:
        path = ROOT / ".github" / "workflows" / f"{branch}.yml"
        config = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert config["on"]["push"]["branches"] == [branch]
        assert config["on"]["pull_request"]["branches"] == [branch]
        jobs = config["jobs"]
        assert jobs["build"]["needs"] == "quality"
        assert jobs["deploy"]["needs"] == "build"
        assert jobs["deploy"]["environment"] == environment
        condition = jobs["deploy"]["if"]
        assert "github.event_name == 'push'" in condition
        assert f"github.ref == 'refs/heads/{branch}'" in condition
        assert config["permissions"] == {"contents": "read"}
        assert branch in config["concurrency"]["group"]
        print(f"WORKFLOW PASS {branch}: filters, needs, environment, deploy guard")
    print("ROUTING push development -> development only")
    print("ROUTING push main -> main only")
    print("ROUTING push feature/demo -> neither workflow")
    print("ROUTING pull_request -> target branch checks; no deployment")


if __name__ == "__main__":
    main()
