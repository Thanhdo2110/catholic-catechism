from __future__ import annotations

from collections.abc import Iterable

from flask import Flask, current_app, g, request


def _supported_languages() -> Iterable[str]:
    return current_app.config["SUPPORTED_LANGUAGES"]


def resolve_language() -> str:
    query_language = request.args.get("lang", type=str)
    if query_language in _supported_languages():
        return query_language

    best_match = request.accept_languages.best_match(list(_supported_languages()))
    if best_match:
        return best_match

    return current_app.config["DEFAULT_LANGUAGE"]


def get_request_language() -> str:
    return getattr(g, "language", current_app.config["DEFAULT_LANGUAGE"])


def register_language_middleware(app: Flask) -> None:
    @app.before_request
    def set_request_language() -> None:
        g.language = resolve_language()

