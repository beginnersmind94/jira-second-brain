/* ============================================================================
   Cashier Training Studio — standalone backend shim (Block A).
   Runs BEFORE the real app script. Overrides window.fetch so every /api, /resources,
   /intent and /course-img call is served from a baked SEED + a localStorage store.
   The SEED is REAL content captured from the live Learning Studio backend.
   Token __SEED__ is replaced by build_share.py with the seed JSON.
   ============================================================================ */
(function () {
  "use strict";
  var SEED = __SEED__;
  var LS = "cts_share_store_v2";

  function clone(o) { return JSON.parse(JSON.stringify(o)); }
  function loadStore() {
    try { var r = localStorage.getItem(LS); if (r) return JSON.parse(r); } catch (e) {}
    return clone(SEED.initialStore);
  }
  var store = loadStore();
  function persist() { try { localStorage.setItem(LS, JSON.stringify(store)); } catch (e) {} }
  window.__ctsStore = function () { return store; };
  window.__ctsReset = function () { store = clone(SEED.initialStore); persist(); location.reload(); };
  window.__ctsSeed = SEED;

  var realFetch = window.fetch ? window.fetch.bind(window) : null;
  function J(obj, status) {
    return new Response(JSON.stringify(obj == null ? {} : obj),
      { status: status || 200, headers: { "Content-Type": "application/json" } });
  }
  function HTML(html, status) {
    return new Response(html || "", { status: status || 200, headers: { "Content-Type": "text/html; charset=utf-8" } });
  }

  // ---- content accessors (SEED + store overlay) ----
  function allTracks() { return [SEED.track].concat(store.userTracks || []); }
  function findTrack(id) { return allTracks().filter(function (t) { return t.id === id; })[0]; }
  function allCourses() { return (SEED.courses || []).concat(store.userCourses || []); }
  function findCourse(id) { return allCourses().filter(function (c) { return c.id === id; })[0]; }
  function allQuizzes() { return (SEED.quizzes || []).concat(store.userQuizzes || []); }
  function findQuiz(id) { return allQuizzes().filter(function (q) { return q.id === id; })[0]; }
  function allAssessments() { return (SEED.assessments || []).concat(store.userAssessments || []); }
  function findAssessment(id) { return allAssessments().filter(function (a) { return a.id === id; })[0]; }

  function trackListItem(t) {
    var c = clone(t);
    delete c.courses; delete c.modules; delete c.progress;
    return c;
  }
  function expandTrack(t) {
    var tt = clone(t);
    tt.courses = (tt.course_ids || []).map(findCourse).filter(Boolean).map(clone);
    tt.modules = [];
    tt.courses.forEach(function (c) {
      (c.lessons || []).forEach(function (l) {
        tt.modules.push({
          id: l.ref || l.title, title: l.title, module: c.title,
          product: "SchoolCafé", _from_courses: true, _course_id: c.id, _lesson_type: l.type,
          source: l.origin_badge === "outside_vendor" ? "ICN_DOC" : "AI_TRANSCRIPT",
          status: "approved"
        });
      });
    });
    tt.progress = clone(store.progress || {});
    tt.locked = false; tt.locked_by = null;
    tt.days_remaining = null; tt.is_overdue = false;
    return tt;
  }

  function learnerName(persona) {
    if (persona === "dana-director") return "Dana Wright";
    if (persona === "sam-trainer") return "Sam Rivera";
    return "John Doe";
  }
  function gamification() {
    var done = 0, ld = (store.progress && store.progress.lessons_done) || {};
    Object.keys(ld).forEach(function (k) { done += (ld[k] || []).length; });
    var xp = done * 10;
    return {
      xp: xp, streak: done > 0 ? 1 : 0, level: 1 + Math.floor(xp / 100),
      badges: store.progress && store.progress.certified ? [{ title: "Track Complete" }] : [],
      next_badge_at: null
    };
  }
  function makeCert(track, pct, persona) {
    var now = new Date().toISOString();
    var nm = learnerName(persona);
    return {
      id: "cert-" + (track ? track.id : "x") + "-" + Date.now(),
      track_id: track ? track.id : "", track_title: track ? track.title : "", track_name: track ? track.title : "",
      title: track ? track.title : "", learner_name: nm, name: nm, recipient: nm, recipient_name: nm,
      issued_at: now, score_pct: pct, assessment_score_pct: pct, status: "issued"
    };
  }

  // ---- scoring ----
  function scoreAttempt(aid, answers, persona) {
    var a = findAssessment(aid);
    if (!a) return J({ detail: "assessment not found" }, 404);
    var qs = a.questions || [];
    var correct = 0; var per = [];
    qs.forEach(function (q) {
      var pick = answers ? answers[q._ptr] : undefined;
      var t = (q.type || "mcq"); var ok = false;
      if (t === "mcq") ok = pick === q.answer_index;
      else if (t === "tf") ok = pick === q.correct;
      else if (t === "fitb") ok = String(pick == null ? "" : pick).trim().toLowerCase() === String(q.answer || "").trim().toLowerCase();
      else if (t === "ordering") { var co = q.correct_order || []; ok = Array.isArray(pick) && pick.length === co.length && pick.every(function (v, i) { return v === co[i]; }); }
      if (ok) correct++;
      per.push({ stem: q.stem || q.prompt || "", correct: ok, source_quote: q.source_quote || q.source_span || q.source_sentence || "", explanation: q.explanation || "" });
    });
    var pct = qs.length ? Math.round(100 * correct / qs.length) : 0;
    var passPct = a.pass_pct || 70;
    var passed = pct >= passPct;
    store.attempts = store.attempts || {};
    store.attempts[aid] = (store.attempts[aid] || 0) + 1;
    var certificate = null;
    if (passed) {
      store.progress.assessment_passed = true;
      store.progress.assessment_score = pct;
      var tr = allTracks().filter(function (t) { return t.assessment_gate_id === aid; })[0];
      if (tr) {
        store.progress.certified = true;
        certificate = makeCert(tr, pct, persona);
        store.certs = store.certs || []; store.certs.push(certificate);
      }
    }
    persist();
    return J({
      score_pct: pct, passed: passed, per_question: per,
      attempts_used: store.attempts[aid], attempts_allowed: a.attempts_allowed || 3,
      certificate: certificate
    });
  }

  // ---- helpers ----
  function nid(prefix) { return prefix + "-" + Math.random().toString(36).slice(2, 8) + Date.now().toString(36).slice(-4); }
  function matchRole(t, persona) {
    if (persona === "sam-trainer") return true;            // trainer sees all
    var roles = (t.role_tags || []).map(function (r) { return String(r).toLowerCase(); });
    if (!roles.length) return true;
    if (persona === "dana-director") return roles.indexOf("cn director") >= 0 || roles.indexOf("director") >= 0;
    return roles.indexOf("cashier") >= 0 || roles.indexOf("site manager") >= 0; // john-cashier default
  }

  // ============================ ROUTER ===================================
  function route(path, method, persona, body, query) {
    // ---------- identity / config ----------
    if (path === "/api/config") return SEED.config;
    if (path === "/api/me") return SEED.me;
    if (path === "/api/auth/login") return { ok: true, signed_in: false };
    if (path === "/intent/resolve" || path === "/intent") return { ok: true };

    // ---------- gamification ----------
    var gm = path.match(/^\/api\/users\/[^/]+\/gamification$/);
    if (gm) return gamification();

    // ---------- tracks ----------
    if (path === "/api/tracks" && method === "GET") {
      return { tracks: allTracks().filter(function (t) { return matchRole(t, persona); }).map(trackListItem) };
    }
    if (path === "/api/tracks" && method === "POST") {
      var nt = { id: nid("track"), title: (body && body.title) || "Untitled track", description: (body && body.description) || "",
        product: "SchoolCafé", role_tags: (body && body.role_tags) || ["Cashier"], course_ids: [], module_ids: [],
        quiz_id: null, assessment_gate_id: null, status: "draft", sequential: true, assignments: [],
        created_at: new Date().toISOString() };
      store.userTracks = store.userTracks || []; store.userTracks.push(nt); persist();
      return nt;
    }
    var tm = path.match(/^\/api\/tracks\/([^/]+)(\/[a-z-]+)?$/);
    if (tm) {
      var tid = decodeURIComponent(tm[1]); var sub = tm[2] || "";
      var t = findTrack(tid);
      if (sub === "" && method === "GET") { return t ? expandTrack(t) : J({ detail: "not found" }, 404); }
      // mutations only meaningful on user tracks; seed track is read-only but we no-op gracefully
      var ut = (store.userTracks || []).filter(function (x) { return x.id === tid; })[0];
      if (sub === "" && (method === "PUT" || method === "PATCH")) { if (ut && body) Object.assign(ut, body); persist(); return ut || t; }
      if (sub === "" && method === "DELETE") { store.userTracks = (store.userTracks || []).filter(function (x) { return x.id !== tid; }); persist(); return { ok: true }; }
      if (sub === "/modules") { if (ut && body) ut.module_ids = body.module_ids || []; persist(); return ut || t; }
      if (sub === "/courses") { if (ut && body) ut.course_ids = body.course_ids || ut.course_ids; persist(); return ut || t; }
      if (sub === "/quiz") { if (ut && body) ut.quiz_id = body.quiz_id; persist(); return ut || t; }
      if (sub === "/assessment-gate") { if (ut && body) ut.assessment_gate_id = body.assessment_id || body.assessment_gate_id; persist(); return ut || t; }
      if (sub === "/publish") { if (ut) ut.status = "published"; persist(); return ut || t; }
      if (sub === "/assignments") { if (ut && body) { ut.assignments = ut.assignments || []; ut.assignments.push(body); } persist(); return ut || t; }
      if (sub === "/lesson-progress" && method === "POST") {
        store.progress.lessons_done = store.progress.lessons_done || {};
        var cid = body && body.course_id, ref = body && body.lesson_ref;
        if (cid && ref) { var arr = store.progress.lessons_done[cid] || (store.progress.lessons_done[cid] = []); if (arr.indexOf(ref) < 0) arr.push(ref); }
        persist();
        return { ok: true, progress: store.progress };
      }
    }

    // ---------- courses ----------
    if (path === "/api/courses" && method === "GET") return { courses: allCourses() };
    if (path === "/api/courses" && method === "POST") {
      var nc = { id: nid("course"), title: (body && body.title) || "Untitled course", description: (body && body.description) || "",
        product: "SchoolCafé", role_tags: (body && body.role_tags) || ["Cashier"], lessons: (body && body.lessons) || [], status: "draft",
        created_at: new Date().toISOString() };
      store.userCourses = store.userCourses || []; store.userCourses.push(nc); persist(); return nc;
    }
    if (path === "/api/courses/images") return { images: [] };
    var cm = path.match(/^\/api\/courses\/([^/]+)(\/[a-z-]+)?$/);
    if (cm) {
      var cid2 = decodeURIComponent(cm[1]); var csub = cm[2] || "";
      var c = findCourse(cid2); var uc = (store.userCourses || []).filter(function (x) { return x.id === cid2; })[0];
      if (csub === "" && method === "GET") return c ? c : J({ detail: "not found" }, 404);
      if (csub === "" && (method === "PUT" || method === "PATCH")) { if (uc && body) Object.assign(uc, body); persist(); return uc || c; }
      if (csub === "" && method === "DELETE") { store.userCourses = (store.userCourses || []).filter(function (x) { return x.id !== cid2; }); persist(); return { ok: true }; }
      if (csub === "/publish") { if (uc) uc.status = "published"; persist(); return uc || c; }
    }

    // ---------- quizzes ----------
    if (path === "/api/quizzes" && method === "GET") return { quizzes: allQuizzes() };
    if ((path === "/api/quizzes" || path === "/api/quizzes/create" || path === "/api/quizzes/generate") && method === "POST") {
      var nq = { id: nid("quiz"), title: (body && body.title) || "Untitled quiz", status: "draft",
        questions: (body && body.questions) || [], source_label: (body && body.source_label) || "", created_at: new Date().toISOString() };
      store.userQuizzes = store.userQuizzes || []; store.userQuizzes.push(nq); persist(); return nq;
    }
    var qm = path.match(/^\/api\/quizzes\/([^/]+)(\/[a-z-]+)?$/);
    if (qm) {
      var qid = decodeURIComponent(qm[1]); var qsub = qm[2] || "";
      var q = findQuiz(qid); var uq = (store.userQuizzes || []).filter(function (x) { return x.id === qid; })[0];
      if (qsub === "" && method === "GET") return q ? q : J({ detail: "not found" }, 404);
      if (qsub === "" && (method === "PUT" || method === "PATCH")) { if (uq && body) Object.assign(uq, body); persist(); return uq || q; }
      if (qsub === "/publish") { if (uq) uq.status = "approved"; persist(); return uq || q; }
    }

    // ---------- assessments ----------
    if (path === "/api/assessments" && method === "GET") return { assessments: allAssessments() };
    if ((path === "/api/assessments" || path === "/api/assessments/auto-assemble") && method === "POST") {
      var na = { id: nid("as"), title: (body && body.title) || "Untitled assessment", pass_pct: (body && body.pass_pct) || 70,
        attempts_allowed: (body && body.attempts_allowed) || 3, time_limit_min: (body && body.time_limit_min) || 15,
        status: "draft", questions: (body && body.questions) || [], question_ids: (body && body.question_ids) || [],
        created_at: new Date().toISOString() };
      na.question_count = na.questions.length;
      store.userAssessments = store.userAssessments || []; store.userAssessments.push(na); persist(); return na;
    }
    var am = path.match(/^\/api\/assessments\/([^/]+)(\/[a-z-]+)?$/);
    if (am) {
      var aid = decodeURIComponent(am[1]); var asub = am[2] || "";
      var a = findAssessment(aid); var ua = (store.userAssessments || []).filter(function (x) { return x.id === aid; })[0];
      if (asub === "" && method === "GET") return a ? a : J({ detail: "not found" }, 404);
      if (asub === "" && (method === "PUT" || method === "PATCH")) { if (ua && body) Object.assign(ua, body); persist(); return ua || a; }
      if (asub === "/publish") { if (ua) ua.status = "published"; persist(); return ua || a; }
      if (asub === "/attempts" && method === "GET") { return { attempts_used: (store.attempts && store.attempts[aid]) || 0, attempts_allowed: (a && a.attempts_allowed) || 3 }; }
      if (asub === "/attempt" && method === "POST") { return scoreAttempt(aid, body && body.answers, persona); }
    }

    // ---------- certificates ----------
    if (path === "/api/certificates" && method === "POST") {
      var ctid = body && body.track_id; var ctr = findTrack(ctid);
      var gate = (ctr && ctr.assessment_gate_id || "").trim();
      if (gate && !(store.progress && store.progress.assessment_passed)) {
        return J({ error: "must_pass_assessment", assessment_id: gate, detail: "You must pass the track assessment before receiving a certificate." }, 409);
      }
      var cert = makeCert(ctr, (store.progress && store.progress.assessment_score) || 100, persona);
      store.certs = store.certs || []; store.certs.push(cert); if (store.progress) store.progress.certified = true; persist();
      return cert;
    }
    if (path === "/api/certificates" && method === "GET") return { certificates: store.certs || [] };
    if (path.indexOf("/api/certificates/") === 0) return { certificates: store.certs || [] };

    // ---------- ICN (videos) ----------
    if (path === "/api/icn") return SEED.icnCatalog;
    if (path === "/api/icn/flashcards" || path === "/api/icn/quiz") return { items: [], cards: [] };
    var im = path.match(/^\/api\/icn\/([^/]+)$/);
    if (im) { var as = SEED.icnAssets[decodeURIComponent(im[1])]; return as ? as : J({ detail: "not found" }, 404); }

    // ---------- resources (guide HTML, webinar cards) ----------
    if (path === "/resources" && method === "GET") return SEED.resourcesList || [];
    var rh = path.match(/^\/resources\/([^/]+)\/html$/);
    if (rh) { var html = SEED.resourcesHtml[decodeURIComponent(rh[1])]; return html != null ? HTML(html) : HTML("<p style='color:#50665A;padding:16px'>Content unavailable in this offline preview.</p>"); }
    var rp = path.match(/^\/resources\/([^/]+)\/pdf$/);
    if (rp) return HTML("<!doctype html><meta charset=utf-8><body style='font-family:sans-serif;padding:40px;color:#14201A'><h2>PDF export</h2><p>PDF download isn't available in this self-contained preview.</p></body>");

    // ---------- catalog / library / misc reads ----------
    if (path.indexOf("/api/modules") === 0) {
      var mods = (SEED.modules.modules || []).slice();
      if (query.source) mods = mods.filter(function (m) { return m.source === query.source; });
      if (query.role) mods = mods.filter(function (m) { return (m.role_tags || []).indexOf(query.role) >= 0; });
      if (query.product) mods = mods.filter(function (m) { return m.product === query.product; });
      if (query.q) { var ql = query.q.toLowerCase(); mods = mods.filter(function (m) { return (m.title || "").toLowerCase().indexOf(ql) >= 0 || (m.module || "").toLowerCase().indexOf(ql) >= 0; }); }
      return { modules: mods, total: mods.length, sources: SEED.modules.sources };
    }
    if (path === "/api/flashcards" || path.indexOf("/api/flashcards") === 0) return SEED.flashcards || { flashcards: [] };
    if (path === "/api/whats-next") return SEED.whatsNext;
    if (path.indexOf("/api/whats-new") === 0) return SEED.whatsNew;
    if (path === "/api/stats/content") return SEED.stats;
    if (path === "/api/progress" && method === "GET") return store.progress || {};
    if (path === "/api/progress" && method === "POST") { persist(); return { ok: true }; }
    if (path === "/api/evals") return { evals: [], runs: [] };
    if (path === "/api/regulatory-dates" || path.indexOf("/api/regulatory-dates") === 0) return { dates: [] };
    if (path.indexOf("/api/library/ask") === 0) return { answer: "", citations: [] };

    // ---------- district / project / roster / gaps (district mgmt is removed) ----------
    // Safe empty responses so any stray call degrades gracefully instead of crashing.
    if (method === "GET") {
      return { ok: true, items: [], tracks: [], modules: [], courses: [], resources: [],
        cards: [], assessments: [], quizzes: [], flashcards: [], districts: [], projects: [],
        users: [], roster: [], tasks: [], sections: [], notes: [], dates: [], rules: [] };
    }
    return { ok: true };
  }

  // ============================ FETCH OVERRIDE ===========================
  window.fetch = function (url, opts) {
    var u = (typeof url === "string") ? url : (url && url.url) || "";
    // strip scheme+host for http(s) AND file:// so the shim works when the file is
    // opened directly (file:///…) as well as served over http.
    var full = u.replace(/^[a-z][a-z0-9+.\-]*:\/\/[^/]*/i, "");
    var qi = full.indexOf("?");
    var path = (qi >= 0 ? full.slice(0, qi) : full).split("#")[0];
    var query = {};
    if (qi >= 0) {
      full.slice(qi + 1).split("&").forEach(function (kv) {
        if (!kv) return; var p = kv.split("="); query[decodeURIComponent(p[0])] = decodeURIComponent((p[1] || "").replace(/\+/g, " "));
      });
    }
    if (!/^\/(api|resources|intent|course-img)\b/.test(path)) {
      return realFetch ? realFetch(url, opts) : Promise.resolve(J({}));
    }
    var method = ((opts && opts.method) || "GET").toUpperCase();
    var persona = "";
    try { persona = (opts && opts.headers && (opts.headers["X-Demo-User"] || opts.headers["x-demo-user"])) || ""; } catch (e) {}
    var body = null;
    try { body = (opts && opts.body) ? JSON.parse(opts.body) : null; } catch (e) {}
    try {
      var res = route(path, method, persona, body, query);
      if (res instanceof Response) return Promise.resolve(res);
      return Promise.resolve(J(res));
    } catch (e) {
      console.warn("[cts-shim] error", path, e);
      return Promise.resolve(J({ ok: true }));
    }
  };
})();
