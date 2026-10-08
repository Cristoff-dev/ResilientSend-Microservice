# app/core/redis.py
import json
import logging
from typing import Any, Optional
from redis import asyncio as aioredis
from app.core.config import settings

# Setup standard logger for observability
logger = logging.getLogger(__name__)

# Initialize Async Redis Client (Connection Pool)
# Using decode_responses=True ensures we get strings back instead of bytes
redis_client = aioredis.from_url(
    settings.REDIS_URL,
    encoding="utf-8",
    decode_responses=True
)

class IdempotencyManager:
    """
    Handles idempotency logic using Redis to prevent duplicate operations,
    such as sending the same email or charging the same transaction twice.
    """
    
    def __init__(self, redis: aioredis.Redis, expiration: int):
        self.redis = redis
        self.expiration = expiration

    async def get_cached_response(self, idempotency_key: str) -> Optional[dict[str, Any]]:
        """
        Retrieves a previously processed response using the idempotency key.
        Returns None if the key doesn't exist or if Redis is temporarily down.
        """
        try:
            cached_data = await self.redis.get(f"idempotency:{idempotency_key}")
            if cached_data:
                logger.info(f"Idempotency hit for key: {idempotency_key}")
                return json.loads(cached_data)
            return None
        except Exception as e:
            # Fail-Open strategy: If Redis is unreachable, we log the error 
            # and return None to let the main API flow continue working.
            logger.error(f"Redis connection error during idempotency check: {e}")
            return None

    async def save_response(self, idempotency_key: str, response_data: dict[str, Any]) -> None:
        """
        Saves a successful transaction result to Redis with a TTL (Time To Live).
        """
        try:
            await self.redis.set(
                f"idempotency:{idempotency_key}",
                json.dumps(response_data),
                ex=self.expiration
            )
            logger.info(f"Idempotency key saved: {idempotency_key}")
        except Exception as e:
            logger.error(f"Redis connection error during idempotency save: {e}")

# Instantiate a global manager to be used in FastAPI Dependency Injection
idempotency_manager = IdempotencyManager(
    redis=redis_client, 
    expiration=settings.IDEMPOTENCY_EXPIRE_SECONDS
)