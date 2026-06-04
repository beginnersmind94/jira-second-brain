"""LangGraph agent: PDF in, decides whether to verify against Jira, 5 key points out.

Follows Chapter 6 of Learning LangChain — the basic Plan-Do loop:
  START -> model -> tools_condition -> {tools -> model | END}
"""
from typing import Annotated, TypedDict

from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from tools import tools

load_dotenv()

SYSTEM_PROMPT = """You are an analyst that reads PDFs and identifies the 5 most important points.

You have access to two tools:
- read_pdf: extract the text of a PDF file
- search_jira: search a Jira ticket database for tickets that confirm a claim

Your workflow:
1. Call read_pdf first to see the document.
2. As you identify candidate key points, call search_jira on the specific
   feature names or workflow steps to verify them. You may call it multiple
   times for different claims.
3. When you have enough evidence, return exactly 5 key points. For each point,
   include a citation status:
     [VERIFIED: NXT-1234] — Jira confirmed this
     [UNVERIFIED]        — no matching ticket found
     [NOT CHECKED]       — you chose not to verify (briefly say why)

Be honest about citation status. Inventing a ticket key is worse than
admitting a claim is unverified.
"""


class State(TypedDict):
    messages: Annotated[list, add_messages]


model = ChatAnthropic(
    model="claude-sonnet-4-6",
    temperature=0.1,
    max_tokens=4096,
).bind_tools(tools)


def model_node(state: State) -> dict:
    response = model.invoke(state["messages"])
    return {"messages": [response]}


def _build_graph():
    builder = StateGraph(State)
    builder.add_node("model", model_node)
    builder.add_node("tools", ToolNode(tools))
    builder.add_edge(START, "model")
    builder.add_conditional_edges("model", tools_condition)
    builder.add_edge("tools", "model")
    return builder.compile()


graph = _build_graph()


def run_agent(pdf_path: str) -> str:
    """Invoke the agent end-to-end and return the final assistant message."""
    initial = {
        "messages": [
            SystemMessage(SYSTEM_PROMPT),
            HumanMessage(
                f"Read the PDF at {pdf_path} and produce the 5 most important "
                f"key points. Verify each against Jira where you can."
            ),
        ]
    }
    final = graph.invoke(initial)
    return final["messages"][-1].content
