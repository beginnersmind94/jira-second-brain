"""Eval suite for the Learning Content Producer.

Design: eval/EVAL-SPEC.md (from the design-eval-suite workflow, grounded in
Anthropic's "Demystifying evals for agents" + our measured failures).

The deterministic regression suite (eval/regression.py) is the 80/20: it runs
with ZERO SDK calls against the real grading functions (validate_citations,
enforce_citations, assemble, build_registry) and pins every historical failure.
Run it on every pipeline change:
    python -m eval.regression
"""
import sys
from pathlib import Path

# Ensure `import demo, demo_d` works regardless of cwd.
_APP_DIR = Path(__file__).resolve().parent.parent
if str(_APP_DIR) not in sys.path:
    sys.path.insert(0, str(_APP_DIR))
