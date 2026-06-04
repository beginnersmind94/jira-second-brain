"""Inspect the SDK's remote MCP server config types."""
from claude_agent_sdk.types import (
    McpHttpServerConfig,
    McpSSEServerConfig,
    McpStdioServerConfig,
)

for cls in (McpStdioServerConfig, McpSSEServerConfig, McpHttpServerConfig):
    print(f"=== {cls.__name__} ===")
    print(f"  type field: {getattr(cls, '__annotations__', {})}")
    print(f"  doc: {(cls.__doc__ or '').strip()[:300]}")
    print()
