from claude_agent_sdk import ClaudeAgentOptions
import inspect

sig = inspect.signature(ClaudeAgentOptions)
print("--- ClaudeAgentOptions parameters ---")
for name, p in sig.parameters.items():
    ann = p.annotation if p.annotation is not inspect.Parameter.empty else "any"
    print(f"  {name}: {ann}")

print()
print("--- docstring (first 2000 chars) ---")
doc = ClaudeAgentOptions.__doc__ or ""
print(doc[:2000])
