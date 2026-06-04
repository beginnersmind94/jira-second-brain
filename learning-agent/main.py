"""Stream a run of the agent against a sample PDF.

Usage:
    python main.py                      # uses the default Eligibility PDF
    python main.py path\\to\\file.pdf    # custom PDF
"""
import os
import sys

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage

from agent import SYSTEM_PROMPT, graph

load_dotenv()

DEFAULT_PDF = (
    r"C:\Users\rahul.mehta\Downloads\Financials-Documentation-KT"
    r"\jira-brain\raw\guides\pdf\SC\Eligibility\Quick-Guide"
    r"\GUIDE-039-add-income-surveys-quick-guide.pdf"
)


def fmt_message(msg):
    if isinstance(msg, AIMessage):
        parts = []
        if msg.content:
            parts.append(f"  text: {msg.content[:600]}")
        for tc in (msg.tool_calls or []):
            parts.append(f"  tool_call: {tc['name']}({tc['args']})")
        return "\n".join(parts) or "  (empty AI message)"
    if isinstance(msg, ToolMessage):
        snippet = (msg.content or "")[:400].replace("\n", " ")
        return f"  tool_result ({msg.name}): {snippet}"
    return f"  {type(msg).__name__}: {str(msg)[:300]}"


def main():
    if not os.getenv("ANTHROPIC_API_KEY") or os.getenv("ANTHROPIC_API_KEY") == "your-key-here":
        print("ERROR: set ANTHROPIC_API_KEY in .env before running.")
        sys.exit(1)

    pdf_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PDF
    print(f"PDF: {pdf_path}\n")

    initial = {
        "messages": [
            SystemMessage(SYSTEM_PROMPT),
            HumanMessage(
                f"Read the PDF at {pdf_path} and produce the 5 most important "
                f"key points. Verify each against Jira where you can."
            ),
        ]
    }

    final_state = None
    for chunk in graph.stream(initial, stream_mode="updates"):
        for node, update in chunk.items():
            print(f"=== {node} ===")
            for msg in update.get("messages", []):
                print(fmt_message(msg))
            print()
        final_state = chunk

    print("=" * 60)
    print("FINAL OUTPUT")
    print("=" * 60)
    if final_state:
        for _, update in final_state.items():
            for msg in update.get("messages", []):
                if isinstance(msg, AIMessage) and msg.content:
                    print(msg.content)


if __name__ == "__main__":
    main()
