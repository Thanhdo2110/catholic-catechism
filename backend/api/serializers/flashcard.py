from __future__ import annotations

from backend.services.spaced_repetition_service import FlashcardReviewResultDTO


def serialize_flashcard_review(review: FlashcardReviewResultDTO) -> dict[str, object]:
    return {
        "user_id": review.user_id,
        "flashcard_id": review.flashcard_id,
        "leitner_level": review.leitner_level,
        "reviewed_at": review.reviewed_at.isoformat(),
        "next_review_at": review.next_review_at.isoformat(),
    }
