from __future__ import annotations

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from backend.models.bible import BibleBook, BibleBookTranslation, BibleVerse, BibleVerseTranslation
from backend.models.category import Category, CategoryTranslation
from backend.models.flashcard import Flashcard, FlashcardTranslation, UserFlashcardProgress
from backend.models.lesson import Lesson, LessonTranslation
from backend.models.quiz_question import QuizQuestion, QuizQuestionTranslation
from backend.models.user import User

__all__ = [
    "BibleBook",
    "BibleBookTranslation",
    "BibleVerse",
    "BibleVerseTranslation",
    "Category",
    "CategoryTranslation",
    "Flashcard",
    "FlashcardTranslation",
    "Lesson",
    "LessonTranslation",
    "QuizQuestion",
    "QuizQuestionTranslation",
    "User",
    "UserFlashcardProgress",
    "db",
]
