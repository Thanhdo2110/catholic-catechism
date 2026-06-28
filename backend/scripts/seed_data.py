from __future__ import annotations

import argparse
import json
import logging
import sys
from collections.abc import Iterable
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, ValidationError, ValidationInfo, field_validator
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.app import create_app
from backend.models import db
from backend.repositories.seed_repository import ContentSeedRepository, SeedStats

LOGGER = logging.getLogger("catechism.seed_data")

SAMPLE_SEED_JSON = """\
{
  "categories": [
    {
      "slug": "creed",
      "sort_order": 1,
      "translations": {
        "en": {
          "title": "The Creed",
          "description": "Foundational beliefs of the Catholic faith."
        },
        "vi": {
          "title": "Kinh Tin Kinh",
          "description": "Nhung niem tin nen tang cua duc tin Cong Giao."
        }
      },
      "lessons": [
        {
          "slug": "the-holy-trinity",
          "difficulty": 1,
          "sort_order": 1,
          "translations": {
            "en": {
              "title": "The Holy Trinity",
              "summary": "One God in three divine persons.",
              "content_markdown": "## The Holy Trinity\\nThe Father, Son, and Holy Spirit are one God."
            },
            "vi": {
              "title": "Ba Ngoi Cuc Thanh",
              "summary": "Mot Thien Chua trong ba Ngoi vi.",
              "content_markdown": "## Ba Ngoi Cuc Thanh\\nChua Cha, Chua Con, va Chua Thanh Than la mot Thien Chua."
            }
          },
          "quiz_questions": [
            {
              "difficulty": 1,
              "translations": {
                "en": {
                  "prompt": "Who is the first person of the Holy Trinity?",
                  "options": ["The Father", "The Son", "The Holy Spirit", "Saint Peter"],
                  "correct_option": "The Father",
                  "reference": "CCC 238-242",
                  "explanation": "The Father is the first person of the Holy Trinity."
                },
                "vi": {
                  "prompt": "Ai la Ngoi thu nhat trong Ba Ngoi Cuc Thanh?",
                  "options": ["Chua Cha", "Chua Con", "Chua Thanh Than", "Thanh Phero"],
                  "correct_option": "Chua Cha",
                  "reference": "GLHTCG 238-242",
                  "explanation": "Chua Cha la Ngoi thu nhat trong Ba Ngoi Cuc Thanh."
                }
              }
            }
          ],
          "flashcards": [
            {
              "translations": {
                "en": {
                  "front_text": "What is the Trinity?",
                  "back_text": "One God in three divine persons: Father, Son, and Holy Spirit.",
                  "reference": "CCC 253-255"
                },
                "vi": {
                  "front_text": "Ba Ngoi la gi?",
                  "back_text": "Mot Thien Chua trong ba Ngoi vi: Chua Cha, Chua Con, va Chua Thanh Than.",
                  "reference": "GLHTCG 253-255"
                }
              }
            }
          ]
        }
      ]
    }
  ]
}
"""


class CategoryTranslationInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    title: str = Field(min_length=1, max_length=255)
    description: str | None = None


class LessonTranslationInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    title: str = Field(min_length=1, max_length=255)
    summary: str | None = None
    content_markdown: str = Field(min_length=1)


class QuizQuestionTranslationInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    prompt: str = Field(min_length=1)
    options: list[str] = Field(min_length=2)
    correct_option: str = Field(min_length=1, max_length=255)
    reference: str | None = Field(default=None, max_length=255)
    explanation: str | None = None

    @field_validator("options")
    @classmethod
    def validate_options(cls, value: list[str]) -> list[str]:
        normalized_options = [option.strip() for option in value]
        if any(not option for option in normalized_options):
            raise ValueError("Quiz options must not be empty")
        if len(set(normalized_options)) != len(normalized_options):
            raise ValueError("Quiz options must be unique per translation")
        return normalized_options

    @field_validator("correct_option")
    @classmethod
    def validate_correct_option(cls, value: str, info: ValidationInfo) -> str:
        options = info.data.get("options", [])
        if options and value not in options:
            raise ValueError("correct_option must match one of the provided options")
        return value


class FlashcardTranslationInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    front_text: str = Field(min_length=1)
    back_text: str = Field(min_length=1)
    reference: str | None = Field(default=None, max_length=255)


class LocalizedCategoryTranslations(BaseModel):
    model_config = ConfigDict(extra="forbid")

    en: CategoryTranslationInput
    vi: CategoryTranslationInput


class LocalizedLessonTranslations(BaseModel):
    model_config = ConfigDict(extra="forbid")

    en: LessonTranslationInput
    vi: LessonTranslationInput


class LocalizedQuizQuestionTranslations(BaseModel):
    model_config = ConfigDict(extra="forbid")

    en: QuizQuestionTranslationInput
    vi: QuizQuestionTranslationInput


class LocalizedFlashcardTranslations(BaseModel):
    model_config = ConfigDict(extra="forbid")

    en: FlashcardTranslationInput
    vi: FlashcardTranslationInput


class FlashcardInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    translations: LocalizedFlashcardTranslations


class QuizQuestionInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    difficulty: int = Field(default=1, ge=1, le=5)
    translations: LocalizedQuizQuestionTranslations


class LessonInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    slug: str = Field(min_length=1, max_length=150)
    difficulty: int = Field(default=1, ge=1, le=5)
    sort_order: int = Field(default=0, ge=0)
    translations: LocalizedLessonTranslations
    quiz_questions: list[QuizQuestionInput] = Field(default_factory=list)
    flashcards: list[FlashcardInput] = Field(default_factory=list)


class CategoryInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    slug: str = Field(min_length=1, max_length=120)
    sort_order: int = Field(default=0, ge=0)
    translations: LocalizedCategoryTranslations
    lessons: list[LessonInput] = Field(default_factory=list)


class SeedDataset(BaseModel):
    model_config = ConfigDict(extra="forbid")

    categories: list[CategoryInput] = Field(default_factory=list)


def configure_logging(verbose: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Seed localized catechism content into MySQL via SQLAlchemy repositories.",
    )
    parser.add_argument(
        "--input-file",
        type=Path,
        help="Path to a JSON seed file containing localized catechism content.",
    )
    parser.add_argument(
        "--use-sample",
        action="store_true",
        help="Seed using the embedded SAMPLE_SEED_JSON payload.",
    )
    parser.add_argument(
        "--print-sample",
        action="store_true",
        help="Print the embedded sample JSON payload and exit.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging.",
    )
    return parser.parse_args()


def load_dataset(input_file: Path | None, use_sample: bool) -> SeedDataset:
    if input_file is not None and use_sample:
        raise ValueError("Use either --input-file or --use-sample, not both")

    if input_file is None and not use_sample:
        LOGGER.info("No input file supplied; defaulting to embedded sample data")
        use_sample = True

    if use_sample:
        payload = SAMPLE_SEED_JSON
        source_name = "embedded sample JSON"
    else:
        if input_file is None:
            raise ValueError("An input file is required unless --use-sample is set")
        source_name = str(input_file.resolve())
        payload = input_file.read_text(encoding="utf-8")

    LOGGER.info("Loading seed dataset from %s", source_name)
    parsed_payload = json.loads(payload)
    dataset = SeedDataset.model_validate(parsed_payload)
    validate_unique_slugs(dataset)
    return dataset


def validate_unique_slugs(dataset: SeedDataset) -> None:
    category_slugs = [category.slug for category in dataset.categories]
    lesson_slugs = [lesson.slug for category in dataset.categories for lesson in category.lessons]

    duplicate_categories = find_duplicates(category_slugs)
    if duplicate_categories:
        raise ValueError(
            "Duplicate category slug(s) found in seed payload: "
            + ", ".join(sorted(duplicate_categories))
        )

    duplicate_lessons = find_duplicates(lesson_slugs)
    if duplicate_lessons:
        raise ValueError(
            "Duplicate lesson slug(s) found in seed payload: "
            + ", ".join(sorted(duplicate_lessons))
        )


def find_duplicates(values: Iterable[str]) -> set[str]:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    return duplicates


def seed_dataset(session: Session, dataset: SeedDataset) -> SeedStats:
    repository = ContentSeedRepository(session)
    repository.assert_slugs_available(
        category_slugs=(category.slug for category in dataset.categories),
        lesson_slugs=(lesson.slug for category in dataset.categories for lesson in category.lessons),
    )

    stats = SeedStats()
    category_translation_mappings: list[dict[str, object]] = []
    lesson_translation_mappings: list[dict[str, object]] = []
    quiz_translation_mappings: list[dict[str, object]] = []
    flashcard_translation_mappings: list[dict[str, object]] = []

    for category in dataset.categories:
        category_id = repository.create_category(
            slug=category.slug,
            sort_order=category.sort_order,
        )
        category_translation_mappings.extend(
            build_category_translation_mappings(category_id=category_id, category=category)
        )
        stats.categories += 1
        stats.category_translations += 2

        for lesson in category.lessons:
            lesson_id = repository.create_lesson(
                category_id=category_id,
                slug=lesson.slug,
                difficulty=lesson.difficulty,
                sort_order=lesson.sort_order,
            )
            lesson_translation_mappings.extend(
                build_lesson_translation_mappings(lesson_id=lesson_id, lesson=lesson)
            )
            stats.lessons += 1
            stats.lesson_translations += 2

            for quiz_question in lesson.quiz_questions:
                quiz_question_id = repository.create_quiz_question(
                    lesson_id=lesson_id,
                    difficulty=quiz_question.difficulty,
                )
                quiz_translation_mappings.extend(
                    build_quiz_translation_mappings(
                        quiz_question_id=quiz_question_id,
                        quiz_question=quiz_question,
                    )
                )
                stats.quiz_questions += 1
                stats.quiz_question_translations += 2

            for flashcard in lesson.flashcards:
                flashcard_id = repository.create_flashcard(lesson_id=lesson_id)
                flashcard_translation_mappings.extend(
                    build_flashcard_translation_mappings(
                        flashcard_id=flashcard_id,
                        flashcard=flashcard,
                    )
                )
                stats.flashcards += 1
                stats.flashcard_translations += 2

    repository.bulk_insert_category_translations(category_translation_mappings)
    repository.bulk_insert_lesson_translations(lesson_translation_mappings)
    repository.bulk_insert_quiz_question_translations(quiz_translation_mappings)
    repository.bulk_insert_flashcard_translations(flashcard_translation_mappings)

    return stats


def build_category_translation_mappings(
    category_id: int,
    category: CategoryInput,
) -> list[dict[str, object]]:
    return [
        {
            "category_id": category_id,
            "language_code": "en",
            "title": category.translations.en.title,
            "description": category.translations.en.description,
        },
        {
            "category_id": category_id,
            "language_code": "vi",
            "title": category.translations.vi.title,
            "description": category.translations.vi.description,
        },
    ]


def build_lesson_translation_mappings(
    lesson_id: int,
    lesson: LessonInput,
) -> list[dict[str, object]]:
    return [
        {
            "lesson_id": lesson_id,
            "language_code": "en",
            "title": lesson.translations.en.title,
            "summary": lesson.translations.en.summary,
            "content_markdown": lesson.translations.en.content_markdown,
        },
        {
            "lesson_id": lesson_id,
            "language_code": "vi",
            "title": lesson.translations.vi.title,
            "summary": lesson.translations.vi.summary,
            "content_markdown": lesson.translations.vi.content_markdown,
        },
    ]


def build_quiz_translation_mappings(
    quiz_question_id: int,
    quiz_question: QuizQuestionInput,
) -> list[dict[str, object]]:
    return [
        {
            "quiz_question_id": quiz_question_id,
            "language_code": "en",
            "prompt": quiz_question.translations.en.prompt,
            "options": quiz_question.translations.en.options,
            "correct_option": quiz_question.translations.en.correct_option,
            "reference": quiz_question.translations.en.reference,
            "explanation": quiz_question.translations.en.explanation,
        },
        {
            "quiz_question_id": quiz_question_id,
            "language_code": "vi",
            "prompt": quiz_question.translations.vi.prompt,
            "options": quiz_question.translations.vi.options,
            "correct_option": quiz_question.translations.vi.correct_option,
            "reference": quiz_question.translations.vi.reference,
            "explanation": quiz_question.translations.vi.explanation,
        },
    ]


def build_flashcard_translation_mappings(
    flashcard_id: int,
    flashcard: FlashcardInput,
) -> list[dict[str, object]]:
    return [
        {
            "flashcard_id": flashcard_id,
            "language_code": "en",
            "front_text": flashcard.translations.en.front_text,
            "back_text": flashcard.translations.en.back_text,
            "reference": flashcard.translations.en.reference,
        },
        {
            "flashcard_id": flashcard_id,
            "language_code": "vi",
            "front_text": flashcard.translations.vi.front_text,
            "back_text": flashcard.translations.vi.back_text,
            "reference": flashcard.translations.vi.reference,
        },
    ]


def run_seed_job(dataset: SeedDataset) -> SeedStats:
    app = create_app()
    with app.app_context():
        with Session(db.engine, autoflush=False, expire_on_commit=False) as session:
            try:
                LOGGER.info("Starting localized seed import")
                stats = seed_dataset(session=session, dataset=dataset)
                session.commit()
                LOGGER.info("Seed import committed successfully")
                return stats
            except Exception:
                session.rollback()
                LOGGER.exception("Seed import failed. Transaction rolled back")
                raise


def main() -> int:
    args = parse_args()
    configure_logging(verbose=args.verbose)

    if args.print_sample:
        print(SAMPLE_SEED_JSON)
        return 0

    try:
        dataset = load_dataset(input_file=args.input_file, use_sample=args.use_sample)
        stats = run_seed_job(dataset)
    except (OSError, ValueError, ValidationError, json.JSONDecodeError, SQLAlchemyError) as error:
        LOGGER.error("Unable to seed catechism data: %s", error)
        return 1

    LOGGER.info(
        "Seed summary: categories=%s lessons=%s quiz_questions=%s flashcards=%s "
        "category_translations=%s lesson_translations=%s quiz_question_translations=%s "
        "flashcard_translations=%s",
        stats.categories,
        stats.lessons,
        stats.quiz_questions,
        stats.flashcards,
        stats.category_translations,
        stats.lesson_translations,
        stats.quiz_question_translations,
        stats.flashcard_translations,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
