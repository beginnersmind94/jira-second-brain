"""SDK enforcement layer for question-bank curation.

The gate is enforced by the SDK runtime, not by prompt text:
  • commit_to_bank is a custom MCP tool — the ONLY tool that writes to the bank.
  • commit_gate_hook is a PreToolUse hook that DENIES the call unless the item's status
    is auto_approved or human_approved. This is the hard layer: it fires even if the model
    calls the tool directly, and regardless of permission mode.
  • make_human_callback builds a canUseTool callback that surfaces needs_human items to a
    human approver at runtime; approve → human_approved, deny → rejected.

Design note on `allowed_tools`: commit_to_bank IS listed so the agent can call it for
already-approved items, but the allowlist is NOT the security boundary — the PreToolUse
hook is. Status, not allow-listing, decides whether a write happens.
"""
from __future__ import annotations

import json

from claude_agent_sdk import (
    ClaudeAgentOptions, HookMatcher, PermissionResultAllow, PermissionResultDeny,
    create_sdk_mcp_server, tool,
)

import qbank_curation as core
from qbank_curation import COMMITTABLE, NEEDS_HUMAN, Stores

MCP = "qbank"
COMMIT_TOOL = f"mcp__{MCP}__commit_to_bank"

_STORES: Stores | None = None
_HUMAN_DECIDER = None   # callable(item) -> (approve: bool, reason: str)


def configure(stores: Stores, human_decider=None) -> None:
    """Wire the module to a store + (optionally) a human decision function."""
    global _STORES, _HUMAN_DECIDER
    _STORES = stores
    _HUMAN_DECIDER = human_decider


# ── The gated write tool (registered with the agent; gated by the hook) ────────
@tool("commit_to_bank", "Write an APPROVED question to the question bank.", {"item_id": str})
async def commit_to_bank_tool(args):
    result = core.commit_to_bank(_STORES, args["item_id"])   # deterministic guard (defense in depth)
    return {"content": [{"type": "text", "text": json.dumps(result)}]}


# ── PreToolUse hook — the HARD gate ────────────────────────────────────────────
async def commit_gate_hook(input, tool_use_id, context):
    """Deny commit_to_bank unless the item's status is committable. Independent of the
    model, the prompt, and the permission mode."""
    tool_name = (input or {}).get("tool_name", "")
    if "commit_to_bank" not in tool_name:
        return {}  # not our tool — no opinion
    item_id = ((input or {}).get("tool_input") or {}).get("item_id")
    item = (_STORES.load_pending().get(item_id) if (_STORES and item_id) else None)
    status = item.get("status") if item else None
    if status in COMMITTABLE:
        return {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "allow"}}
    reason = (f"GATE DENIED: cannot commit '{item_id}' — status '{status}' is not "
              f"{' or '.join(COMMITTABLE)}. No question reaches the bank without passing the gate.")
    if _STORES:
        _STORES.audit_log("hook_denied_commit", item_id or "?", reason=reason, rule="PreToolUse")
    return {"hookSpecificOutput": {"hookEventName": "PreToolUse",
                                   "permissionDecision": "deny", "permissionDecisionReason": reason}}


# ── canUseTool human approval callback ─────────────────────────────────────────
def make_human_callback(stores: Stores, decider):
    """Return a canUseTool callback. When the agent tries to commit a needs_human item,
    surface it to `decider(item) -> (approve, reason)`; approve promotes to human_approved
    (so the hook will then allow), deny sets rejected. Auto/human-approved pass through;
    anything else is denied."""
    async def can_use_tool(tool_name, tool_input, context):
        if "commit_to_bank" not in tool_name:
            return PermissionResultAllow()  # other tools governed by allowed_tools + dontAsk
        item_id = (tool_input or {}).get("item_id")
        item = stores.load_pending().get(item_id) if item_id else None
        status = item.get("status") if item else None
        if status in COMMITTABLE:
            return PermissionResultAllow()
        if status == NEEDS_HUMAN:
            approve, reason = decider(item)
            new = core.human_decide(stores, item_id, approve, by="human_callback", reason=reason)
            return PermissionResultAllow() if new in COMMITTABLE else \
                PermissionResultDeny(message=f"human rejected: {reason}")
        return PermissionResultDeny(message=f"status '{status}' cannot be committed")
    return can_use_tool


# ── Options builder ────────────────────────────────────────────────────────────
def build_curation_options(stores: Stores, decider, extra_tools=None) -> ClaudeAgentOptions:
    configure(stores, decider)
    server = create_sdk_mcp_server(name=MCP, version="1.0.0", tools=[commit_to_bank_tool])
    return ClaudeAgentOptions(
        model="claude-sonnet-4-6",
        permission_mode="dontAsk",                       # anything unexpected is denied, not run
        mcp_servers={MCP: server},
        allowed_tools=["Read", "AskUserQuestion", COMMIT_TOOL] + list(extra_tools or []),
        can_use_tool=make_human_callback(stores, decider),
        hooks={"PreToolUse": [HookMatcher(matcher="commit_to_bank", hooks=[commit_gate_hook])]},
    )
