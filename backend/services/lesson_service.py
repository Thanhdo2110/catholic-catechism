from __future__ import annotations

from collections.abc import Sequence

from backend.repositories.lesson_repository import LessonRepository
from backend.services.dto import LocalizedLessonDTO


class LessonService:
    def __init__(self, lesson_repository: LessonRepository) -> None:
        self._lesson_repository = lesson_repository

    def list_lessons(self, category_id: int | None, language: str) -> Sequence[LocalizedLessonDTO]:
        localized_lessons = self._lesson_repository.list_localized(
            category_id=category_id,
            language=language,
        )
        return [
            LocalizedLessonDTO(
                id=lesson.id,
                category_id=lesson.category_id,
                slug=lesson.slug,
                language=lesson.language,
                title=lesson.title,
                summary=lesson.summary,
                content_markdown=lesson.content_markdown,
            )
            for lesson in localized_lessons
        ]
