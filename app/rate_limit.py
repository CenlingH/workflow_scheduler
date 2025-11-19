import time
import redis

r = redis.Redis(host="localhost", port=6379, db=0)

BUCKET_CAPACITY = 10             # max tokens
REFILL_RATE = 1                  # tokens per second


def allow_request(user_id: str) -> bool:
    """
    Return True if request is allowed, False if rate limited.

    Each user has their own token bucket:
      - redis key: bucket:{user_id}:tokens
      - redis key: bucket:{user_id}:timestamp
    """
    now = time.time()

    token_key = f"bucket:{user_id}:tokens"
    ts_key = f"bucket:{user_id}:timestamp"
    tokens = r.get(token_key)
    last_ts = r.get(ts_key)

    tokens = float(tokens) if tokens else float(BUCKET_CAPACITY)
    last_ts = float(last_ts) if last_ts else now

    elapsed = now - last_ts
    refill = elapsed * REFILL_RATE
    tokens = min(BUCKET_CAPACITY, tokens + refill)

    if tokens < 1:
        r.set(token_key, tokens)
        r.set(ts_key, now)
        return False

    tokens -= 1
    r.set(token_key, tokens)
    r.set(ts_key, now)
    return True
