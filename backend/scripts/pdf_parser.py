from __future__ import annotations

import argparse
import json
import logging
import re
import tempfile
import unicodedata
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

try:
    import requests
    from pypdf import PdfReader
except ImportError as error:  # pragma: no cover - runtime dependency guard
    raise SystemExit(
        "Missing runtime dependencies for pdf_parser.py. "
        "Install them with `pip install requests pypdf`."
    ) from error

LOGGER = logging.getLogger("catechism.pdf_parser")

ROOT_DIR = Path(__file__).resolve().parents[2]
OUTPUT_PATH = ROOT_DIR / "backend" / "scripts" / "data_source.json"

SOURCE_ONE_URL = "https://kholuu.wordpress.com/wp-content/uploads/2015/04/giaolyconggiao_full.pdf"
SOURCE_TWO_URL = "https://ducmefatimamancoi.org/images/file/gzN7Tazg0QgQAMxK/giaolyhonnhangiadinh.pdf"
DOWNLOAD_CHUNK_SIZE = 1024 * 1024
SOURCE_ONE_BATCH_SIZE = 50
SOURCE_REQUEST_TIMEOUT = (20, 180)

SOURCE_ONE_MARKER = re.compile(r"^\s*(?P<reference>\d{1,4}(?:-\d{1,4})?)\.\s*(?P<text>.+)\s*$")
SOURCE_TWO_LESSON_MARKER = re.compile(
    r"^\s*B[àa]i\s+(?P<number>\d+)\s*:\s*(?P<title>.+?)\s*$",
    re.IGNORECASE,
)
SOURCE_TWO_QUESTION_MARKER = re.compile(
    r"^\s*(?:\d+\.\s*)?(?:H\.|Hỏi\s*:)\s*(?P<text>.+?)\s*$",
    re.IGNORECASE,
)
SOURCE_TWO_ANSWER_MARKER = re.compile(
    r"^\s*(?:\d+\.\s*)?(?:T\.|Thưa\s*:)\s*(?P<text>.+?)\s*$",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class ParsedQuizSeed:
    reference_text: str
    question_vi: str
    option_a_vi: str
    explanation_vi: str
    question_en: str
    option_a_en: str
    explanation_en: str


@dataclass(frozen=True)
class ParsedFlashcardSeed:
    reference_text: str
    front_text_vi: str
    back_text_vi: str
    front_text_en: str
    back_text_en: str


@dataclass(frozen=True)
class LessonBlock:
    lesson_number: int
    title_vi: str
    body_vi: str
    quiz_items: list[ParsedQuizSeed]
    flashcards: list[ParsedFlashcardSeed]


def configure_logging(verbose: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download catechism PDFs, parse localized content, and write backend/scripts/data_source.json.",
    )
    parser.add_argument(
        "--output-file",
        type=Path,
        default=OUTPUT_PATH,
        help="Destination JSON file. Defaults to backend/scripts/data_source.json.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging.",
    )
    return parser.parse_args()


@contextmanager
def streamed_pdf_download(url: str, source_name: str) -> Iterator[Path]:
    temp_path: Path | None = None
    LOGGER.info("Downloading %s from %s", source_name, url)

    try:
        with requests.get(url, stream=True, timeout=SOURCE_REQUEST_TIMEOUT) as response:
            response.raise_for_status()

            with tempfile.NamedTemporaryFile(
                mode="wb",
                delete=False,
                suffix=".pdf",
                prefix="catechism_",
            ) as temporary_file:
                temp_path = Path(temporary_file.name)
                total_bytes = 0
                for chunk in response.iter_content(chunk_size=DOWNLOAD_CHUNK_SIZE):
                    if not chunk:
                        continue
                    temporary_file.write(chunk)
                    total_bytes += len(chunk)

            LOGGER.info(
                "Downloaded %s to %s (%s bytes)",
                source_name,
                temp_path,
                total_bytes,
            )
            yield temp_path
    except requests.RequestException:
        LOGGER.exception("Failed to download %s", source_name)
        raise
    finally:
        if temp_path is not None:
            try:
                temp_path.unlink(missing_ok=True)
                LOGGER.debug("Deleted temporary file %s", temp_path)
            except OSError:
                LOGGER.warning("Could not delete temporary file %s", temp_path, exc_info=True)


def extract_pdf_text(pdf_path: Path, source_name: str) -> str:
    LOGGER.info("Extracting text from %s", source_name)
    try:
        reader = PdfReader(str(pdf_path))
    except Exception:
        LOGGER.exception("Unable to open %s as PDF", source_name)
        raise

    page_texts: list[str] = []
    for page_number, page in enumerate(reader.pages, start=1):
        try:
            extracted = page.extract_text() or ""
            page_texts.append(extracted)
        except Exception:
            LOGGER.warning(
                "Skipping unreadable page %s in %s",
                page_number,
                source_name,
                exc_info=True,
            )

    combined_text = "\n\n".join(page_texts)
    if not combined_text.strip():
        raise ValueError(f"No extractable text found in {source_name}")

    LOGGER.info("Extracted %s characters from %s", len(combined_text), source_name)
    return combined_text


def normalize_text(raw_text: str) -> str:
    normalized = unicodedata.normalize("NFKC", raw_text)
    normalized = normalized.replace("\x00", "")
    normalized = normalized.replace("\r\n", "\n").replace("\r", "\n")
    normalized = normalized.replace("\u00a0", " ")
    normalized = normalized.replace("ﬁ", "fi").replace("ﬂ", "fl")
    normalized = re.sub(r"(\w)-\n(\w)", r"\1\2", normalized)
    normalized = re.sub(r"[ \t]+", " ", normalized)
    normalized = re.sub(r"\n{3,}", "\n\n", normalized)
    return normalized


def clean_line(line: str) -> str:
    line = line.strip(" \t")
    line = re.sub(r"\s+", " ", line)
    return line.strip()


def slugify(value: str) -> str:
    ascii_value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", ascii_value.lower()).strip("-")
    return slug or "item"


def first_sentence(text: str, max_length: int = 240) -> str:
    cleaned = collapse_text(text)
    if not cleaned:
        return ""

    match = re.match(r"(.+?[.!?])(\s|$)", cleaned)
    sentence = match.group(1).strip() if match else cleaned
    if len(sentence) <= max_length:
        return sentence
    return sentence[: max_length - 3].rstrip(" ,;:") + "..."


def collapse_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def is_source_one_noise(line: str) -> bool:
    if not line:
        return True
    if re.fullmatch(r"\d+", line):
        return True
    if "wordpress.com" in line.lower():
        return True
    if "giaolyconggiao_full" in line.lower():
        return True
    if line.lower() in {"muc luc", "mục lục"}:
        return True
    return False


def is_source_two_noise(line: str) -> bool:
    lowered = line.lower()
    if not line:
        return True
    if re.fullmatch(r"\d+", line):
        return True
    if re.search(r"\.{4,}\s*\d+\s*$", line):
        return True
    if "ducmefatimamancoi.org" in lowered:
        return True
    if "uy ban giao ly" in lowered or "ủy ban giáo lý" in lowered:
        return True
    if "trở về trang mục lục" in lowered or "trở lên đầu trang" in lowered:
        return True
    if "giaolyhonnhangiadinh.pdf" in lowered:
        return True
    return False


def parse_source_one(text: str) -> list[ParsedQuizSeed]:
    lines = [clean_line(line) for line in normalize_text(text).splitlines()]
    parsed_entries: list[ParsedQuizSeed] = []
    current_reference: str | None = None
    current_prompt: str | None = None
    current_body_lines: list[str] = []

    def finalize_current() -> None:
        nonlocal current_reference, current_prompt, current_body_lines
        if current_reference is None or current_prompt is None:
            return

        body_lines = [
            line
            for line in current_body_lines
            if line and not re.fullmatch(r"\d{1,4}(?:-\d{1,4})?(?:\s*,\s*\d{1,4}(?:-\d{1,4})?)*", line)
        ]
        answer_text = collapse_text(" ".join(body_lines))
        if current_prompt.endswith("?"):
            question_vi = current_prompt
            option_a_vi = first_sentence(answer_text or current_prompt)
            explanation_vi = answer_text or current_prompt
        else:
            merged_text = collapse_text(" ".join([current_prompt, answer_text]))
            question_vi = f"Đoạn giáo lý số {current_reference} trình bày điều gì?"
            option_a_vi = first_sentence(merged_text)
            explanation_vi = merged_text

        if option_a_vi and explanation_vi:
            parsed_entries.append(
                ParsedQuizSeed(
                    reference_text=current_reference,
                    question_vi=question_vi,
                    option_a_vi=option_a_vi,
                    explanation_vi=explanation_vi,
                    question_en=(
                        f"According to Catechism No. {current_reference}, "
                        "which statement best reflects the teaching?"
                    ),
                    option_a_en=f"Primary teaching extracted from Catechism No. {current_reference}.",
                    explanation_en=(
                        f"English translation pending. Review the Vietnamese passage parsed from "
                        f"Catechism No. {current_reference}."
                    ),
                )
            )

        current_reference = None
        current_prompt = None
        current_body_lines = []

    for raw_line in lines:
        line = raw_line.strip()
        if is_source_one_noise(line):
            continue

        marker = SOURCE_ONE_MARKER.match(line)
        if marker:
            finalize_current()
            current_reference = marker.group("reference")
            current_prompt = collapse_text(marker.group("text"))
            current_body_lines = []
            continue

        if current_reference is not None:
            current_body_lines.append(line)

    finalize_current()
    if not parsed_entries:
        raise ValueError("No numbered catechism paragraphs were parsed from source one")

    LOGGER.info("Parsed %s numbered catechism entries from source one", len(parsed_entries))
    return parsed_entries


def parse_source_two(text: str) -> list[LessonBlock]:
    lines = [clean_line(line) for line in normalize_text(text).splitlines()]
    lessons: list[LessonBlock] = []
    current_number: int | None = None
    current_title: str | None = None
    current_lines: list[str] = []

    def finalize_lesson() -> None:
        nonlocal current_number, current_title, current_lines
        if current_number is None or current_title is None:
            return

        body_lines = [line for line in current_lines if line and not is_source_two_noise(line)]
        body_text = collapse_text(" ".join(body_lines))
        if not body_text:
            current_number = None
            current_title = None
            current_lines = []
            return

        quiz_items = parse_source_two_questions(
            lesson_number=current_number,
            lesson_title_vi=current_title,
            lines=body_lines,
        )
        flashcards = build_flashcards_from_quiz_items(quiz_items)
        lessons.append(
            LessonBlock(
                lesson_number=current_number,
                title_vi=current_title,
                body_vi=body_text,
                quiz_items=quiz_items,
                flashcards=flashcards,
            )
        )
        current_number = None
        current_title = None
        current_lines = []

    for raw_line in lines:
        line = raw_line.strip()
        if is_source_two_noise(line):
            continue

        marker = SOURCE_TWO_LESSON_MARKER.match(line)
        if marker:
            finalize_lesson()
            current_number = int(marker.group("number"))
            current_title = collapse_text(marker.group("title"))
            current_lines = []
            continue

        if current_number is not None:
            current_lines.append(line)

    finalize_lesson()
    deduplicated_lessons = deduplicate_source_two_lessons(lessons)
    if not deduplicated_lessons:
        raise ValueError("No lesson blocks were parsed from source two")

    LOGGER.info("Parsed %s lesson blocks from source two", len(deduplicated_lessons))
    return deduplicated_lessons


def deduplicate_source_two_lessons(lessons: list[LessonBlock]) -> list[LessonBlock]:
    deduplicated: dict[int, LessonBlock] = {}
    for lesson in lessons:
        existing = deduplicated.get(lesson.lesson_number)
        if existing is None or len(lesson.body_vi) > len(existing.body_vi):
            deduplicated[lesson.lesson_number] = lesson
    return [deduplicated[number] for number in sorted(deduplicated)]


def parse_source_two_questions(
    lesson_number: int,
    lesson_title_vi: str,
    lines: list[str],
) -> list[ParsedQuizSeed]:
    parsed_questions: list[ParsedQuizSeed] = []
    current_question: str | None = None
    current_answer_lines: list[str] = []

    def finalize_pair() -> None:
        nonlocal current_question, current_answer_lines
        if not current_question:
            current_answer_lines = []
            return

        answer_text = collapse_text(" ".join(current_answer_lines))
        if answer_text:
            parsed_questions.append(
                ParsedQuizSeed(
                    reference_text=f"Bài {lesson_number}",
                    question_vi=current_question,
                    option_a_vi=first_sentence(answer_text),
                    explanation_vi=answer_text,
                    question_en=(
                        f"According to Marriage and Family Catechism Lesson {lesson_number}, "
                        "which answer is correct?"
                    ),
                    option_a_en=f"Primary answer extracted from Lesson {lesson_number}.",
                    explanation_en=(
                        f"English translation pending. Review the Vietnamese answer parsed from "
                        f"Lesson {lesson_number}."
                    ),
                )
            )

        current_question = None
        current_answer_lines = []

    for line in lines:
        question_match = SOURCE_TWO_QUESTION_MARKER.match(line)
        if question_match:
            finalize_pair()
            current_question = collapse_text(question_match.group("text"))
            continue

        answer_match = SOURCE_TWO_ANSWER_MARKER.match(line)
        if answer_match:
            if current_question is None:
                continue
            current_answer_lines = [collapse_text(answer_match.group("text"))]
            continue

        if current_question is not None and current_answer_lines:
            current_answer_lines.append(line)

    finalize_pair()
    if parsed_questions:
        return parsed_questions

    lesson_summary = first_sentence(" ".join(lines))
    return [
        ParsedQuizSeed(
            reference_text=f"Bài {lesson_number}",
            question_vi=f"Bài {lesson_number} dạy điều gì về {lesson_title_vi}?",
            option_a_vi=lesson_summary,
            explanation_vi=collapse_text(" ".join(lines)),
            question_en=(
                f"What does Marriage and Family Catechism Lesson {lesson_number} teach "
                f"about {lesson_title_vi}?"
            ),
            option_a_en=f"Primary teaching extracted from Lesson {lesson_number}.",
            explanation_en=(
                f"English translation pending. Review the Vietnamese lesson content parsed from "
                f"Lesson {lesson_number}."
            ),
        )
    ]


def build_flashcards_from_quiz_items(quiz_items: list[ParsedQuizSeed]) -> list[ParsedFlashcardSeed]:
    return [
        ParsedFlashcardSeed(
            reference_text=item.reference_text,
            front_text_vi=item.question_vi,
            back_text_vi=item.explanation_vi,
            front_text_en=item.question_en,
            back_text_en=item.explanation_en,
        )
        for item in quiz_items
    ]


def build_vi_distractors(
    correct_option: str,
    all_options: list[str],
    reference_text: str,
    context_hint: str,
) -> list[str]:
    choices = [correct_option]
    for candidate in all_options:
        normalized_candidate = collapse_text(candidate)
        if not normalized_candidate or normalized_candidate == correct_option or normalized_candidate in choices:
            continue
        choices.append(normalized_candidate)
        if len(choices) == 4:
            return choices

    fallback_pool = [
        f"Nội dung này liên quan đến {context_hint}, nhưng không phải phát biểu chính của mục {reference_text}.",
        f"Đây là một tóm lược giáo lý lân cận với tham chiếu {reference_text}, không phải câu trả lời đúng.",
        f"Đây là một diễn giải khái quát cùng chủ đề, nhưng không trùng với bản văn được trích xuất.",
    ]
    for candidate in fallback_pool:
        if candidate not in choices:
            choices.append(candidate)
        if len(choices) == 4:
            break
    return choices


def build_en_options(reference_text: str, context_hint: str) -> list[str]:
    return [
        f"Primary teaching extracted from {context_hint} {reference_text}.",
        f"A nearby catechetical statement related to {context_hint} {reference_text}.",
        f"A broader doctrinal summary from the same subject area as {reference_text}.",
        f"A related formulation from the surrounding catechetical material, but not the exact answer.",
    ]


def build_source_one_category(parsed_entries: list[ParsedQuizSeed]) -> dict[str, object]:
    lessons: list[dict[str, object]] = []
    option_pool = [entry.option_a_vi for entry in parsed_entries]

    for batch_index, batch_start in enumerate(range(0, len(parsed_entries), SOURCE_ONE_BATCH_SIZE), start=1):
        batch = parsed_entries[batch_start : batch_start + SOURCE_ONE_BATCH_SIZE]
        start_reference = batch[0].reference_text
        end_reference = batch[-1].reference_text
        lesson_slug = f"catechism-paragraphs-{start_reference}-{end_reference}"
        lesson_title_vi = f"Đoạn Giáo Lý {start_reference}-{end_reference}"
        lesson_title_en = f"Catechism Paragraphs {start_reference}-{end_reference}"
        lesson_body_vi = "\n\n".join(
            f"### {entry.reference_text}\n{entry.explanation_vi}" for entry in batch
        )
        lesson_body_en = (
            f"## {lesson_title_en}\n\n"
            "English translation pending. Refer to the Vietnamese catechism paragraphs "
            "parsed from the source PDF."
        )

        lesson_quiz_questions = [
            {
                "difficulty": 1,
                "translations": {
                    "en": {
                        "prompt": entry.question_en,
                        "options": build_en_options(entry.reference_text, "Catechism No."),
                        "correct_option": build_en_options(entry.reference_text, "Catechism No.")[0],
                        "reference": entry.reference_text,
                        "explanation": entry.explanation_en,
                    },
                    "vi": {
                        "prompt": entry.question_vi,
                        "options": build_vi_distractors(
                            correct_option=entry.option_a_vi,
                            all_options=option_pool,
                            reference_text=entry.reference_text,
                            context_hint="Giáo lý Công giáo",
                        ),
                        "correct_option": entry.option_a_vi,
                        "reference": entry.reference_text,
                        "explanation": entry.explanation_vi,
                    },
                },
            }
            for entry in batch
        ]

        lesson_flashcards = [
            {
                "translations": {
                    "en": {
                        "front_text": entry.question_en,
                        "back_text": entry.explanation_en,
                        "reference": entry.reference_text,
                    },
                    "vi": {
                        "front_text": entry.question_vi,
                        "back_text": entry.explanation_vi,
                        "reference": entry.reference_text,
                    },
                }
            }
            for entry in batch
        ]

        lessons.append(
            {
                "slug": lesson_slug,
                "difficulty": 1,
                "sort_order": batch_index,
                "translations": {
                    "en": {
                        "title": lesson_title_en,
                        "summary": (
                            f"Auto-parsed catechism paragraphs covering references "
                            f"{start_reference} to {end_reference}."
                        ),
                        "content_markdown": lesson_body_en,
                    },
                    "vi": {
                        "title": lesson_title_vi,
                        "summary": (
                            f"Tổng hợp tự động các đoạn giáo lý từ số {start_reference} "
                            f"đến {end_reference}."
                        ),
                        "content_markdown": lesson_body_vi,
                    },
                },
                "quiz_questions": lesson_quiz_questions,
                "flashcards": lesson_flashcards,
            }
        )

    return {
        "slug": "catechism-of-the-catholic-church",
        "sort_order": 1,
        "translations": {
            "en": {
                "title": "Catechism of the Catholic Church",
                "description": "Auto-parsed numbered catechism material with English placeholders.",
            },
            "vi": {
                "title": "Giáo Lý Công Giáo",
                "description": "Dữ liệu giáo lý được tự động phân tích từ nguồn PDF tiếng Việt.",
            },
        },
        "lessons": lessons,
    }


def build_source_two_category(lesson_blocks: list[LessonBlock]) -> dict[str, object]:
    option_pool = [item.option_a_vi for lesson in lesson_blocks for item in lesson.quiz_items]
    lessons: list[dict[str, object]] = []

    for lesson in lesson_blocks:
        lesson_slug = f"bai-{lesson.lesson_number}-{slugify(lesson.title_vi)}"
        lesson_title_en = f"Lesson {lesson.lesson_number}: Marriage and Family Catechism"
        lesson_body_en = (
            f"## {lesson_title_en}\n\n"
            "English translation pending. Refer to the Vietnamese lesson content parsed "
            "from the Marriage and Family Catechism source PDF."
        )

        quiz_questions = []
        for item in lesson.quiz_items:
            en_options = build_en_options(str(lesson.lesson_number), "Lesson")
            vi_options = build_vi_distractors(
                correct_option=item.option_a_vi,
                all_options=option_pool,
                reference_text=item.reference_text,
                context_hint=lesson.title_vi,
            )
            quiz_questions.append(
                {
                    "difficulty": 1,
                    "translations": {
                        "en": {
                            "prompt": item.question_en,
                            "options": en_options,
                            "correct_option": en_options[0],
                            "reference": item.reference_text,
                            "explanation": item.explanation_en,
                        },
                        "vi": {
                            "prompt": item.question_vi,
                            "options": vi_options,
                            "correct_option": item.option_a_vi,
                            "reference": item.reference_text,
                            "explanation": item.explanation_vi,
                        },
                    },
                }
            )

        flashcards = [
            {
                "translations": {
                    "en": {
                        "front_text": flashcard.front_text_en,
                        "back_text": flashcard.back_text_en,
                        "reference": flashcard.reference_text,
                    },
                    "vi": {
                        "front_text": flashcard.front_text_vi,
                        "back_text": flashcard.back_text_vi,
                        "reference": flashcard.reference_text,
                    },
                }
            }
            for flashcard in lesson.flashcards
        ]

        lessons.append(
            {
                "slug": lesson_slug,
                "difficulty": 1,
                "sort_order": lesson.lesson_number,
                "translations": {
                    "en": {
                        "title": lesson_title_en,
                        "summary": f"Auto-parsed content from Marriage and Family Catechism Lesson {lesson.lesson_number}.",
                        "content_markdown": lesson_body_en,
                    },
                    "vi": {
                        "title": f"Bài {lesson.lesson_number}: {lesson.title_vi}",
                        "summary": first_sentence(lesson.body_vi),
                        "content_markdown": f"## Bài {lesson.lesson_number}: {lesson.title_vi}\n\n{lesson.body_vi}",
                    },
                },
                "quiz_questions": quiz_questions,
                "flashcards": flashcards,
            }
        )

    return {
        "slug": "marriage-and-family-catechism",
        "sort_order": 2,
        "translations": {
            "en": {
                "title": "Marriage and Family Catechism",
                "description": "Auto-parsed lesson content with English placeholders.",
            },
            "vi": {
                "title": "Giáo Lý Hôn Nhân Và Gia Đình",
                "description": "Các bài giáo lý hôn nhân và gia đình được tự động phân tích từ PDF.",
            },
        },
        "lessons": lessons,
    }


def build_dataset() -> dict[str, object]:
    LOGGER.info("Building catechism dataset from PDF sources")

    try:
        with streamed_pdf_download(SOURCE_ONE_URL, "Catechism of the Catholic Church (Full)") as pdf_path:
            source_one_text = extract_pdf_text(pdf_path, "Catechism of the Catholic Church (Full)")
        source_one_entries = parse_source_one(source_one_text)
    except Exception:
        LOGGER.exception("Source one parsing failed")
        raise

    try:
        with streamed_pdf_download(SOURCE_TWO_URL, "Marriage & Family Catechism") as pdf_path:
            source_two_text = extract_pdf_text(pdf_path, "Marriage & Family Catechism")
        source_two_lessons = parse_source_two(source_two_text)
    except Exception:
        LOGGER.exception("Source two parsing failed")
        raise

    dataset = {
        "categories": [
            build_source_one_category(source_one_entries),
            build_source_two_category(source_two_lessons),
        ]
    }
    LOGGER.info(
        "Dataset ready with %s categories",
        len(dataset["categories"]),
    )
    return dataset


def write_dataset(dataset: dict[str, object], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = output_path.with_suffix(output_path.suffix + ".tmp")
    LOGGER.info("Writing dataset to %s", output_path)

    try:
        temporary_path.write_text(
            json.dumps(dataset, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        temporary_path.replace(output_path)
    except Exception:
        LOGGER.exception("Failed to write dataset to %s", output_path)
        try:
            temporary_path.unlink(missing_ok=True)
        except OSError:
            LOGGER.warning("Could not delete temporary output file %s", temporary_path, exc_info=True)
        raise


def main() -> int:
    args = parse_args()
    configure_logging(verbose=args.verbose)

    try:
        dataset = build_dataset()
        write_dataset(dataset, args.output_file)
    except Exception as error:
        LOGGER.error("PDF parsing job failed: %s", error)
        return 1

    LOGGER.info("PDF parsing job completed successfully")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
