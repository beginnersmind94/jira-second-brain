from pathlib import Path
p = Path(r'C:\Users\rahul.mehta\Downloads\Financials-Documentation-KT\jira-brain\learning-agent\tests\test_completion_store.py')
print("parent:", p.parent)
print("parent.parent:", p.parent.parent)
import sys
sys.path.insert(0, str(p.parent.parent))
import completion_store as cs
print("completion_store found:", cs.__file__)
