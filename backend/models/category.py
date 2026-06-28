from __future__ import annotations

from sqlalchemy import ForeignKey, Index, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models import db
from backend.models.base import TimestampMixin


class Category(TimestampMixin, db.Model):
    __tablename__ = "categories"
    __table_args__ = (
        Index("ix_categories_slug", "slug", unique=True),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(120), nullable=False)
    sort_order: Mapped[int] = mapped_column(nullable=False, default=0)
    translations: Mapped[list["CategoryTranslation"]] = relationship(
        back_populates="category",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class CategoryTranslation(TimestampMixin, db.Model):
    __tablename__ = "category_translations"
    __table_args__ = (
        UniqueConstraint("category_id", "language_code", name="uq_category_language"),
        Index("ix_category_language_lookup", "category_id", "language_code"),
        Index("ix_category_translation_language", "language_code"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="CASCADE"),
        nullable=False,
    )
    language_code: Mapped[str] = mapped_column(String(5), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)

    category: Mapped[Category] = relationship(back_populates="translations")
