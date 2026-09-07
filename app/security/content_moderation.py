"""Output moderation and PII redaction in isolated processes."""
from app.security.scanner_process import run_scanners


def redact_pii(text: str) -> str:
    return run_scanners("pii", text)["sanitized"]


def moderate_output(text: str) -> tuple[bool, str | None]:
    result = run_scanners("moderation", text)
    return result["is_safe"], ", ".join(result["failed_checks"]) or None


def moderate_and_redact(text: str) -> tuple[bool, str, str | None]:
    allowed, reason = moderate_output(text)
    return allowed, redact_pii(text) if allowed else "", reason
