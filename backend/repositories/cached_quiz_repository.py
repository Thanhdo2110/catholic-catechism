from __future__ import annotations

from dataclasses import asdict

from backend.repositories.quiz_repository import QuizRepository
from backend.repositories.records import LocalizedQuizQuestionRecord
from backend.repositories.redis_cache_repository import RedisCacheRepository


class CachedQuizRepository:
    def __init__(
        self,
        quiz_repository: QuizRepository,
        cache_repository: RedisCacheRepository,
    ) -> None:
        self._quiz_repository = quiz_repository
        self._cache_repository = cache_repository

    def get_localized(self, quiz_id: int, language: str) -> LocalizedQuizQuestionRecord | None:
        cache_key = self._build_cache_key(quiz_id=quiz_id, language=language)
        cached_payload = self._cache_repository.get_json(cache_key)
        if cached_payload is not None:
            return LocalizedQuizQuestionRecord(**cached_payload)

        localized_quiz = self._quiz_repository.get_localized(quiz_id=quiz_id, language=language)
        if localized_quiz is None:
            return None

        self._cache_repository.set_json(cache_key, asdict(localized_quiz))
        return localized_quiz

    @staticmethod
    def _build_cache_key(quiz_id: int, language: str) -> str:
        return f"quiz:{quiz_id}:{language}"
