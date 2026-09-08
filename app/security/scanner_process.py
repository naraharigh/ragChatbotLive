"""Run one security model per child process; never retain models in the API."""

import json
import re
import subprocess
import sys
from pathlib import Path

from fastapi import HTTPException
from loguru import logger

from app.config import settings


def run_scanners(stage: str, text: str) -> dict:
    names = {
        "input": ["PromptInjection", "Toxicity", "BanTopics", "TokenLimit"],
        "moderation": ["Toxicity", "BanTopics"],
        "pii": ["Sensitive"],
    }[stage]
    scores = {}
    for name in names:
        payload = {
            "stage": stage, "name": name, "text": text,
            "injection_threshold": settings.prompt_injection_threshold,
            "toxicity_threshold": settings.toxicity_threshold,
            "output_threshold": settings.output_toxicity_threshold,
        }
        logger.info("Starting isolated scanner stage={} scanner={}", stage, name)
        returncode = None
        worker_error = "unknown"
        try:
            result = subprocess.run(
                [sys.executable, "-m", "app.security.scanner_worker"],
                input=json.dumps(payload), text=True, capture_output=True,
                cwd=Path(__file__).resolve().parents[2], timeout=300,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
            returncode = result.returncode
            if returncode:
                # Only accept a class name from our worker's structured marker.
                match = re.search(r"^SCANNER_ERROR:([A-Za-z][A-Za-z0-9_]{0,99})$", result.stderr, re.MULTILINE)
                if match:
                    worker_error = match.group(1)
                raise RuntimeError("Scanner process failed")
            output = json.loads(result.stdout)
            text = output["sanitized"]
            valid = output["valid"]
            if not isinstance(text, str) or not isinstance(valid, bool):
                raise ValueError("Invalid scanner response")
            scores[name] = output["score"]
        except (OSError, subprocess.TimeoutExpired, ValueError, KeyError, TypeError, RuntimeError) as exc:
            # Scanner logs can contain private request text. Do not echo them.
            logger.error(
                "Isolated scanner failed stage={} scanner={} error={} exit_code={} worker_error={}",
                stage, name, type(exc).__name__, returncode, worker_error,
            )
            raise HTTPException(503, "Security scanning unavailable. Please retry later.") from None
        logger.info("Finished isolated scanner stage={} scanner={}", stage, name)
        if not valid and stage != "pii":
            return {"is_safe": False, "sanitized": text, "failed_checks": [name], "scores": scores}
    return {"is_safe": True, "sanitized": text, "failed_checks": [], "scores": scores}
