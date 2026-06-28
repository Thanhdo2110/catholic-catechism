from __future__ import annotations

from dataclasses import dataclass

from flask import request


@dataclass(frozen=True)
class FlashcardReviewRequest:
    user_id: int
    flashcard_id: int
    answered_correctly: bool

    @classmethod
    def from_json(cls, flashcard_id: int) -> "FlashcardReviewRequest":
        payload = request.get_json(silent=True) or {}
        answered_correctly = payload["answered_correctly"]
        if not isinstance(answered_correctly, bool):
            raise ValueError("answered_correctly must be a boolean")

        return cls(
            user_id=int(payload["user_id"]),
            flashcard_id=flashcard_id,
            answered_correctly=answered_correctly,
        )
