from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models.category import Category, CategoryTranslation
from backend.models.flashcard import Flashcard, FlashcardTranslation
from backend.models.lesson import Lesson, LessonTranslation
from backend.models.quiz_question import QuizQuestion, QuizQuestionTranslation


@dataclass
class SeedStats:
    categories: int = 0
    lessons: int = 0
    quiz_questions: int = 0
    flashcards: int = 0
    category_translations: int = 0
    lesson_translations: int = 0
    quiz_question_translations: int = 0
    flashcard_translations: int = 0


class ContentSeedRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def assert_slugs_available(
        self,
        category_slugs: Iterable[str],
        lesson_slugs: Iterable[str],
    ) -> None:
        category_slug_list = list(category_slugs)
        lesson_slug_list = list(lesson_slugs)

        if category_slug_list:
            existing_category_slugs = set(
                self._session.execute(
                    select(Category.slug).where(Category.slug.in_(category_slug_list))
                ).scalars()
            )
            if existing_category_slugs:
                raise ValueError(
                    "Category slug(s) already exist: "
                    + ", ".join(sorted(existing_category_slugs))
                )

        if lesson_slug_list:
            existing_lesson_slugs = set(
                self._session.execute(
                    select(Lesson.slug).where(Lesson.slug.in_(lesson_slug_list))
                ).scalars()
            )
            if existing_lesson_slugs:
                raise ValueError(
                    "Lesson slug(s) already exist: "
                    + ", ".join(sorted(existing_lesson_slugs))
                )

    def create_category(self, slug: str, sort_order: int) -> int:
        category = Category(slug=slug, sort_order=sort_order)
        self._session.add(category)
        self._session.flush()
        return category.id

    def bulk_insert_category_translations(self, mappings: Sequence[dict[str, Any]]) -> None:
        self._bulk_insert(CategoryTranslation, mappings)

    def create_lesson(
        self,
        category_id: int,
        slug: str,
        difficulty: int,
        sort_order: int,
    ) -> int:
        lesson = Lesson(
            category_id=category_id,
            slug=slug,
            difficulty=difficulty,
            sort_order=sort_order,
        )
        self._session.add(lesson)
        self._session.flush()
        return lesson.id

    def bulk_insert_lesson_translations(self, mappings: Sequence[dict[str, Any]]) -> None:
        self._bulk_insert(LessonTranslation, mappings)

    def create_quiz_question(self, lesson_id: int, difficulty: int) -> int:
        quiz_question = QuizQuestion(lesson_id=lesson_id, difficulty=difficulty)
        self._session.add(quiz_question)
        self._session.flush()
        return quiz_question.id

    def bulk_insert_quiz_question_translations(self, mappings: Sequence[dict[str, Any]]) -> None:
        self._bulk_insert(QuizQuestionTranslation, mappings)

    def create_flashcard(self, lesson_id: int) -> int:
        flashcard = Flashcard(lesson_id=lesson_id)
        self._session.add(flashcard)
        self._session.flush()
        return flashcard.id

    def bulk_insert_flashcard_translations(self, mappings: Sequence[dict[str, Any]]) -> None:
        self._bulk_insert(FlashcardTranslation, mappings)

    def _bulk_insert(self, model: type[Any], mappings: Sequence[dict[str, Any]]) -> None:
        if not mappings:
            return

        self._session.bulk_insert_mappings(model, list(mappings), render_nulls=True)
