with open(r'C:\Users\rahul.mehta\Downloads\Financials-Documentation-KT\jira-brain\learning-agent\demo_app.py', encoding='utf-8') as f:
    src = f.read()
checks = [
    ('import completion_store as _cs', 'import completion_store'),
    ('from auth import CurrentUser, get_current_user', 'import auth'),
    ('@app.post("/api/tracks/{tid}/progress")', 'POST /api/tracks/{tid}/progress route'),
    ('_cs.get_progress(', 'get_progress call in api_get_track'),
    ('_cs.issue_certificate(', 'issue_certificate call in POST /api/certificates'),
    ('_cs.get_certificate(', 'get_certificate call in GET /api/certificates/{cid}'),
    ('_cs.set_module_done(', 'set_module_done call in api_mark_module_done'),
]
all_ok = True
for pattern, label in checks:
    if pattern in src:
        print(f'  OK: {label}')
    else:
        print(f'  MISSING: {label}')
        all_ok = False
if all_ok:
    print('All checks passed')
else:
    raise SystemExit(1)
