"""Bound query concurrency and report Linux process memory without model imports."""

from functools import wraps
from pathlib import Path
from threading import Lock

from fastapi import HTTPException
from loguru import logger

_query_lock = Lock()


def log_memory(stage: str) -> None:
    try:
        lines = Path("/proc/self/status").read_text().splitlines()
        memory = {
            line.split(":", 1)[0]: line.split(":", 1)[1].strip()
            for line in lines if line.startswith(("VmRSS:", "VmHWM:"))
        }
        logger.info("Query memory stage={} {}", stage, memory)
    except OSError:
        logger.debug("Process memory metrics unavailable on this platform")


def single_query(function):
    @wraps(function)
    def wrapped(*args, **kwargs):
        if not _query_lock.acquire(blocking=False):
            raise HTTPException(
                status_code=429,
                detail="Another query is running. Please retry shortly.",
                headers={"Retry-After": "5"},
            )
        try:
            log_memory("start")
            return function(*args, **kwargs)
        finally:
            try:
                log_memory("finish")
            finally:
                _query_lock.release()
    return wrapped
