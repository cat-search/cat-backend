from functools import wraps
from dataclasses import dataclass
from asyncpg.pool import Pool
import time
import httpx


# Shared application variables class
@dataclass
class CatState:
    db_pool:   Pool = None                 # DB connection pool
    ht_client: httpx.AsyncClient = None    # Http client


def measure_latency(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = await func(*args, **kwargs)
        end = time.perf_counter()
        latency = end - start
        return result, latency

    return wrapper
