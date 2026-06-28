from __future__ import annotations

from dataclasses import dataclass

from flask import request


@dataclass(frozen=True)
class LessonListRequest:
    category_id: int | None = None

    @classmethod
    def from_query(cls) -> "LessonListRequest":
        return cls(category_id=request.args.get("category_id", type=int))

