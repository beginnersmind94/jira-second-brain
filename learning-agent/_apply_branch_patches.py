path = r'C:/Users/rahul.mehta/Downloads/Financials-Documentation-KT/jira-brain/learning-agent/demo_app.py'
with open(path, encoding='utf-8') as f:
    src = f.read()

changes = []

# PATCH 1: Add Depends, Request if missing
if 'Body, Depends, FastAPI' not in src:
    src = src.replace(
        'from fastapi import Body, FastAPI, HTTPException, Query',
        'from fastapi import Body, Depends, FastAPI, HTTPException, Query, Request',
        1
    )
    changes.append('Add Depends+Request to fastapi import')

# PATCH 2: Add completion_store + auth imports after roster_sync
if 'import completion_store as _cs' not in src:
    anchor = 'from roster_sync import RosterSyncClient\n'
    # Find the next non-blank line after anchor
    idx = src.find(anchor)
    if idx >= 0:
        insert_pos = idx + len(anchor)
        insertion = ('# Identity resolution — demo stub; Task 11 (SSO) replaces the stub body.\n'
                     'from auth import CurrentUser, get_current_user\n'
                     '# Durable per-learner completion records (disk-backed JSON, keyed by user_id).\n'
                     'import completion_store as _cs\n')
        src = src[:insert_pos] + insertion + src[insert_pos:]
        changes.append('Add auth + completion_store imports')
    else:
        print('ERROR: roster_sync anchor not found')
        raise SystemExit(1)

# PATCH 3: Wire api_get_track to include progress from store
if '_cs.get_progress(' not in src:
    old = (
        '@app.get("/api/tracks/{tid}")\n'
        'async def api_get_track(tid: str):\n'
        '    track = _ms.load_track(tid)\n'
        '    if not track:\n'
        '        raise HTTPException(404, "track not found")\n'
        '    # icn_dir so ICN_DOC modules expand inside a track (learner sees the mixed track).\n'
        '    return _ms.expand_track(track, icn_dir=_ICN_DIR)\n'
    )
    new = (
        '@app.get("/api/tracks/{tid}")\n'
        'async def api_get_track(\n'
        '    tid: str,\n'
        '    current_user: CurrentUser = Depends(get_current_user),\n'
        '):\n'
        '    track = _ms.load_track(tid)\n'
        '    if not track:\n'
        '        raise HTTPException(404, "track not found")\n'
        '    # icn_dir so ICN_DOC modules expand inside a track (learner sees the mixed track).\n'
        '    expanded = _ms.expand_track(track, icn_dir=_ICN_DIR)\n'
        '    # Attach durable per-user progress so the learner view reflects real completion.\n'
        '    module_ids = [m["id"] for m in (expanded.get("modules") or [])]\n'
        '    expanded["progress"] = _cs.get_progress(\n'
        '        current_user.id, tid, module_ids=module_ids\n'
        '    )\n'
        '    return expanded\n'
    )
    if old in src:
        src = src.replace(old, new, 1)
        changes.append('Wire api_get_track with progress')
    else:
        # Try alternate form that might already have CurrentUser but not _cs call
        print('api_get_track old form not found, checking for alternate form...')
        idx = src.find('@app.get("/api/tracks/{tid}")')
        print(repr(src[idx:idx+350]))

# PATCH 4: Wire the progress route body if it's a stub
if '@app.post("/api/tracks/{tid}/progress")' in src:
    # Find the function and check if it uses _cs.set_module_done
    idx = src.find('@app.post("/api/tracks/{tid}/progress")')
    end_idx = src.find('\n\n\n@app.', idx + 1)
    segment = src[idx:end_idx]
    if '_cs.set_module_done(' not in segment:
        # The route exists but doesn't use the store. Replace it.
        new_route = (
            '@app.post("/api/tracks/{tid}/progress")\n'
            'async def api_mark_module_done(\n'
            '    tid: str,\n'
            '    body: dict = Body(default={}),\n'
            '    current_user: CurrentUser = Depends(get_current_user),\n'
            '):\n'
            '    """Mark a module done for the authenticated learner.\n'
            '\n'
            '    Body: { "module_id": "<id>" }\n'
            '    Returns: updated progress dict {modules_done, pct, certified, cert_issued_at}.\n'
            '    """\n'
            '    module_id = (body.get("module_id") or "").strip()\n'
            '    if not module_id:\n'
            '        raise HTTPException(400, "module_id is required")\n'
            '    track = _ms.load_track(tid)\n'
            '    if not track:\n'
            '        raise HTTPException(404, "track not found")\n'
            '    module_ids = track.get("module_ids") or []\n'
            '    progress = _cs.set_module_done(\n'
            '        current_user.id, tid, module_id, module_ids=module_ids\n'
            '    )\n'
            '    return progress'
        )
        src = src[:idx] + new_route + src[end_idx:]
        changes.append('Wire api_mark_module_done with _cs.set_module_done')

# PATCH 5: Wire POST /api/certificates to use _cs.issue_certificate
if '_cs.issue_certificate(' not in src:
    start5 = src.find('@app.post("/api/certificates")')
    end5 = src.find('\n\n\n@app.', start5 + 1)
    if start5 < 0 or end5 < 0:
        print('ERROR: POST /api/certificates not found')
        raise SystemExit(1)
    new_cert_post = '''\
@app.post("/api/certificates")
async def issue_certificate(
    payload: dict = Body(default={}),
    current_user: CurrentUser = Depends(get_current_user),
):
    """Issue + persist a completion certificate for a track.

    Uses CompletionStore so certs survive server restarts and are keyed by
    user identity.  Falls back to the payload learner_name for backward
    compatibility with the demo UI (which passes learner_name directly).
    """
    track_id = (payload.get("track_id") or "").strip()
    if not track_id:
        raise HTTPException(400, "track_id is required")
    track = _ms.load_track(track_id)
    if not track:
        raise HTTPException(404, "track not found")
    # Resolve learner name: prefer user identity, fall back to payload.
    learner = (payload.get("learner_name") or "").strip() or current_user.name or "Demo Learner"
    cert = _cs.issue_certificate(
        current_user.id,
        track_id,
        learner,
        track_title=track.get("title") or track_id,
        product=track.get("product") or "Schoo\lCaf\xe9",
        role=(track.get("role_tags") or [None])[0],
        modules=len(track.get("module_ids") or []),
    )

    # Fire completion writeback to SchoolCafe / PrimeroEdge (non-fatal).
    learner_id = (payload.get("learner_id") or learner).strip()
    district_id = (payload.get("district_id") or current_user.district_id or "demo-district").strip()
    try:
        await roster_sync.sync_completion(district_id, learner_id, track_id, 100, certified=True)
    except Exception as exc:
        import logging
        logging.getLogger(__name__).warning(
            "cert sync_completion failed (non-fatal) learner=%s track=%s: %s",
            learner_id, track_id, exc,
        )

    return JSONResponse(cert)'''
    src = src[:start5] + new_cert_post + src[end5:]
    changes.append('Wire POST /api/certificates with _cs.issue_certificate')

# PATCH 6: Wire GET /api/certificates/{cid} to use _cs.get_certificate
if '_cs.get_certificate(' not in src:
    old_get_cert = (
        '@app.get("/api/certificates/{cid}")\n'
        'async def get_certificate(cid: str):\n'
        '    p = CERTS / f"{cid}.json"\n'
        '    if not p.exists():\n'
        '        raise HTTPException(404, "certificate not found")\n'
        '    return JSONResponse(json.loads(p.read_text(encoding="utf-8")))'
    )
    new_get_cert = (
        '@app.get("/api/certificates/{cid}")\n'
        'async def get_certificate(cid: str):\n'
        '    """Retrieve a certificate by id.\n'
        '\n'
        '    Checks CompletionStore first (durable, per-user). Falls back to the legacy\n'
        '    flat CERTS/ directory so previously issued certificates remain accessible.\n'
        '    """\n'
        '    cert = _cs.get_certificate(cid)\n'
        '    if cert is not None:\n'
        '        return JSONResponse(cert)\n'
        '    # Legacy fallback: certs issued before the store was wired.\n'
        '    p = CERTS / f"{cid}.json"\n'
        '    if p.exists():\n'
        '        return JSONResponse(json.loads(p.read_text(encoding="utf-8")))\n'
        '    raise HTTPException(404, "certificate not found")'
    )
    if old_get_cert in src:
        src = src.replace(old_get_cert, new_get_cert, 1)
        changes.append('Wire GET /api/certificates/{cid} with _cs.get_certificate')
    else:
        print('WARNING: GET cert old form not found')
        idx = src.find('@app.get("/api/certificates/{cid}")')
        print(repr(src[idx:idx+300]))

with open(path, 'w', encoding='utf-8') as f:
    f.write(src)

if changes:
    print('Applied patches:')
    for c in changes:
        print(f'  - {c}')
else:
    print('No patches needed (all already in place)')
