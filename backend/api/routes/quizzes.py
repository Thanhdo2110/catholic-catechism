from __future__ import annotations

from flask import Blueprint, current_app

from backend.api.middleware import get_request_language
from backend.api.schemas.quiz import QuizDetailRequest
from backend.api.serializers.quiz import serialize_quiz

quizzes_blueprint = Blueprint("quizzes", __name__)


@quizzes_blueprint.get("/quizzes/<int:quiz_id>")
def get_quiz(quiz_id: int) -> tuple[dict[str, object], int]:
    request_model = QuizDetailRequest(quiz_id=quiz_id)
    quiz_service = current_app.extensions["services"]["quiz_service"]
    quiz = quiz_service.get_question(
        quiz_id=request_model.quiz_id,
        language=get_request_language(),
    )
    return serialize_quiz(quiz), 200
