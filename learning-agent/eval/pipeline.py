"""Eval pipeline runner — re-sequences demo_d's run_cell_d STAGES in-memory.

This module RETURNS the generated artifacts and writes NO files. It reuses every
pipeline stage from demo_d verbatim (plan -> registry -> parallel section writers
-> deterministic assemble -> strict validator). It does NOT reimplement any stage.

The caller is responsible for setting demo._FIX (via demo._load_fixture(module))
once before invoking run_pipeline; build_registry / write_section / assemble /
validate_citations all read demo._FIX as the ground-truth registry source.
"""
import asyncio
import time

from claude_agent_sdk import ClaudeAgentOptions

import demo
import demo_d
import pricing


async def run_pipeline(module: str, transcript_path: str, fmt: str) -> dict:
    """Run the cell-D pipeline for one (module, transcript, fmt) and return artifacts.

    Mirrors demo_d.run_cell_d's stage sequence exactly, but returns the artifacts
    instead of persisting drafts / printing telemetry. Assumes demo._FIX is set.
    """
    t0 = time.monotonic()

    # ── Stage 1: Plan (research with tools, emit section plan) ──
    # plan_opts is built EXACTLY as run_cell_d builds it.
    plan_opts = ClaudeAgentOptions(
        model="claude-sonnet-4-6", effort="medium",
        system_prompt=demo_d.plan_system_prompt(module, fmt),
        mcp_servers={demo.MCP_SERVER_NAME: demo.demo_mcp_server},
        allowed_tools=demo.ALLOWED_TOOLS, disallowed_tools=demo_d._DISALLOWED,
        tools=[], max_turns=20,
    )
    plan_prompt = (
        f"Plan a {fmt} `{module}` guide from the transcript at:\n  {transcript_path}\n"
        f"Call parse_transcript first (module=\"{module}\"). Emit ONLY the JSON section plan."
    )
    pr = await demo_d._run(plan_prompt, plan_opts)
    plan = demo_d._parse_json(pr["text"])
    if not plan or not plan.get("sections"):
        raise RuntimeError(f"PLAN FAILED to parse. Raw head:\n{pr['text'][:800]}")
    sections_plan = plan["sections"]
    plan_secs = pr["secs"]

    # ── Stage 2: build registry from the planned ticket keys ──
    all_keys = [k for s in sections_plan for k in s.get("ticket_keys", [])]
    registry, by_ticket = demo_d.build_registry(all_keys)

    # ── Stage 3: parallel section writers (CITE-IDs only) ──
    budget = demo_d._FORMAT_BUDGET[fmt]
    sem = asyncio.Semaphore(demo_d.SECTION_CONCURRENCY)
    sec_t0 = time.monotonic()
    sections = await asyncio.gather(*(
        demo_d.write_section(s, registry, by_ticket, module, sem, budget=budget)
        for s in sections_plan
    ))
    sec_secs = time.monotonic() - sec_t0

    # ── Stage 4: deterministic assemble + render, then strict validation ──
    html, asm = demo_d.assemble(module, sections, registry)
    integ = demo.validate_citations(html)

    total_secs = time.monotonic() - t0

    # Cost of the whole run = plan call + every section call.
    usages = [pr.get("usage")] + [s.get("usage") for s in sections]
    cost = pricing.cost_of(usages)

    return {
        "html": html,
        "sections": sections,
        "asm": asm,
        "integ": integ,
        "words": demo._words(html),
        "plan_secs": float(plan_secs),
        "sec_secs": float(sec_secs),
        "total_secs": float(total_secs),
        "fmt": fmt,
        "cost": cost,
    }
