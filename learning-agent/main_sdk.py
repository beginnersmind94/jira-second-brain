"""Run the Claude Agent SDK version, streaming each message as it arrives.

Usage:
    python main_sdk.py                     # default Eligibility PDF
    python main_sdk.py path\\to\\file.pdf   # custom PDF
"""
import asyncio
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from dotenv import load_dotenv

load_dotenv()

from claude_agent_sdk import (
    AssistantMessage,
    ResultMessage,
    SystemMessage,
    TextBlock,
    ToolResultBlock,
    ToolUseBlock,
    UserMessage,
    query,
)

from agent_sdk import options

DEFAULT_PDF = (
    r"C:\Users\rahul.mehta\Downloads\Financials-Documentation-KT"
    r"\jira-brain\raw\guides\pdf\SC\Eligibility\Quick-Guide"
    r"\GUIDE-039-add-income-surveys-quick-guide.pdf"
)


def render(message):
    label = type(message).__name__
    if isinstance(message, SystemMessage):
        return f"[system] subtype={getattr(message, 'subtype', '?')}"
    if isinstance(message, AssistantMessage):
        lines = [f"[assistant]"]
        for block in (message.content or []):
            if isinstance(block, TextBlock):
                lines.append(f"  text: {block.text[:600]}")
            elif isinstance(block, ToolUseBlock):
                lines.append(f"  tool_call: {block.name}({block.input})")
            else:
                lines.append(f"  {type(block).__name__}: {block}")
        return "\n".join(lines)
    if isinstance(message, UserMessage):
        lines = [f"[user/tool_result]"]
        for block in (message.content or []):
            if isinstance(block, ToolResultBlock):
                content = block.content
                if isinstance(content, list):
                    snippet = " ".join(
                        c.get("text", "") if isinstance(c, dict) else str(c)
                        for c in content
                    )
                else:
                    snippet = str(content)
                lines.append(f"  tool_result: {snippet[:400]}")
            elif isinstance(block, TextBlock):
                lines.append(f"  text: {block.text[:300]}")
            else:
                lines.append(f"  {type(block).__name__}")
        return "\n".join(lines)
    if isinstance(message, ResultMessage):
        return (
            f"[result] cost_usd={getattr(message, 'total_cost_usd', '?')} "
            f"turns={getattr(message, 'num_turns', '?')}"
        )
    return f"[{label}]"


async def run(pdf_path: str):
    prompt = (
        f"Read the PDF at the following path and produce the 5 most "
        f"important key points. Verify each against Jira where you can.\n\n"
        f"PDF path: {pdf_path}"
    )
    final_text = []
    async for message in query(prompt=prompt, options=options):
        print(render(message))
        print()
        if isinstance(message, AssistantMessage):
            for block in (message.content or []):
                if isinstance(block, TextBlock):
                    final_text.append(block.text)

    print("=" * 60)
    print("FINAL OUTPUT")
    print("=" * 60)
    print("\n".join(final_text))


def main():
    pdf_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PDF
    print(f"PDF: {pdf_path}\n")
    asyncio.run(run(pdf_path))


if __name__ == "__main__":
    main()
