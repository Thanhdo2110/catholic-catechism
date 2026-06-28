from __future__ import annotations

from flask import Flask

from backend.services.lesson_service import LessonService
from backend.services.quiz_service import QuizService
from backend.services.spaced_repetition_service import SpacedRepetitionService


def register_services(app: Flask) -> None:
    repositories = app.extensions["repositories"]
    app.extensions.setdefault("services", {})
    app.extensions["services"]["lesson_service"] = LessonService(
        lesson_repository=repositories["lesson_repository"],
    )
    app.extensions["services"]["quiz_service"] = QuizService(
        quiz_repository=repositories["cached_quiz_repository"],
    )
    app.extensions["services"]["spaced_repetition_service"] = SpacedRepetitionService(
        progress_repository=repositories["flashcard_progress_repository"],
    )
