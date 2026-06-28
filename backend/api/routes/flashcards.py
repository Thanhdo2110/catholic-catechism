from __future__ import annotations

from flask import Blueprint, current_app

from backend.api.schemas.flashcard import FlashcardReviewRequest
from backend.api.serializers.flashcard import serialize_flashcard_review

flashcards_blueprint = Blueprint("flashcards", __name__)


@flashcards_blueprint.post("/flashcards/<int:flashcard_id>/review")
def review_flashcard(flashcard_id: int) -> tuple[dict[str, object], int]:
    request_model = FlashcardReviewRequest.from_json(flashcard_id=flashcard_id)
    spaced_repetition_service = current_app.extensions["services"]["spaced_repetition_service"]
    review_result = spaced_repetition_service.review_flashcard(
        user_id=request_model.user_id,
        flashcard_id=request_model.flashcard_id,
        answered_correctly=request_model.answered_correctly,
    )
    return serialize_flashcard_review(review_result), 200
