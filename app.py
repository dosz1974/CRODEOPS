"""Small HTTP service used to demonstrate separate branch pipelines."""

import argparse
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

try:
    from build_info import BRANCH, REVISION
except ImportError:
    BRANCH, REVISION = "source", "unbuilt"


def response(path, environment):
    if path == "/health":
        return 200, {"status": "ok", "environment": environment}
    if path == "/":
        return 200, {
            "service": "branch-pipelines-demo",
            "environment": environment,
            "branch": BRANCH,
            "revision": REVISION,
        }
    return 404, {"error": "not found"}


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        status, payload = response(self.path, self.server.environment)
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--ready-file", type=Path)
    args = parser.parse_args()
    environment = os.environ.get("APP_ENV", "development")
    if environment not in {"development", "production"}:
        parser.error("APP_ENV must be development or production")
    with ThreadingHTTPServer(("127.0.0.1", args.port), Handler) as server:
        server.environment = environment
        url = f"http://127.0.0.1:{server.server_port}"
        if args.ready_file:
            temporary = args.ready_file.with_suffix(".tmp")
            temporary.write_text(json.dumps({"url": url}), encoding="utf-8")
            temporary.replace(args.ready_file)
        print(f"READY {url} environment={environment}", flush=True)
        server.serve_forever()


if __name__ == "__main__":
    main()
