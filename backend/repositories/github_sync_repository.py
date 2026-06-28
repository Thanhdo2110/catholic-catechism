from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from sqlalchemy import delete, select, tuple_
from sqlalchemy.orm import Session

from backend.models.bible import BibleBook, BibleBookTranslation, BibleVerse, BibleVerseTranslation
from backend.models.category import Category, CategoryTranslation
from backend.models.lesson import Lesson, LessonTranslation


class GitHubDataSyncRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def upsert_category(
        self,
        slug: str,
        sort_order: int,
        translations: Sequence[dict[str, Any]],
    ) -> int:
        category = self._session.execute(
            select(Category).where(Category.slug == slug)
        ).scalar_one_or_none()

        if category is None:
            category = Category(slug=slug, sort_order=sort_order)
            self._session.add(category)
            self._session.flush()
        else:
            category.sort_order = sort_order
            self._session.flush()
            self._session.execute(
                delete(CategoryTranslation).where(CategoryTranslation.category_id == category.id)
            )

        translation_mappings = [
            {
                "category_id": category.id,
                **translation,
            }
            for translation in translations
        ]
        self._session.bulk_insert_mappings(
            CategoryTranslation,
            translation_mappings,
            render_nulls=True,
        )
        return category.id

    def replace_lessons_batch(
        self,
        category_id: int,
        lesson_mappings: Sequence[dict[str, Any]],
        translation_mappings: Sequence[dict[str, Any]],
    ) -> None:
        if not lesson_mappings:
            return

        slugs = [lesson["slug"] for lesson in lesson_mappings]
        existing_lessons = self._session.execute(
            select(Lesson.id, Lesson.slug).where(
                Lesson.category_id == category_id,
                Lesson.slug.in_(slugs),
            )
        ).all()
        existing_lesson_ids = [row.id for row in existing_lessons]

        if existing_lesson_ids:
            self._session.execute(
                delete(LessonTranslation).where(LessonTranslation.lesson_id.in_(existing_lesson_ids))
            )
            self._session.execute(delete(Lesson).where(Lesson.id.in_(existing_lesson_ids)))

        self._session.bulk_insert_mappings(Lesson, list(lesson_mappings), render_nulls=True)
        inserted_rows = self._session.execute(
            select(Lesson.id, Lesson.slug).where(
                Lesson.category_id == category_id,
                Lesson.slug.in_(slugs),
            )
        ).all()
        lesson_id_by_slug = {row.slug: row.id for row in inserted_rows}

        resolved_translation_mappings = [
            {
                "lesson_id": lesson_id_by_slug[translation["lesson_slug"]],
                "language_code": translation["language_code"],
                "title": translation["title"],
                "summary": translation["summary"],
                "content_markdown": translation["content_markdown"],
            }
            for translation in translation_mappings
        ]
        self._session.bulk_insert_mappings(
            LessonTranslation,
            resolved_translation_mappings,
            render_nulls=True,
        )

    def sync_bible_books(
        self,
        book_mappings: Sequence[dict[str, Any]],
        translation_mappings: Sequence[dict[str, Any]],
    ) -> dict[int, int]:
        existing_books = self._session.execute(select(BibleBook)).scalars().all()
        existing_by_number = {book.canonical_number: book for book in existing_books}

        for mapping in book_mappings:
            existing = existing_by_number.get(mapping["canonical_number"])
            if existing is None:
                book = BibleBook(
                    canonical_number=mapping["canonical_number"],
                    abbrev=mapping["abbrev"],
                )
                self._session.add(book)
                self._session.flush()
                existing_by_number[book.canonical_number] = book
            else:
                existing.abbrev = mapping["abbrev"]

        book_ids = [book.id for book in existing_by_number.values()]
        if book_ids:
            self._session.execute(
                delete(BibleBookTranslation).where(BibleBookTranslation.bible_book_id.in_(book_ids))
            )

        resolved_translation_mappings = [
            {
                "bible_book_id": existing_by_number[mapping["canonical_number"]].id,
                "language_code": mapping["language_code"],
                "title": mapping["title"],
            }
            for mapping in translation_mappings
        ]
        self._session.bulk_insert_mappings(
            BibleBookTranslation,
            resolved_translation_mappings,
            render_nulls=True,
        )
        return {
            canonical_number: book.id
            for canonical_number, book in existing_by_number.items()
        }

    def replace_bible_verses_batch(
        self,
        verse_mappings: Sequence[dict[str, Any]],
        translation_mappings: Sequence[dict[str, Any]],
    ) -> None:
        if not verse_mappings:
            return

        verse_keys = [
            (
                mapping["bible_book_id"],
                mapping["chapter_number"],
                mapping["verse_number"],
            )
            for mapping in verse_mappings
        ]
        existing_verses = self._session.execute(
            select(
                BibleVerse.id,
                BibleVerse.bible_book_id,
                BibleVerse.chapter_number,
                BibleVerse.verse_number,
            ).where(
                tuple_(
                    BibleVerse.bible_book_id,
                    BibleVerse.chapter_number,
                    BibleVerse.verse_number,
                ).in_(verse_keys)
            )
        ).all()
        existing_verse_ids = [row.id for row in existing_verses]
        if existing_verse_ids:
            self._session.execute(
                delete(BibleVerseTranslation).where(
                    BibleVerseTranslation.bible_verse_id.in_(existing_verse_ids)
                )
            )
            self._session.execute(delete(BibleVerse).where(BibleVerse.id.in_(existing_verse_ids)))

        self._session.bulk_insert_mappings(BibleVerse, list(verse_mappings), render_nulls=True)
        inserted_rows = self._session.execute(
            select(
                BibleVerse.id,
                BibleVerse.bible_book_id,
                BibleVerse.chapter_number,
                BibleVerse.verse_number,
            ).where(
                tuple_(
                    BibleVerse.bible_book_id,
                    BibleVerse.chapter_number,
                    BibleVerse.verse_number,
                ).in_(verse_keys)
            )
        ).all()
        verse_id_by_key = {
            (row.bible_book_id, row.chapter_number, row.verse_number): row.id
            for row in inserted_rows
        }
        resolved_translation_mappings = [
            {
                "bible_verse_id": verse_id_by_key[
                    (
                        mapping["bible_book_id"],
                        mapping["chapter_number"],
                        mapping["verse_number"],
                    )
                ],
                "language_code": mapping["language_code"],
                "text": mapping["text"],
            }
            for mapping in translation_mappings
        ]
        self._session.bulk_insert_mappings(
            BibleVerseTranslation,
            resolved_translation_mappings,
            render_nulls=True,
        )
