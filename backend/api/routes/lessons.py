from __future__ import annotations

from flask import Blueprint, current_app

from backend.api.middleware import get_request_language
from backend.api.schemas.lesson import LessonListRequest
from backend.api.serializers.lesson import serialize_lessons

lessons_blueprint = Blueprint("lessons", __name__)


@lessons_blueprint.get("/lessons")
def list_lessons() -> tuple[dict[str, object], int]:
    request_model = LessonListRequest.from_query()
    lesson_service = current_app.extensions["services"]["lesson_service"]
    lessons = lesson_service.list_lessons(
        category_id=request_model.category_id,
        language=get_request_language(),
    )
    return serialize_lessons(lessons), 200
