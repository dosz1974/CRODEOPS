import unittest

from app import response


class AppTests(unittest.TestCase):
    def test_development_health(self):
        status, payload = response("/health", "development")
        self.assertEqual(status, 200)
        self.assertEqual(payload, {"status": "ok", "environment": "development"})

    def test_production_health(self):
        status, payload = response("/health", "production")
        self.assertEqual(status, 200)
        self.assertEqual(payload["environment"], "production")

    def test_index_identifies_service(self):
        status, payload = response("/", "development")
        self.assertEqual(status, 200)
        self.assertEqual(payload["service"], "branch-pipelines-demo")

    def test_index_preserves_environment(self):
        _, payload = response("/", "production")
        self.assertEqual(payload["environment"], "production")

    def test_index_has_build_metadata(self):
        _, payload = response("/", "development")
        self.assertIn("branch", payload)
        self.assertIn("revision", payload)

    def test_unknown_route_is_404(self):
        self.assertEqual(response("/missing", "development"),
                         (404, {"error": "not found"}))


if __name__ == "__main__":
    unittest.main()
