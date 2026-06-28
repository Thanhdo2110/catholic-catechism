from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class LocalizedLessonRecord:
    id: int
    category_id: int
    slug: str
    language: str
    title: str
    summary: str | None
    content_markdown: str


@dataclass(frozen=True)
class LocalizedQuizQuestionRecord:
    id: int
    lesson_id: int
    difficulty: int
    language: str
    prompt: str
    options: list[str]
    correct_option: str
    reference: str | None
    explanation: str | None


@dataclass(frozen=True)
class FlashcardProgressRecord:
    id: int
    user_id: int
    flashcard_id: int
    leitner_level: int
    last_reviewed_at: datetime | None
    next_review_at: datetime | None
