from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

from redis import Redis
from redis.exceptions import RedisError


class RedisCacheRepository:
    def __init__(self, client: Redis, default_ttl_seconds: int) -> None:
        self._client = client
        self._default_ttl_seconds = default_ttl_seconds

    def get_json(self, key: str) -> dict[str, Any] | None:
        try:
            cached_value = self._client.get(key)
        except RedisError:
            return None

        if cached_value is None:
            return None

        if isinstance(cached_value, bytes):
            cached_value = cached_value.decode("utf-8")

        return json.loads(cached_value)

    def set_json(
        self,
        key: str,
        payload: Mapping[str, Any],
        ttl_seconds: int | None = None,
    ) -> None:
        try:
            self._client.setex(
                name=key,
                time=ttl_seconds or self._default_ttl_seconds,
                value=json.dumps(payload),
            )
        except RedisError:
            return None
