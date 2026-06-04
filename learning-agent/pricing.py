"""Token pricing → cost-per-run. Rates (USD per MTok) from claude.com/pricing.

We run claude-sonnet-4-6. cache_write uses the 5-minute write rate (the SDK's
default ephemeral cache). cost_of() sums a list of per-call usage dicts (each the
raw usage from a ResultMessage) so a whole multi-call pipeline run gets one cost.
"""
_PER_MTOK = {
    "claude-sonnet-4-6": {"input": 3.0, "output": 15.0, "cache_read": 0.30, "cache_write": 3.75},
    "claude-opus-4-8":   {"input": 5.0, "output": 25.0, "cache_read": 0.50, "cache_write": 6.25},
    "claude-haiku-4-5":  {"input": 1.0, "output": 5.0,  "cache_read": 0.10, "cache_write": 1.25},
}
DEFAULT_MODEL = "claude-sonnet-4-6"


def cost_of(usages, model: str = DEFAULT_MODEL) -> dict:
    """usages: iterable of usage dicts (or None). Returns cost + token totals."""
    rates = _PER_MTOK.get(model, _PER_MTOK[DEFAULT_MODEL])
    tot = {"input": 0, "output": 0, "cache_read": 0, "cache_write": 0}
    for u in usages:
        if not u:
            continue
        tot["input"] += int(u.get("input_tokens") or 0)
        tot["output"] += int(u.get("output_tokens") or 0)
        tot["cache_read"] += int(u.get("cache_read_input_tokens") or 0)
        tot["cache_write"] += int(u.get("cache_creation_input_tokens") or 0)
    cost = (tot["input"] * rates["input"] + tot["output"] * rates["output"]
            + tot["cache_read"] * rates["cache_read"] + tot["cache_write"] * rates["cache_write"]) / 1_000_000
    return {
        "model": model, "cost_usd": round(cost, 4),
        "input_tokens": tot["input"], "output_tokens": tot["output"],
        "cache_read_tokens": tot["cache_read"], "cache_write_tokens": tot["cache_write"],
        "total_tokens": sum(tot.values()),
    }
