"""Private stdin/stdout protocol for a single short-lived scanner."""

import contextlib
import json
import sys


def main() -> None:
    request = json.load(sys.stdin)
    # Reserve stdout for the JSON result, including during library imports.
    with contextlib.redirect_stdout(sys.stderr):
        import llm_guard.input_scanners as inputs
        import llm_guard.output_scanners as outputs

        stage, name = request["stage"], request["name"]
        module = inputs if stage == "input" else outputs
        if name == "PromptInjection":
            scanner = inputs.PromptInjection(threshold=request["injection_threshold"])
        elif name == "Toxicity":
            threshold = request["toxicity_threshold"] if stage == "input" else request["output_threshold"]
            scanner = module.Toxicity(threshold=threshold)
        elif name == "BanTopics":
            scanner = module.BanTopics(
                topics=["violence", "self-harm", "illegal activities"],
                threshold=request["toxicity_threshold"] if stage == "input" else 0.9,
            )
        elif name == "TokenLimit":
            scanner = inputs.TokenLimit(limit=4096)
        elif name == "Sensitive":
            scanner = outputs.Sensitive(redact=True, threshold=request["output_threshold"])
        else:
            raise ValueError("Unknown scanner")
        args = (request["text"],) if stage == "input" else ("", request["text"])
        sanitized, valid, score = scanner.scan(*args)
    json.dump({"sanitized": str(sanitized), "valid": bool(valid), "score": float(score)}, sys.stdout)


if __name__ == "__main__":
    main()
