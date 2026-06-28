from __future__ import annotations

from sqlalchemy import ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models import db
from backend.models.base import TimestampMixin


class BibleBook(TimestampMixin, db.Model):
    __tablename__ = "bible_books"
    __table_args__ = (
        UniqueConstraint("canonical_number", name="uq_bible_book_canonical_number"),
        UniqueConstraint("abbrev", name="uq_bible_book_abbrev"),
        Index("ix_bible_books_abbrev", "abbrev"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    canonical_number: Mapped[int] = mapped_column(Integer(), nullable=False)
    abbrev: Mapped[str] = mapped_column(String(10), nullable=False)
    translations: Mapped[list["BibleBookTranslation"]] = relationship(
        back_populates="bible_book",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    verses: Mapped[list["BibleVerse"]] = relationship(
        back_populates="bible_book",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class BibleBookTranslation(TimestampMixin, db.Model):
    __tablename__ = "bible_book_translations"
    __table_args__ = (
        UniqueConstraint("bible_book_id", "language_code", name="uq_bible_book_language"),
        Index("ix_bible_book_language_lookup", "bible_book_id", "language_code"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    bible_book_id: Mapped[int] = mapped_column(
        ForeignKey("bible_books.id", ondelete="CASCADE"),
        nullable=False,
    )
    language_code: Mapped[str] = mapped_column(String(5), nullable=False)
    title: Mapped[str] = mapped_column(String(120), nullable=False)

    bible_book: Mapped[BibleBook] = relationship(back_populates="translations")


class BibleVerse(TimestampMixin, db.Model):
    __tablename__ = "bible_verses"
    __table_args__ = (
        UniqueConstraint(
            "bible_book_id",
            "chapter_number",
            "verse_number",
            name="uq_bible_verse_lookup",
        ),
        Index("ix_bible_verse_book_chapter", "bible_book_id", "chapter_number"),
        Index("ix_bible_verse_book_chapter_verse", "bible_book_id", "chapter_number", "verse_number"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    bible_book_id: Mapped[int] = mapped_column(
        ForeignKey("bible_books.id", ondelete="CASCADE"),
        nullable=False,
    )
    chapter_number: Mapped[int] = mapped_column(Integer(), nullable=False)
    verse_number: Mapped[int] = mapped_column(Integer(), nullable=False)
    bible_book: Mapped[BibleBook] = relationship(back_populates="verses")
    translations: Mapped[list["BibleVerseTranslation"]] = relationship(
        back_populates="bible_verse",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class BibleVerseTranslation(TimestampMixin, db.Model):
    __tablename__ = "bible_verse_translations"
    __table_args__ = (
        UniqueConstraint("bible_verse_id", "language_code", name="uq_bible_verse_language"),
        Index("ix_bible_verse_language_lookup", "bible_verse_id", "language_code"),
        Index("ix_bible_verse_translation_language", "language_code"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    bible_verse_id: Mapped[int] = mapped_column(
        ForeignKey("bible_verses.id", ondelete="CASCADE"),
        nullable=False,
    )
    language_code: Mapped[str] = mapped_column(String(5), nullable=False)
    text: Mapped[str] = mapped_column(Text(), nullable=False)

    bible_verse: Mapped[BibleVerse] = relationship(back_populates="translations")
