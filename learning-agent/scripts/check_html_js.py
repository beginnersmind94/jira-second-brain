#!/usr/bin/env python3
"""
Parse-check the inline <script> block in static/index.html using Node.js.

Exit 0 = PARSE OK
Exit 1 = syntax error found (prints exact line + token)
Exit 2 = node not found or script block not found

Usage:
    python scripts/check_html_js.py              # checks static/index.html
    python scripts/check_html_js.py path/to.html  # checks any HTML file
"""
import re, subprocess, sys, tempfile, os

def main():
    html_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(__file__), '..', 'static', 'index.html'
    )
    html_path = os.path.abspath(html_path)

    if not os.path.exists(html_path):
        print(f"ERROR: file not found: {html_path}", file=sys.stderr)
        sys.exit(2)

    with open(html_path, encoding='utf-8') as f:
        html = f.read()

    # Extract all inline <script> blocks (no src= attribute)
    blocks = re.findall(r'<script(?![^>]*\bsrc\b)[^>]*>(.*?)</script>', html, re.DOTALL)
    if not blocks:
        print("ERROR: no inline <script> block found", file=sys.stderr)
        sys.exit(2)

    # Find node
    node = None
    for candidate in ['node', 'node.exe']:
        try:
            r = subprocess.run([candidate, '--version'], capture_output=True, timeout=5)
            if r.returncode == 0:
                node = candidate
                break
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

    if not node:
        print("WARNING: node not found — skipping JS parse check", file=sys.stderr)
        print("Install Node.js to enable this check: https://nodejs.org/")
        sys.exit(0)  # Non-fatal if node isn't installed

    errors = []
    for i, block in enumerate(blocks):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js',
                                         delete=False, encoding='utf-8') as tmp:
            tmp.write(block)
            tmp_path = tmp.name
        try:
            result = subprocess.run(
                [node, '--check', tmp_path],
                capture_output=True, text=True, timeout=15
            )
            if result.returncode != 0:
                # Node reports line numbers relative to the temp file.
                # Map them back to the HTML file for a useful error message.
                err = result.stderr.strip()
                # Find where this block starts in the HTML so we can offset line numbers
                block_start_line = html[:html.index(block)].count('\n') + 1
                # Adjust line numbers in node's error output
                def adjust_line(m):
                    rel = int(m.group(1))
                    return f'line {block_start_line + rel - 1}'
                err_mapped = re.sub(r'(?<!\w)(\d+)(?=:\d+\))', adjust_line, err)
                # Clean up temp file path in the message
                err_mapped = err_mapped.replace(tmp_path, html_path)
                errors.append(f"Script block {i+1}:\n{err_mapped}")
        finally:
            os.unlink(tmp_path)

    if errors:
        print(f"\n{'='*60}", file=sys.stderr)
        print("JS PARSE ERROR — commit blocked", file=sys.stderr)
        print(f"{'='*60}", file=sys.stderr)
        for e in errors:
            print(e, file=sys.stderr)
        print(f"{'='*60}\n", file=sys.stderr)
        print("Fix the syntax error above, then retry.", file=sys.stderr)
        sys.exit(1)

    block_sizes = [len(b) for b in blocks]
    print(f"PARSE OK — {len(blocks)} script block(s), "
          f"{sum(block_sizes):,} chars, node {node}")
    sys.exit(0)

if __name__ == '__main__':
    main()
