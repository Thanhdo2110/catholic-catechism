from __future__ import annotations

from backend.services.dto import LocalizedQuizQuestionDTO


def serialize_quiz(quiz: LocalizedQuizQuestionDTO) -> dict[str, object]:
    return {
        "id": quiz.id,
        "lesson_id": quiz.lesson_id,
        "difficulty": quiz.difficulty,
        "language": quiz.language,
        "prompt": quiz.prompt,
        "options": quiz.options,
        "correct_option": quiz.correct_option,
        "reference": quiz.reference,
        "explanation": quiz.explanation,
    }
