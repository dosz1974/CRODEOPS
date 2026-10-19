import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts.deploy import deploy


class DeploymentGuards(unittest.TestCase):
    def prepare(self, root):
        artifact = root / "app.pyz"
        artifact.write_bytes(b"demo artifact")
        manifest = {
            "branch": "development",
            "revision": "test-commit",
            "sha256": hashlib.sha256(artifact.read_bytes()).hexdigest(),
        }
        (root / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        return artifact

    def test_development_artifact_cannot_deploy_to_production(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            artifact = self.prepare(root)
            with self.assertRaisesRegex(ValueError, "Branch and environment"):
                deploy(artifact, "production", root / "target")
            self.assertFalse((root / "target").exists())

    def test_changed_artifact_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            artifact = self.prepare(root)
            artifact.write_bytes(b"changed artifact")
            with self.assertRaisesRegex(ValueError, "checksum mismatch"):
                deploy(artifact, "development", root / "target")
            self.assertFalse((root / "target").exists())
