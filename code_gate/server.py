"""Simple HTTP server that exposes the code-gate API and serves the PWA frontend.

Start with:
    python -m code_gate.server          # default port 5000
    python -m code_gate.server --port 8080
"""
from __future__ import annotations

import argparse
import json
import mimetypes
import socket
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from .challenges import check_answer, get_challenge
from .gate import GateState, load_state, save_state

DEFAULT_STATE_PATH = Path.home() / ".code_gate" / "state.json"
APP_DIR = Path(__file__).parent.parent / "app"

_state_path: Path = DEFAULT_STATE_PATH


def _json_response(handler: BaseHTTPRequestHandler, data: object, status: int = 200) -> None:
    body = json.dumps(data, ensure_ascii=False).encode()
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.end_headers()
    handler.wfile.write(body)


def _state_dict(state: GateState) -> dict:
    return {
        "is_unlocked": state.is_unlocked,
        "solved_challenges": state.solved_challenges,
        "required_challenges": state.required_challenges,
        "unlock_attempts_today": state.unlock_attempts_today,
        "daily_streak": state.daily_streak,
        "total_challenges_solved": state.total_challenges_solved,
        "last_solved_date": state.last_solved_date,
    }


class GateHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args: object) -> None:  # quiet logs
        pass

    def do_OPTIONS(self) -> None:  # CORS preflight
        self.send_response(HTTPStatus.NO_CONTENT)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"

        if path == "/api/status":
            state = load_state(_state_path)
            _json_response(self, _state_dict(state))
            return

        if path == "/api/challenge":
            state = load_state(_state_path)
            challenge = get_challenge(state.unlock_attempts_today)
            _json_response(self, {
                "id": challenge["id"],
                "category": challenge["category"],
                "question": challenge["question"],
                "options": challenge["options"],
                "difficulty": challenge["difficulty"],
            })
            return

        # Serve static PWA files
        self._serve_static(path)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")

        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length) if length else b"{}"
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            _json_response(self, {"error": "Invalid JSON"}, 400)
            return

        if path == "/api/solve":
            challenge_id = data.get("challenge_id")
            user_answer = data.get("answer", "")
            from .challenges import all_challenges
            challenges = {c["id"]: c for c in all_challenges()}
            challenge = challenges.get(challenge_id)
            if challenge is None:
                _json_response(self, {"error": "Unknown challenge_id"}, 400)
                return
            correct = check_answer(challenge, user_answer)
            state = load_state(_state_path)
            unlocked = state.register_unlock_attempt(solved=correct)
            save_state(_state_path, state)
            _json_response(self, {
                "correct": correct,
                "unlocked": unlocked,
                **_state_dict(state),
            })
            return

        if path == "/api/reset":
            state = GateState()
            save_state(_state_path, state)
            _json_response(self, {"reset": True, **_state_dict(state)})
            return

        _json_response(self, {"error": "Not found"}, 404)

    # Static files the server is allowed to serve directly.
    # Maps URL basename → hardcoded filename (explicit allowlist — no user input reaches the path).
    _STATIC_FILES: dict[str, str] = {
        "index.html":   "index.html",
        "styles.css":   "styles.css",
        "app.js":       "app.js",
        "manifest.json": "manifest.json",
        "sw.js":        "sw.js",
    }

    def _serve_static(self, path: str) -> None:
        # Derive a safe filename: look up only the final segment in the hard-coded map.
        # If not found, fall back to index.html (SPA pattern).
        if path == "/" or path == "":
            key = "index.html"
        else:
            key = path.lstrip("/").rsplit("/", 1)[-1]

        # safe_name is always a hardcoded literal from _STATIC_FILES — never user input.
        safe_name = self._STATIC_FILES.get(key, "index.html")

        # Build the file path from a hardcoded directory + a fully sanitised, hardcoded name.
        file_path = APP_DIR / safe_name

        if not file_path.exists():
            self.send_error(HTTPStatus.NOT_FOUND)
            return

        mime, _ = mimetypes.guess_type(safe_name)
        mime = mime or "application/octet-stream"
        # Sanitize mime to prevent HTTP response-splitting via newlines
        mime = mime.replace("\r", "").replace("\n", "").split(";")[0].strip()
        body = file_path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def _local_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()


def serve(port: int = 5000, state_path: Path = DEFAULT_STATE_PATH) -> None:
    global _state_path
    _state_path = state_path
    ip = _local_ip()
    print(f"code-gate server running on port {port}")
    print(f"  Local:   http://localhost:{port}")
    print(f"  Network: http://{ip}:{port}")
    print("Open either URL in your phone's browser (same Wi-Fi network required for Network URL).")
    print("Press Ctrl+C to stop.\n")
    with ThreadingHTTPServer(("0.0.0.0", port), GateHandler) as httpd:
        httpd.serve_forever()


def main() -> int:
    parser = argparse.ArgumentParser(description="code-gate web server")
    parser.add_argument("--port", type=int, default=5000, help="Port to listen on (default: 5000)")
    parser.add_argument(
        "--state-file",
        type=Path,
        default=DEFAULT_STATE_PATH,
        help=f"State file path (default: {DEFAULT_STATE_PATH})",
    )
    args = parser.parse_args()
    serve(port=args.port, state_path=args.state_file)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
