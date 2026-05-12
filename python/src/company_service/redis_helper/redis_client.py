import os
import redis

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")

redis_client = redis.from_url(REDIS_URL, decode_responses=True)

RESULT_KEY_PREFIX = "result:"
RESULT_TTL_SECONDS = 60

PROCESSING_KEY_PREFIX = "processing:"
PROCESSING_TTL_SECONDS = 120  # safety expiry in case consumer crashes before setting result
