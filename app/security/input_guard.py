"""Input security scanning in isolated processes."""
from app.security.scanner_process import run_scanners


def scan_input(text: str) -> dict:
    return run_scanners("input", text)


def check_input_safe(text: str) -> tuple[bool, str | None]:
    result = scan_input(text)
    return result["is_safe"], ", ".join(result["failed_checks"]) or None
