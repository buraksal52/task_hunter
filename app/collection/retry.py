from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

import httpx

TRANSIENT_STATUS_CODES = {408, 425, 429, 500, 502, 503, 504}


@dataclass(frozen=True)
class RetryDecision:
    retry: bool
    delay_seconds: int
    reason: str


def retry_delay_seconds(attempt: int, retry_after: int | None = None, cap: int = 3600) -> int:
    if retry_after is not None:
        return max(0, min(retry_after, cap))
    return min(cap, 5 * (2 ** max(0, attempt - 1)))


def decide_retry(
    attempt: int,
    max_attempts: int,
    status_code: int | None = None,
    retry_after: int | None = None,
    transient_error: bool = False,
) -> RetryDecision:
    if attempt >= max_attempts:
        return RetryDecision(False, 0, "attempt limit reached")
    if status_code is not None and status_code not in TRANSIENT_STATUS_CODES:
        return RetryDecision(False, 0, "permanent HTTP status")
    if status_code is None and not transient_error:
        return RetryDecision(False, 0, "error is not marked transient")
    return RetryDecision(
        True,
        retry_delay_seconds(attempt, retry_after),
        "transient error with bounded backoff",
    )


async def fetch_with_retry(
    fetch: Callable[[], Awaitable[Any]],
    max_attempts: int = 3,
    sleep: Callable[[float], Awaitable[None]] | None = None,
) -> Any:
    """Retry only transient HTTP/network failures; never retry malformed data or 4xx."""
    import asyncio

    sleep = sleep or asyncio.sleep
    for attempt in range(1, max_attempts + 1):
        try:
            return await fetch()
        except httpx.HTTPStatusError as error:
            decision = decide_retry(
                attempt,
                max_attempts,
                status_code=error.response.status_code,
                retry_after=_retry_after(error.response.headers.get("Retry-After")),
            )
            if not decision.retry:
                raise
        except httpx.RequestError:
            decision = decide_retry(attempt, max_attempts, transient_error=True)
            if not decision.retry:
                raise
        await sleep(decision.delay_seconds)
    raise RuntimeError("retry loop ended unexpectedly")


def _retry_after(value: str | None) -> int | None:
    if value is None:
        return None
    try:
        return max(0, int(value))
    except ValueError:
        return None
