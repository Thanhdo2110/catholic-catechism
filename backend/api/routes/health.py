from __future__ import annotations

from flask import Blueprint

from backend.api.serializers.base import serialize_payload

health_blueprint = Blueprint("health", __name__)


@health_blueprint.get("/health")
def healthcheck() -> tuple[dict[str, str], int]:
    return serialize_payload({"status": "ok"}), 200
