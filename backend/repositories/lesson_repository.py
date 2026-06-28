from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import select

from backend.models import db
from backend.models.lesson import Lesson, LessonTranslation
from backend.repositories.records import LocalizedLessonRecord


class LessonRepository:
    def list_localized(self, category_id: int | None, language: str) -> Sequence[LocalizedLessonRecord]:
        query = (
            select(Lesson, LessonTranslation)
            .join(LessonTranslation, LessonTranslation.lesson_id == Lesson.id)
            .where(LessonTranslation.language_code == language)
            .order_by(Lesson.sort_order.asc(), Lesson.id.asc())
        )
        if category_id is not None:
            query = query.where(Lesson.category_id == category_id)
        return [
            LocalizedLessonRecord(
                id=lesson.id,
                category_id=lesson.category_id,
                slug=lesson.slug,
                language=translation.language_code,
                title=translation.title,
                summary=translation.summary,
                content_markdown=translation.content_markdown,
            )
            for lesson, translation in db.session.execute(query).all()
        ]
