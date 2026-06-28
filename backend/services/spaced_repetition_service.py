from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from backend.repositories.flashcard_progress_repository import FlashcardProgressRepository
from backend.repositories.records import FlashcardProgressRecord


LEITNER_INTERVALS: dict[int, timedelta] = {
    1: timedelta(days=1),
    2: timedelta(days=3),
    3: timedelta(days=7),
    4: timedelta(days=14),
    5: timedelta(days=30),
}


@dataclass(frozen=True)
class FlashcardReviewResultDTO:
    user_id: int
    flashcard_id: int
    leitner_level: int
    reviewed_at: datetime
    next_review_at: datetime


class SpacedRepetitionService:
    def __init__(self, progress_repository: FlashcardProgressRepository) -> None:
        self._progress_repository = progress_repository

    def review_flashcard(
        self,
        user_id: int,
        flashcard_id: int,
        answered_correctly: bool,
        reviewed_at: datetime | None = None,
    ) -> FlashcardReviewResultDTO:
        effective_reviewed_at = reviewed_at or datetime.now(UTC)
        existing_progress = self._progress_repository.get_by_user_and_flashcard(
            user_id=user_id,
            flashcard_id=flashcard_id,
        )
        next_level = self._calculate_next_level(existing_progress, answered_correctly)
        next_review_at = effective_reviewed_at + LEITNER_INTERVALS[next_level]
        persisted_progress = self._progress_repository.save_review(
            user_id=user_id,
            flashcard_id=flashcard_id,
            leitner_level=next_level,
            last_reviewed_at=effective_reviewed_at,
            next_review_at=next_review_at,
        )

        return FlashcardReviewResultDTO(
            user_id=persisted_progress.user_id,
            flashcard_id=persisted_progress.flashcard_id,
            leitner_level=persisted_progress.leitner_level,
            reviewed_at=effective_reviewed_at,
            next_review_at=persisted_progress.next_review_at or next_review_at,
        )

    @staticmethod
    def _calculate_next_level(
        progress: FlashcardProgressRecord | None,
        answered_correctly: bool,
    ) -> int:
        if not answered_correctly:
            return 1

        current_level = progress.leitner_level if progress is not None else 1
        return min(current_level + 1, 5)
