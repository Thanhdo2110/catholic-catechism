from __future__ import annotations

from flask import Blueprint

from backend.api.routes.flashcards import flashcards_blueprint
from backend.api.routes.health import health_blueprint
from backend.api.routes.lessons import lessons_blueprint
from backend.api.routes.quizzes import quizzes_blueprint


def create_api_blueprint() -> Blueprint:
    api_blueprint = Blueprint("api", __name__)
    api_blueprint.register_blueprint(flashcards_blueprint)
    api_blueprint.register_blueprint(health_blueprint)
    api_blueprint.register_blueprint(lessons_blueprint)
    api_blueprint.register_blueprint(quizzes_blueprint)
    return api_blueprint
