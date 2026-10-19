"""Deploy to an isolated local directory and verify the running artifact."""

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path


def deploy(artifact, environment, target):
    manifest = json.loads(artifact.with_name("manifest.json").read_text(encoding="utf-8"))
    expected_branch = {"development": "development", "production": "main"}[environment]
    if manifest["branch"] != expected_branch:
        raise ValueError("Branch and environment do not match")
    if hashlib.sha256(artifact.read_bytes()).hexdigest() != manifest["sha256"]:
        raise ValueError("Artifact checksum mismatch")
    target.mkdir(parents=True, exist_ok=True)
    deployed = target / "app.pyz"
    shutil.copy2(artifact, deployed)
    shutil.copy2(artifact.with_name("manifest.json"), target / "manifest.json")
    env = dict(os.environ, APP_ENV=environment)
    with tempfile.TemporaryDirectory() as temp:
        ready = Path(temp) / "ready.json"
        process = subprocess.Popen(
            [sys.executable, str(deployed), "--port", "0", "--ready-file", str(ready)],
            env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        try:
            deadline = time.monotonic() + 15
            while not ready.exists():
                if process.poll() is not None or time.monotonic() >= deadline:
                    raise RuntimeError("Application failed to start")
                time.sleep(0.05)
            url = json.loads(ready.read_text(encoding="utf-8"))["url"]
            with urllib.request.urlopen(url + "/health", timeout=5) as resp:
                health = json.load(resp)
                assert resp.status == 200
            assert health == {"status": "ok", "environment": environment}
            print(f"HTTP /health -> 200 environment={environment}")
            with urllib.request.urlopen(url + "/", timeout=5) as resp:
                index = json.load(resp)
                assert resp.status == 200
            assert index["branch"] == expected_branch
            assert index["revision"] == manifest["revision"]
            assert index["environment"] == environment
            print(f"HTTP / -> 200 branch={index['branch']} revision verified")
            try:
                urllib.request.urlopen(url + "/missing", timeout=5)
            except urllib.error.HTTPError as exc:
                assert exc.code == 404
            else:
                raise AssertionError("Unknown route did not return 404")
            print("HTTP /missing -> 404")
            print(f"DEPLOY PASS environment={environment}; checksum verified")
        finally:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
    print("Demo server stopped after smoke checks")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", type=Path, required=True)
    parser.add_argument("--environment", choices=["development", "production"], required=True)
    parser.add_argument("--target", type=Path, required=True)
    args = parser.parse_args()
    deploy(args.artifact, args.environment, args.target)
