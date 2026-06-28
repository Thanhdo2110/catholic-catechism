from __future__ import annotations

from flask import Flask
from redis import Redis

from backend.repositories.cached_quiz_repository import CachedQuizRepository
from backend.repositories.flashcard_progress_repository import FlashcardProgressRepository
from backend.repositories.lesson_repository import LessonRepository
from backend.repositories.quiz_repository import QuizRepository
from backend.repositories.redis_cache_repository import RedisCacheRepository


def register_repositories(app: Flask) -> None:
    app.extensions.setdefault("repositories", {})
    redis_client = Redis.from_url(app.config["REDIS_URL"], decode_responses=True)
    cache_repository = RedisCacheRepository(
        client=redis_client,
        default_ttl_seconds=app.config["REDIS_DEFAULT_TTL_SECONDS"],
    )
    quiz_repository = QuizRepository()
    app.extensions["repositories"]["lesson_repository"] = LessonRepository()
    app.extensions["repositories"]["flashcard_progress_repository"] = FlashcardProgressRepository()
    app.extensions["repositories"]["cache_repository"] = cache_repository
    app.extensions["repositories"]["quiz_repository"] = quiz_repository
    app.extensions["repositories"]["cached_quiz_repository"] = CachedQuizRepository(
        quiz_repository=quiz_repository,
        cache_repository=cache_repository,
    )
