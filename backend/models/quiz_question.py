from __future__ import annotations

from sqlalchemy import ForeignKey, Index, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models import db
from backend.models.base import TimestampMixin


class QuizQuestion(TimestampMixin, db.Model):
    __tablename__ = "quiz_questions"
    __table_args__ = (
        Index("ix_quiz_questions_lesson_id", "lesson_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    lesson_id: Mapped[int] = mapped_column(
        ForeignKey("lessons.id", ondelete="CASCADE"),
        nullable=False,
    )
    difficulty: Mapped[int] = mapped_column(nullable=False, default=1)
    translations: Mapped[list["QuizQuestionTranslation"]] = relationship(
        back_populates="quiz_question",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class QuizQuestionTranslation(TimestampMixin, db.Model):
    __tablename__ = "quiz_question_translations"
    __table_args__ = (
        UniqueConstraint("quiz_question_id", "language_code", name="uq_quiz_question_language"),
        Index("ix_quiz_question_language_lookup", "quiz_question_id", "language_code"),
        Index("ix_quiz_question_translation_language", "language_code"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    quiz_question_id: Mapped[int] = mapped_column(
        ForeignKey("quiz_questions.id", ondelete="CASCADE"),
        nullable=False,
    )
    language_code: Mapped[str] = mapped_column(String(5), nullable=False)
    prompt: Mapped[str] = mapped_column(Text(), nullable=False)
    options: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    correct_option: Mapped[str] = mapped_column(String(255), nullable=False)
    reference: Mapped[str | None] = mapped_column(String(255), nullable=True)
    explanation: Mapped[str | None] = mapped_column(Text(), nullable=True)

    quiz_question: Mapped[QuizQuestion] = relationship(back_populates="translations")
