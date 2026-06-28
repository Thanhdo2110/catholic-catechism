from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class QuizDetailRequest:
    quiz_id: int

