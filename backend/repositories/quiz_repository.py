from __future__ import annotations

from sqlalchemy import select

from backend.models import db
from backend.models.quiz_question import QuizQuestion, QuizQuestionTranslation
from backend.repositories.records import LocalizedQuizQuestionRecord


class QuizRepository:
    def get_localized(self, quiz_id: int, language: str) -> LocalizedQuizQuestionRecord | None:
        query = (
            select(QuizQuestion, QuizQuestionTranslation)
            .join(QuizQuestionTranslation, QuizQuestionTranslation.quiz_question_id == QuizQuestion.id)
            .where(
                QuizQuestion.id == quiz_id,
                QuizQuestionTranslation.language_code == language,
            )
        )
        row = db.session.execute(query).one_or_none()
        if row is None:
            return None

        quiz_question, translation = row
        return LocalizedQuizQuestionRecord(
            id=quiz_question.id,
            lesson_id=quiz_question.lesson_id,
            difficulty=quiz_question.difficulty,
            language=translation.language_code,
            prompt=translation.prompt,
            options=translation.options,
            correct_option=translation.correct_option,
            reference=translation.reference,
            explanation=translation.explanation,
        )
