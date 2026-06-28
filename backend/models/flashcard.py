from __future__ import annotations

from datetime import datetime

from sqlalchemy import ForeignKey, Index, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models import db
from backend.models.base import TimestampMixin


class Flashcard(TimestampMixin, db.Model):
    __tablename__ = "flashcards"
    __table_args__ = (
        Index("ix_flashcards_lesson_id", "lesson_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    lesson_id: Mapped[int] = mapped_column(
        ForeignKey("lessons.id", ondelete="CASCADE"),
        nullable=False,
    )
    translations: Mapped[list["FlashcardTranslation"]] = relationship(
        back_populates="flashcard",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class FlashcardTranslation(TimestampMixin, db.Model):
    __tablename__ = "flashcard_translations"
    __table_args__ = (
        UniqueConstraint("flashcard_id", "language_code", name="uq_flashcard_language"),
        Index("ix_flashcard_language_lookup", "flashcard_id", "language_code"),
        Index("ix_flashcard_translation_language", "language_code"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    flashcard_id: Mapped[int] = mapped_column(
        ForeignKey("flashcards.id", ondelete="CASCADE"),
        nullable=False,
    )
    language_code: Mapped[str] = mapped_column(String(5), nullable=False)
    front_text: Mapped[str] = mapped_column(Text(), nullable=False)
    back_text: Mapped[str] = mapped_column(Text(), nullable=False)
    reference: Mapped[str | None] = mapped_column(String(255), nullable=True)

    flashcard: Mapped[Flashcard] = relationship(back_populates="translations")


class UserFlashcardProgress(TimestampMixin, db.Model):
    __tablename__ = "user_flashcard_progress"
    __table_args__ = (
        UniqueConstraint("user_id", "flashcard_id", name="uq_user_flashcard_progress"),
        Index("ix_user_flashcard_due_lookup", "user_id", "next_review_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    flashcard_id: Mapped[int] = mapped_column(
        ForeignKey("flashcards.id", ondelete="CASCADE"),
        nullable=False,
    )
    leitner_level: Mapped[int] = mapped_column(nullable=False, default=1)
    last_reviewed_at: Mapped[datetime | None] = mapped_column(nullable=True)
    next_review_at: Mapped[datetime | None] = mapped_column(nullable=True)
