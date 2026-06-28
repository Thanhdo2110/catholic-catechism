from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LocalizedLessonDTO:
    id: int
    category_id: int
    slug: str
    language: str
    title: str
    summary: str | None
    content_markdown: str


@dataclass(frozen=True)
class LocalizedQuizQuestionDTO:
    id: int
    lesson_id: int
    difficulty: int
    language: str
    prompt: str
    options: list[str]
    correct_option: str
    reference: str | None
    explanation: str | None

