from __future__ import annotations

from datetime import datetime

from sqlalchemy import select

from backend.models import db
from backend.models.flashcard import UserFlashcardProgress
from backend.repositories.records import FlashcardProgressRecord


class FlashcardProgressRepository:
    def get_by_user_and_flashcard(
        self,
        user_id: int,
        flashcard_id: int,
    ) -> FlashcardProgressRecord | None:
        query = select(UserFlashcardProgress).where(
            UserFlashcardProgress.user_id == user_id,
            UserFlashcardProgress.flashcard_id == flashcard_id,
        )
        progress = db.session.execute(query).scalar_one_or_none()
        if progress is None:
            return None

        return self._to_record(progress)

    def save_review(
        self,
        user_id: int,
        flashcard_id: int,
        leitner_level: int,
        last_reviewed_at: datetime,
        next_review_at: datetime,
    ) -> FlashcardProgressRecord:
        progress = db.session.execute(
            select(UserFlashcardProgress).where(
                UserFlashcardProgress.user_id == user_id,
                UserFlashcardProgress.flashcard_id == flashcard_id,
            )
        ).scalar_one_or_none()

        if progress is None:
            progress = UserFlashcardProgress(
                user_id=user_id,
                flashcard_id=flashcard_id,
            )
            db.session.add(progress)

        progress.leitner_level = leitner_level
        progress.last_reviewed_at = last_reviewed_at
        progress.next_review_at = next_review_at
        db.session.commit()
        db.session.refresh(progress)

        return self._to_record(progress)

    @staticmethod
    def _to_record(progress: UserFlashcardProgress) -> FlashcardProgressRecord:
        return FlashcardProgressRecord(
            id=progress.id,
            user_id=progress.user_id,
            flashcard_id=progress.flashcard_id,
            leitner_level=progress.leitner_level,
            last_reviewed_at=progress.last_reviewed_at,
            next_review_at=progress.next_review_at,
        )
