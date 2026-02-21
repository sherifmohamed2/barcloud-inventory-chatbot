"""
Thin endpoint handlers.

Designed to be used as a mixin with BaseHTTPRequestHandler in server.py.
"""

import json
import logging
from pathlib import Path

from pydantic import ValidationError

from src.app.schemas import ChatRequest
from src.app.application.container import get_chat_service
from src.app.presentation.errors import map_exception_to_http, RequestError

STATIC_DIR = Path(__file__).parent / "static"
logger = logging.getLogger(__name__)


class ChatHandlerMixin:
    """
    Mixin providing handler methods. Designed to be used with
    BaseHTTPRequestHandler in server.py.
    """

    def handle_get(self, path: str) -> tuple[int, bytes, str]:
        """Returns (status_code, body_bytes, content_type)."""
        if path in ("/", "/index.html"):
            f = STATIC_DIR / "index.html"
            return (
                (200, f.read_bytes(), "text/html")
                if f.exists()
                else (404, b'{"error":"not found"}', "application/json")
            )
        elif path == "/health":
            return (200, b'{"status":"ok"}', "application/json")
        # Serve static files (CSS, JS)
        elif path.startswith("/"):
            static_file = STATIC_DIR / path.lstrip("/")
            if static_file.exists() and static_file.is_file():
                content_type = "text/plain"
                if path.endswith(".css"):
                    content_type = "text/css"
                elif path.endswith(".js"):
                    content_type = "application/javascript"
                elif path.endswith(".html"):
                    content_type = "text/html"
                return (200, static_file.read_bytes(), content_type)
        return (404, b'{"error":"not found"}', "application/json")

    def handle_post_chat(self, raw_body: bytes) -> tuple[int, dict]:
        """Returns (status_code, response_dict)."""
        try:
            body = json.loads(raw_body)
        except (json.JSONDecodeError, ValueError) as e:
            raise RequestError(f"Invalid JSON body: {e}") from e

        req = ChatRequest(**body)  # raises ValidationError on bad input
        svc = get_chat_service()
        resp = svc.get_chat_response(req.session_id, req.message)
        code = 200 if resp.status == "ok" else 500
        return code, resp.model_dump()
