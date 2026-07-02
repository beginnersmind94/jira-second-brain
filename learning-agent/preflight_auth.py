"""ANC booth pre-flight: verify the Claude login works BEFORE opening the booth.

The single most common demo-day failure here is an expired Claude Code OAuth login,
which surfaces mid-generation as a 401 (or the misleading "Claude Code not found" /
"error result: success"). This probes it cheaply up front so the operator can run
`claude login` before a customer is standing there.

Exit codes: 0 = login valid · 1 = login expired/invalid · 2 = claude CLI missing ·
3 = probe timed out. Non-zero prints a clear remedy line.
"""
import shutil
import subprocess
import sys


def main() -> int:
    claude = shutil.which("claude")
    if not claude:
        print("PREFLIGHT FAIL: 'claude' CLI not found on PATH. Install Claude Code and run `claude login`.")
        return 2
    try:
        r = subprocess.run(
            [claude, "-p", "Reply with exactly: AUTH_OK"],
            capture_output=True, text=True, timeout=60,
        )
    except subprocess.TimeoutExpired:
        print("PREFLIGHT FAIL: auth probe timed out (network down?). Check connectivity, then retry.")
        return 3
    blob = (r.stdout or "") + (r.stderr or "")
    if r.returncode == 0 and "AUTH_OK" in blob:
        print("PREFLIGHT OK: Claude login is valid — live generation is good to go.")
        return 0
    if "401" in blob or "authenticate" in blob.lower() or "credential" in blob.lower():
        print("PREFLIGHT FAIL: Claude login expired/invalid.  Fix it now:  claude login")
        return 1
    print(f"PREFLIGHT FAIL: unexpected probe result (rc={r.returncode}). Output:\n{blob.strip()[:300]}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
