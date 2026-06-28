from __future__ import annotations

import argparse
import asyncio
import json
import logging
import sys
from collections.abc import Iterable, Iterator, Sequence
from dataclasses import dataclass
from itertools import zip_longest
from pathlib import Path
from typing import Callable

import aiohttp
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.app import create_app
from backend.models import db
from backend.repositories.github_sync_repository import GitHubDataSyncRepository

LOGGER = logging.getLogger("catechism.github_data_sync")

GITHUB_API_BASE = "https://api.github.com"
CCC_RELEASE_API_URL = f"{GITHUB_API_BASE}/repos/aseemsavio/catholicism-in-json/releases/latest"
BIBLE_EN_URL = "https://raw.githubusercontent.com/thiagobodruk/bible/master/json/en_kjv.json"
BIBLE_VI_URL = "https://raw.githubusercontent.com/thiagobodruk/bible/master/json/vi_vietnamese.json"
DEFAULT_VI_CCC_PATH = ROOT_DIR / "backend" / "scripts" / "data_source.json"
DEFAULT_BATCH_SIZE = 500
REQUEST_TIMEOUT = aiohttp.ClientTimeout(total=300, connect=30, sock_read=300)
CCC_CATEGORY_SLUG = "ccc-paragraph-sync"
HTTP_HEADERS = {
    "Accept": "application/json, text/plain;q=0.9, */*;q=0.8",
    "User-Agent": "CatholicCatechismDataSync/1.0",
}
MISSING_VERSE_PLACEHOLDERS = {
    "en": "[Verse not present in this translation]",
    "vi": "[Câu này không có trong bản dịch này]",
}

CANONICAL_BIBLE_BOOKS: tuple[tuple[str, str, str], ...] = (
    ("gn", "Genesis", "Sáng Thế Ký"),
    ("ex", "Exodus", "Xuất Ê-díp-tô Ký"),
    ("lv", "Leviticus", "Lê-vi Ký"),
    ("nm", "Numbers", "Dân Số Ký"),
    ("dt", "Deuteronomy", "Phục Truyền Luật Lệ Ký"),
    ("js", "Joshua", "Giô-suê"),
    ("jud", "Judges", "Các Quan Xét"),
    ("rt", "Ruth", "Ru-tơ"),
    ("1sm", "1 Samuel", "1 Sa-mu-ên"),
    ("2sm", "2 Samuel", "2 Sa-mu-ên"),
    ("1kgs", "1 Kings", "1 Các Vua"),
    ("2kgs", "2 Kings", "2 Các Vua"),
    ("1ch", "1 Chronicles", "1 Sử Ký"),
    ("2ch", "2 Chronicles", "2 Sử Ký"),
    ("ezr", "Ezra", "Ê-xơ-ra"),
    ("ne", "Nehemiah", "Nê-hê-mi"),
    ("et", "Esther", "Ê-xơ-tê"),
    ("job", "Job", "Gióp"),
    ("ps", "Psalms", "Thi Thiên"),
    ("prv", "Proverbs", "Châm Ngôn"),
    ("ec", "Ecclesiastes", "Truyền Đạo"),
    ("so", "Song of Solomon", "Nhã Ca"),
    ("is", "Isaiah", "Ê-sai"),
    ("jr", "Jeremiah", "Giê-rê-mi"),
    ("lm", "Lamentations", "Ca Thương"),
    ("ez", "Ezekiel", "Ê-xê-chi-ên"),
    ("dn", "Daniel", "Đa-ni-ên"),
    ("ho", "Hosea", "Ô-sê"),
    ("jl", "Joel", "Giô-ên"),
    ("am", "Amos", "A-mốt"),
    ("ob", "Obadiah", "Áp-đia"),
    ("jn", "Jonah", "Giô-na"),
    ("mi", "Micah", "Mi-chê"),
    ("na", "Nahum", "Na-hum"),
    ("hk", "Habakkuk", "Ha-ba-cúc"),
    ("zp", "Zephaniah", "Sô-phô-ni"),
    ("hg", "Haggai", "A-ghê"),
    ("zc", "Zechariah", "Xa-cha-ri"),
    ("ml", "Malachi", "Ma-la-chi"),
    ("mt", "Matthew", "Ma-thi-ơ"),
    ("mk", "Mark", "Mác"),
    ("lk", "Luke", "Lu-ca"),
    ("jo", "John", "Giăng"),
    ("act", "Acts", "Công Vụ Các Sứ Đồ"),
    ("rm", "Romans", "Rô-ma"),
    ("1co", "1 Corinthians", "1 Cô-rinh-tô"),
    ("2co", "2 Corinthians", "2 Cô-rinh-tô"),
    ("gl", "Galatians", "Ga-la-ti"),
    ("eph", "Ephesians", "Ê-phê-sô"),
    ("ph", "Philippians", "Phi-líp"),
    ("cl", "Colossians", "Cô-lô-se"),
    ("1ts", "1 Thessalonians", "1 Tê-sa-lô-ni-ca"),
    ("2ts", "2 Thessalonians", "2 Tê-sa-lô-ni-ca"),
    ("1tm", "1 Timothy", "1 Ti-mô-thê"),
    ("2tm", "2 Timothy", "2 Ti-mô-thê"),
    ("tt", "Titus", "Tít"),
    ("phm", "Philemon", "Phi-lê-môn"),
    ("hb", "Hebrews", "Hê-bơ-rơ"),
    ("jm", "James", "Gia-cơ"),
    ("1pe", "1 Peter", "1 Phi-e-rơ"),
    ("2pe", "2 Peter", "2 Phi-e-rơ"),
    ("1jo", "1 John", "1 Giăng"),
    ("2jo", "2 John", "2 Giăng"),
    ("3jo", "3 John", "3 Giăng"),
    ("jd", "Jude", "Giu-đe"),
    ("re", "Revelation", "Khải Huyền"),
)


@dataclass(frozen=True)
class CccParagraphRecord:
    paragraph_number: int
    english_text: str
    vietnamese_text: str


@dataclass(frozen=True)
class BibleVerseSeed:
    canonical_book_number: int
    book_abbrev: str
    chapter_number: int
    verse_number: int
    text_en: str
    text_vi: str


def configure_logging(verbose: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch multilingual CCC and Bible data from GitHub and sync it into MySQL.",
    )
    parser.add_argument(
        "--vi-ccc-file",
        type=Path,
        default=DEFAULT_VI_CCC_PATH,
        help="Path to the Vietnamese CCC JSON parsed from PDF.",
    )
    parser.add_argument(
        "--bible-en-url",
        default=BIBLE_EN_URL,
        help="English Bible JSON URL.",
    )
    parser.add_argument(
        "--bible-vi-url",
        default=BIBLE_VI_URL,
        help="Vietnamese Bible JSON URL.",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=DEFAULT_BATCH_SIZE,
        help="Bulk insert batch size.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging.",
    )
    return parser.parse_args()


async def fetch_text(session: aiohttp.ClientSession, url: str, label: str) -> str:
    LOGGER.info("Fetching %s from %s", label, url)
    try:
        async with session.get(url) as response:
            response.raise_for_status()
            payload = await response.text()
            LOGGER.info("Fetched %s (%s bytes)", label, len(payload.encode("utf-8")))
            return payload
    except aiohttp.ClientError:
        LOGGER.exception("Failed to fetch %s", label)
        raise


async def load_local_text(path: Path) -> str:
    LOGGER.info("Reading local Vietnamese CCC data from %s", path)
    return await asyncio.to_thread(path.read_text, encoding="utf-8")


async def resolve_ccc_asset_url(session: aiohttp.ClientSession) -> str:
    LOGGER.info("Resolving latest CCC release asset URL from GitHub API")
    try:
        async with session.get(CCC_RELEASE_API_URL) as response:
            response.raise_for_status()
            release_payload = await response.json()
    except aiohttp.ClientError:
        LOGGER.exception("Failed to resolve latest CCC release")
        raise

    assets = release_payload.get("assets", [])
    for asset in assets:
        if asset.get("name") == "catechism.json":
            asset_url = asset["browser_download_url"]
            LOGGER.info("Resolved CCC asset URL: %s", asset_url)
            return asset_url

    raise ValueError("Latest CCC release did not include catechism.json")


async def fetch_source_payloads(
    vi_ccc_path: Path,
    bible_en_url: str,
    bible_vi_url: str,
) -> tuple[str, str, str, str]:
    async with aiohttp.ClientSession(timeout=REQUEST_TIMEOUT, headers=HTTP_HEADERS) as session:
        ccc_asset_task = asyncio.create_task(resolve_ccc_asset_url(session))
        vi_ccc_task = asyncio.create_task(load_local_text(vi_ccc_path))
        bible_en_task = asyncio.create_task(fetch_text(session, bible_en_url, "English Bible JSON"))
        bible_vi_task = asyncio.create_task(fetch_text(session, bible_vi_url, "Vietnamese Bible JSON"))

        ccc_asset_url = await ccc_asset_task
        ccc_en_task = asyncio.create_task(fetch_text(session, ccc_asset_url, "English CCC JSON"))

        return await asyncio.gather(
            ccc_en_task,
            vi_ccc_task,
            bible_en_task,
            bible_vi_task,
        )


def strip_bom(text: str) -> str:
    return text.lstrip("\ufeff")


def collapse_text(text: str) -> str:
    return " ".join(text.split()).strip()


def first_sentence(text: str, max_length: int = 240) -> str:
    normalized = collapse_text(text)
    if not normalized:
        return ""

    for delimiter in (". ", "! ", "? "):
        if delimiter in normalized:
            sentence = normalized.split(delimiter, 1)[0] + delimiter.strip()
            break
    else:
        sentence = normalized

    if len(sentence) <= max_length:
        return sentence
    return sentence[: max_length - 3].rstrip(" ,;:") + "..."


def parse_ccc_english(payload: str) -> dict[int, str]:
    parsed = json.loads(strip_bom(payload))
    if not isinstance(parsed, list):
        raise ValueError("English CCC payload must be a JSON array")

    mapping: dict[int, str] = {}
    for row in parsed:
        if not isinstance(row, dict):
            continue
        paragraph_number = int(row["id"])
        paragraph_text = collapse_text(str(row["text"]))
        if paragraph_text:
            mapping[paragraph_number] = paragraph_text

    if len(mapping) != 2865:
        LOGGER.warning("Expected 2865 CCC paragraphs, parsed %s", len(mapping))
    else:
        LOGGER.info("Parsed all 2865 English CCC paragraphs")
    return mapping


def parse_vi_ccc_source(payload: str) -> dict[int, str]:
    parsed = json.loads(strip_bom(payload))
    categories = parsed.get("categories", [])
    if not isinstance(categories, list):
        raise ValueError("Vietnamese CCC JSON must expose a categories array")

    mapping: dict[int, str] = {}
    for category in categories:
        if not isinstance(category, dict):
            continue
        if category.get("slug") != "catechism-of-the-catholic-church":
            continue
        lessons = category.get("lessons", [])
        for lesson in lessons:
            quiz_questions = lesson.get("quiz_questions", [])
            for question in quiz_questions:
                translations = question.get("translations", {})
                vi_translation = translations.get("vi", {})
                reference = str(vi_translation.get("reference", ""))
                paragraph_number = extract_paragraph_number(reference)
                if paragraph_number is None:
                    continue
                paragraph_text = collapse_text(
                    str(
                        vi_translation.get("explanation")
                        or vi_translation.get("correct_option")
                        or ""
                    )
                )
                if not paragraph_text:
                    continue
                existing = mapping.get(paragraph_number, "")
                if len(paragraph_text) > len(existing):
                    mapping[paragraph_number] = paragraph_text

    if not mapping:
        raise ValueError(
            "No Vietnamese CCC paragraph entries were found in backend/scripts/data_source.json. "
            "Run pdf_parser.py first."
        )

    LOGGER.info("Parsed %s Vietnamese CCC paragraphs from local data source", len(mapping))
    return mapping


def extract_paragraph_number(reference: str) -> int | None:
    digits = "".join(character if character.isdigit() else " " for character in reference)
    candidates = [segment for segment in digits.split() if segment]
    if not candidates:
        return None
    return int(candidates[0])


def align_ccc_records(
    english_by_paragraph: dict[int, str],
    vietnamese_by_paragraph: dict[int, str],
) -> list[CccParagraphRecord]:
    aligned_numbers = sorted(set(english_by_paragraph) & set(vietnamese_by_paragraph))
    missing_vi = sorted(set(english_by_paragraph) - set(vietnamese_by_paragraph))
    missing_en = sorted(set(vietnamese_by_paragraph) - set(english_by_paragraph))

    LOGGER.info(
        "CCC alignment complete: matched=%s missing_vi=%s missing_en=%s",
        len(aligned_numbers),
        len(missing_vi),
        len(missing_en),
    )
    if missing_vi:
        LOGGER.warning("Vietnamese CCC is missing %s paragraph(s); first few: %s", len(missing_vi), missing_vi[:10])
    if missing_en:
        LOGGER.warning("English CCC is missing %s paragraph(s); first few: %s", len(missing_en), missing_en[:10])

    if not aligned_numbers:
        raise ValueError("No aligned CCC paragraph pairs were found")

    return [
        CccParagraphRecord(
            paragraph_number=number,
            english_text=english_by_paragraph[number],
            vietnamese_text=vietnamese_by_paragraph[number],
        )
        for number in aligned_numbers
    ]


def parse_bible_payload(payload: str) -> list[dict[str, object]]:
    parsed = json.loads(strip_bom(payload))
    if not isinstance(parsed, list):
        raise ValueError("Bible payload must be a JSON array")
    return parsed


def build_bible_book_mappings() -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    book_mappings: list[dict[str, object]] = []
    translation_mappings: list[dict[str, object]] = []

    for canonical_number, (abbrev, title_en, title_vi) in enumerate(CANONICAL_BIBLE_BOOKS, start=1):
        book_mappings.append(
            {
                "canonical_number": canonical_number,
                "abbrev": abbrev,
            }
        )
        translation_mappings.extend(
            [
                {
                    "canonical_number": canonical_number,
                    "language_code": "en",
                    "title": title_en,
                },
                {
                    "canonical_number": canonical_number,
                    "language_code": "vi",
                    "title": title_vi,
                },
            ]
        )

    return book_mappings, translation_mappings


def generate_bible_verse_seeds(
    english_books: Sequence[dict[str, object]],
    vietnamese_books: Sequence[dict[str, object]],
) -> Iterator[BibleVerseSeed]:
    if len(english_books) != len(CANONICAL_BIBLE_BOOKS):
        raise ValueError(f"Expected 66 English Bible books, found {len(english_books)}")
    if len(vietnamese_books) != len(CANONICAL_BIBLE_BOOKS):
        raise ValueError(f"Expected 66 Vietnamese Bible books, found {len(vietnamese_books)}")

    for canonical_number, (expected_abbrev, _, _) in enumerate(CANONICAL_BIBLE_BOOKS, start=1):
        english_book = english_books[canonical_number - 1]
        vietnamese_book = vietnamese_books[canonical_number - 1]
        english_abbrev = str(english_book.get("abbrev"))
        vietnamese_abbrev = str(vietnamese_book.get("abbrev"))

        if english_abbrev != expected_abbrev or vietnamese_abbrev != expected_abbrev:
            raise ValueError(
                f"Bible source abbreviations diverged at book {canonical_number}: "
                f"expected {expected_abbrev}, got en={english_abbrev}, vi={vietnamese_abbrev}"
            )

        english_chapters = english_book.get("chapters")
        vietnamese_chapters = vietnamese_book.get("chapters")
        if not isinstance(english_chapters, list) or not isinstance(vietnamese_chapters, list):
            raise ValueError(f"Bible book {expected_abbrev} did not expose chapter arrays")
        if len(english_chapters) != len(vietnamese_chapters):
            raise ValueError(
                f"Bible chapter count mismatch for {expected_abbrev}: "
                f"en={len(english_chapters)} vi={len(vietnamese_chapters)}"
            )

        for chapter_number, (english_verses, vietnamese_verses) in enumerate(
            zip(english_chapters, vietnamese_chapters),
            start=1,
        ):
            if not isinstance(english_verses, list) or not isinstance(vietnamese_verses, list):
                raise ValueError(
                    f"Bible chapter arrays invalid for {expected_abbrev} chapter {chapter_number}"
                )
            if len(english_verses) != len(vietnamese_verses):
                LOGGER.warning(
                    "Bible verse count mismatch for %s chapter %s: en=%s vi=%s. "
                    "Proceeding with zip_longest alignment.",
                    expected_abbrev,
                    chapter_number,
                    len(english_verses),
                    len(vietnamese_verses),
                )

            for verse_number, (text_en, text_vi) in enumerate(
                zip_longest(
                    english_verses,
                    vietnamese_verses,
                    fillvalue="",
                ),
                start=1,
            ):
                normalized_en = collapse_text(str(text_en))
                normalized_vi = collapse_text(str(text_vi))

                if not normalized_en and not normalized_vi:
                    continue

                if not normalized_en:
                    normalized_en = MISSING_VERSE_PLACEHOLDERS["en"]
                if not normalized_vi:
                    normalized_vi = MISSING_VERSE_PLACEHOLDERS["vi"]

                yield BibleVerseSeed(
                    canonical_book_number=canonical_number,
                    book_abbrev=expected_abbrev,
                    chapter_number=chapter_number,
                    verse_number=verse_number,
                    text_en=normalized_en,
                    text_vi=normalized_vi,
                )


def batched(iterable: Iterable[object], batch_size: int) -> Iterator[list[object]]:
    batch: list[object] = []
    for item in iterable:
        batch.append(item)
        if len(batch) >= batch_size:
            yield batch
            batch = []
    if batch:
        yield batch


def sync_ccc_content(
    session_factory: Callable[[], Session],
    aligned_records: Sequence[CccParagraphRecord],
    batch_size: int,
) -> None:
    with session_factory() as category_session:
        repository = GitHubDataSyncRepository(category_session)
        try:
            category_id = repository.upsert_category(
                slug=CCC_CATEGORY_SLUG,
                sort_order=10,
                translations=[
                    {
                        "language_code": "en",
                        "title": "Catechism of the Catholic Church Paragraph Sync",
                        "description": "GitHub-sourced English paragraphs aligned with Vietnamese parsed catechism content.",
                    },
                    {
                        "language_code": "vi",
                        "title": "Đồng Bộ Số Giáo Lý Công Giáo",
                        "description": "Các đoạn giáo lý tiếng Anh từ GitHub được ghép với dữ liệu tiếng Việt đã phân tích.",
                    },
                ],
            )
            category_session.commit()
        except Exception:
            category_session.rollback()
            LOGGER.exception("Failed to prepare CCC sync category")
            raise

    for batch_number, batch in enumerate(batched(aligned_records, batch_size), start=1):
        LOGGER.info(
            "Syncing CCC batch %s containing paragraph numbers %s-%s",
            batch_number,
            batch[0].paragraph_number,
            batch[-1].paragraph_number,
        )
        with session_factory() as session:
            repository = GitHubDataSyncRepository(session)
            lesson_mappings = [
                {
                    "category_id": category_id,
                    "slug": f"ccc-paragraph-{record.paragraph_number:04d}",
                    "difficulty": 1,
                    "sort_order": record.paragraph_number,
                }
                for record in batch
            ]
            translation_mappings = []
            for record in batch:
                lesson_slug = f"ccc-paragraph-{record.paragraph_number:04d}"
                translation_mappings.extend(
                    [
                        {
                            "lesson_slug": lesson_slug,
                            "language_code": "en",
                            "title": f"Catechism Paragraph {record.paragraph_number}",
                            "summary": first_sentence(record.english_text),
                            "content_markdown": f"## Paragraph {record.paragraph_number}\n\n{record.english_text}",
                        },
                        {
                            "lesson_slug": lesson_slug,
                            "language_code": "vi",
                            "title": f"Số {record.paragraph_number}",
                            "summary": first_sentence(record.vietnamese_text),
                            "content_markdown": f"## Số {record.paragraph_number}\n\n{record.vietnamese_text}",
                        },
                    ]
                )

            try:
                repository.replace_lessons_batch(
                    category_id=category_id,
                    lesson_mappings=lesson_mappings,
                    translation_mappings=translation_mappings,
                )
                session.commit()
            except Exception:
                session.rollback()
                LOGGER.exception("CCC batch %s failed and was rolled back", batch_number)
                raise


def sync_bible_content(
    session_factory: Callable[[], Session],
    english_payload: str,
    vietnamese_payload: str,
    batch_size: int,
) -> None:
    english_books = parse_bible_payload(english_payload)
    vietnamese_books = parse_bible_payload(vietnamese_payload)
    book_mappings, book_translation_mappings = build_bible_book_mappings()

    with session_factory() as book_session:
        repository = GitHubDataSyncRepository(book_session)
        try:
            book_id_by_number = repository.sync_bible_books(
                book_mappings=book_mappings,
                translation_mappings=book_translation_mappings,
            )
            book_session.commit()
        except Exception:
            book_session.rollback()
            LOGGER.exception("Bible book sync failed and was rolled back")
            raise

    verse_seed_iterator = generate_bible_verse_seeds(english_books, vietnamese_books)
    total_verses = 0

    for batch_number, batch in enumerate(batched(verse_seed_iterator, batch_size), start=1):
        LOGGER.info(
            "Syncing Bible batch %s with %s verse rows",
            batch_number,
            len(batch),
        )
        total_verses += len(batch)
        with session_factory() as session:
            repository = GitHubDataSyncRepository(session)
            verse_mappings = [
                {
                    "bible_book_id": book_id_by_number[seed.canonical_book_number],
                    "chapter_number": seed.chapter_number,
                    "verse_number": seed.verse_number,
                }
                for seed in batch
            ]
            translation_mappings = []
            for seed in batch:
                bible_book_id = book_id_by_number[seed.canonical_book_number]
                translation_mappings.extend(
                    [
                        {
                            "bible_book_id": bible_book_id,
                            "chapter_number": seed.chapter_number,
                            "verse_number": seed.verse_number,
                            "language_code": "en",
                            "text": seed.text_en,
                        },
                        {
                            "bible_book_id": bible_book_id,
                            "chapter_number": seed.chapter_number,
                            "verse_number": seed.verse_number,
                            "language_code": "vi",
                            "text": seed.text_vi,
                        },
                    ]
                )

            try:
                repository.replace_bible_verses_batch(
                    verse_mappings=verse_mappings,
                    translation_mappings=translation_mappings,
                )
                session.commit()
            except Exception:
                session.rollback()
                LOGGER.exception("Bible batch %s failed and was rolled back", batch_number)
                raise

    LOGGER.info("Bible sync completed with %s verse parent rows", total_verses)


def run_pipeline(args: argparse.Namespace) -> None:
    ccc_en_payload, ccc_vi_payload, bible_en_payload, bible_vi_payload = asyncio.run(
        fetch_source_payloads(
            vi_ccc_path=args.vi_ccc_file,
            bible_en_url=args.bible_en_url,
            bible_vi_url=args.bible_vi_url,
        )
    )

    english_by_paragraph = parse_ccc_english(ccc_en_payload)
    vietnamese_by_paragraph = parse_vi_ccc_source(ccc_vi_payload)
    aligned_ccc_records = align_ccc_records(
        english_by_paragraph=english_by_paragraph,
        vietnamese_by_paragraph=vietnamese_by_paragraph,
    )

    app = create_app()
    with app.app_context():
        db.create_all()

        def session_factory() -> Session:
            return Session(db.engine, autoflush=False, expire_on_commit=False)

        sync_ccc_content(
            session_factory=session_factory,
            aligned_records=aligned_ccc_records,
            batch_size=args.batch_size,
        )
        sync_bible_content(
            session_factory=session_factory,
            english_payload=bible_en_payload,
            vietnamese_payload=bible_vi_payload,
            batch_size=args.batch_size,
        )


def main() -> int:
    args = parse_args()
    configure_logging(verbose=args.verbose)

    if args.batch_size < 1:
        LOGGER.error("--batch-size must be greater than zero")
        return 1

    try:
        run_pipeline(args)
    except (OSError, ValueError, json.JSONDecodeError, SQLAlchemyError, aiohttp.ClientError) as error:
        LOGGER.error("GitHub data sync failed: %s", error)
        return 1
    except Exception as error:
        LOGGER.exception("GitHub data sync failed unexpectedly: %s", error)
        return 1

    LOGGER.info("GitHub data sync completed successfully")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
