"""Live smoke test for the Anthropic Citations API (Version B only).

Prints SKIP and exits 0 when ANTHROPIC_API_KEY is unset, so it never breaks
Version A or CI. With a key, it sends one citation-enabled document and asserts
the response carries a verbatim cited_text tagged with our document title.

No temperature/top_p: those are rejected with a 400 on Opus 4.8/4.7/Fable 5, so
omitting them keeps CITATIONS_MODEL free to point at any current model.
"""
import os
import sys


def main() -> int:
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("SKIP: no ANTHROPIC_API_KEY")
        return 0
    from anthropic import Anthropic

    client = Anthropic()
    model = os.getenv("CITATIONS_MODEL", "claude-sonnet-4-6")
    resp = client.messages.create(
        model=model,
        max_tokens=512,
        messages=[{"role": "user", "content": [
            {"type": "document",
             "source": {"type": "text", "media_type": "text/plain",
                        "data": "The cashier must confirm the student PIN before serving a meal."},
             "title": "NXT-TEST:AC",
             "citations": {"enabled": True}},
            {"type": "text",
             "text": "In one sentence, state what the cashier must do, and cite the source."},
        ]}],
    )
    cited = []
    for block in resp.content:
        if getattr(block, "type", None) == "text":
            for c in (getattr(block, "citations", None) or []):
                cited.append((getattr(c, "document_title", ""), getattr(c, "cited_text", "")))
    print("citations:", cited)
    ok = any(t == "NXT-TEST:AC" and (s or "").strip() for t, s in cited)
    print("PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
