from __future__ import annotations

from sqlalchemy import ForeignKey, Index, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models import db
from backend.models.base import TimestampMixin


class Lesson(TimestampMixin, db.Model):
    __tablename__ = "lessons"
    __table_args__ = (
        Index("ix_lessons_category_id", "category_id"),
        Index("ix_lessons_slug", "slug", unique=True),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="RESTRICT"),
        nullable=False,
    )
    slug: Mapped[str] = mapped_column(String(150), nullable=False)
    difficulty: Mapped[int] = mapped_column(nullable=False, default=1)
    sort_order: Mapped[int] = mapped_column(nullable=False, default=0)
    translations: Mapped[list["LessonTranslation"]] = relationship(
        back_populates="lesson",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class LessonTranslation(TimestampMixin, db.Model):
    __tablename__ = "lesson_translations"
    __table_args__ = (
        UniqueConstraint("lesson_id", "language_code", name="uq_lesson_language"),
        Index("ix_lesson_language_lookup", "lesson_id", "language_code"),
        Index("ix_lesson_translation_language", "language_code"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    lesson_id: Mapped[int] = mapped_column(
        ForeignKey("lessons.id", ondelete="CASCADE"),
        nullable=False,
    )
    language_code: Mapped[str] = mapped_column(String(5), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text(), nullable=True)
    content_markdown: Mapped[str] = mapped_column(Text(), nullable=False)

    lesson: Mapped[Lesson] = relationship(back_populates="translations")
