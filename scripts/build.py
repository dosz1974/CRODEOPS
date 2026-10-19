"""Build a standalone zipapp and a checksum manifest using stdlib only."""

import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
import zipapp
from pathlib import Path


def build(branch, output):
    root = Path(__file__).resolve().parents[1]
    revision = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=root, text=True
    ).strip()
    output.mkdir(parents=True, exist_ok=True)
    artifact = output / "app.pyz"
    with tempfile.TemporaryDirectory() as temp:
        stage = Path(temp)
        shutil.copy2(root / "app.py", stage / "app.py")
        (stage / "build_info.py").write_text(
            f"BRANCH = {branch!r}\nREVISION = {revision!r}\n", encoding="utf-8"
        )
        zipapp.create_archive(stage, artifact, main="app:main", compressed=True)
    manifest = {
        "branch": branch,
        "revision": revision,
        "artifact": artifact.name,
        "sha256": hashlib.sha256(artifact.read_bytes()).hexdigest(),
    }
    (output / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    print(f"BUILD PASS branch={branch} revision={revision}")
    print(f"ARTIFACT {artifact.name} sha256={manifest['sha256']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--branch", choices=["development", "main"], required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    build(args.branch, args.output)
