from __future__ import annotations

from collections.abc import Sequence

from backend.services.dto import LocalizedLessonDTO


def serialize_lessons(lessons: Sequence[LocalizedLessonDTO]) -> dict[str, object]:
    return {
        "items": [
            {
                "id": lesson.id,
                "category_id": lesson.category_id,
                "slug": lesson.slug,
                "language": lesson.language,
                "title": lesson.title,
                "summary": lesson.summary,
                "content_markdown": lesson.content_markdown,
            }
            for lesson in lessons
        ]
    }
