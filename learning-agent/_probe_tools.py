"""Diagnostic: ask the agent 'what tools do you have?' and dump everything verbosely."""
import asyncio
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from claude_agent_sdk import (
    AssistantMessage,
    ResultMessage,
    SystemMessage,
    TextBlock,
    ToolUseBlock,
    UserMessage,
    query,
)

from agent_sdk import options


async def main():
    print("=== probing available tools ===")
    print(f"setting_sources: {options.setting_sources}")
    print(f"mcp_servers keys: {list(options.mcp_servers.keys()) if isinstance(options.mcp_servers, dict) else options.mcp_servers}")
    print()

    async for message in query(
        prompt="List EVERY tool you currently have access to, grouped by source. Just dump tool names — don't call any. Do not include reasoning, just the list.",
        options=options,
    ):
        cls = type(message).__name__
        if isinstance(message, SystemMessage):
            sub = getattr(message, "subtype", "?")
            data = getattr(message, "data", None)
            print(f"[system/{sub}]")
            if data:
                if isinstance(data, dict):
                    for k, v in data.items():
                        if k == "tools" and isinstance(v, list):
                            print(f"  tools ({len(v)}):")
                            for t in v:
                                print(f"    - {t}")
                        elif k == "mcp_servers" and isinstance(v, list):
                            print(f"  mcp_servers ({len(v)}):")
                            for s in v:
                                print(f"    - {s}")
                        else:
                            sv = str(v)
                            if len(sv) > 200:
                                sv = sv[:200] + "…"
                            print(f"  {k}: {sv}")
                else:
                    print(f"  data: {str(data)[:400]}")
        elif isinstance(message, AssistantMessage):
            for block in (message.content or []):
                if isinstance(block, TextBlock):
                    print(f"[assistant.text]\n{block.text}")
                elif isinstance(block, ToolUseBlock):
                    print(f"[assistant.tool_call] {block.name}")
        elif isinstance(message, ResultMessage):
            print(f"[result] cost=${getattr(message, 'total_cost_usd', 0):.4f} turns={getattr(message, 'num_turns', '?')}")


if __name__ == "__main__":
    asyncio.run(main())
