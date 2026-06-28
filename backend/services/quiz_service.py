from __future__ import annotations

from backend.repositories.cached_quiz_repository import CachedQuizRepository
from backend.services.dto import LocalizedQuizQuestionDTO


class QuizService:
    def __init__(self, quiz_repository: CachedQuizRepository) -> None:
        self._quiz_repository = quiz_repository

    def get_question(self, quiz_id: int, language: str) -> LocalizedQuizQuestionDTO:
        localized_quiz = self._quiz_repository.get_localized(quiz_id=quiz_id, language=language)
        if localized_quiz is None:
            raise LookupError(f"Quiz question {quiz_id} not found for language {language}")

        return LocalizedQuizQuestionDTO(
            id=localized_quiz.id,
            lesson_id=localized_quiz.lesson_id,
            difficulty=localized_quiz.difficulty,
            language=localized_quiz.language,
            prompt=localized_quiz.prompt,
            options=localized_quiz.options,
            correct_option=localized_quiz.correct_option,
            reference=localized_quiz.reference,
            explanation=localized_quiz.explanation,
        )
