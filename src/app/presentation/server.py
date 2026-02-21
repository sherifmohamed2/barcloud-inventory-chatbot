"""
HTTP server entry point.

Thin HTTP adapter. All routing and serialisation logic is in handlers.py.
This class only deals with reading/writing HTTP bytes.
"""

import json
import logging
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

from src.app.config import get_settings
from src.app.logging_conf import configure_logging
from src.app.domain.errors import ConfigurationError
from src.app.presentation.handlers import ChatHandlerMixin
from src.app.presentation.errors import map_exception_to_http


class ChatServer(ChatHandlerMixin, BaseHTTPRequestHandler):
    """
    Thin HTTP adapter. All routing and serialisation logic is in handlers.py.
    This class only deals with reading/writing HTTP bytes.
    """

    protocol_version = "HTTP/1.1"

    def do_GET(self) -> None:
        status, body, ct = self.handle_get(self.path)
        self._write(status, body, ct)

    def do_POST(self) -> None:
        if self.path != "/api/chat":
            self._write(404, b'{"error":"not found"}', "application/json")
            return
        try:
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length)
            status, data = self.handle_post_chat(raw)
            body = json.dumps(data, default=str).encode()
            self._write(status, body, "application/json")
        except Exception as exc:
            status, data = map_exception_to_http(exc)
            body = json.dumps(data, default=str).encode()
            self._write(status, body, "application/json")

    def do_OPTIONS(self) -> None:
        """Handle CORS preflight requests."""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def _write(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt: str, *args) -> None:
        logging.getLogger("http.server").info(
            "%s — " + fmt, self.address_string(), *args
        )


def main() -> None:
    configure_logging()
    logger = logging.getLogger("server")

    try:
        cfg = get_settings()
    except ConfigurationError as exc:
        logging.critical("Startup aborted — %s: %s", exc.message, exc.detail)
        sys.exit(1)

    server = HTTPServer((cfg.host, cfg.port), ChatServer)
    logger.info("=" * 55)
    logger.info("  BarCloud Inventory Chatbot")
    logger.info("  URL      → http://localhost:%d", cfg.port)
    logger.info("  Provider → %s  |  Model → %s", cfg.provider, cfg.model_name)
    logger.info("=" * 55)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutdown requested — stopping server")
        server.shutdown()


if __name__ == "__main__":
    main()
