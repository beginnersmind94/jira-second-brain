/* ============================================================================
   District-Admin Studio — standalone backend shim (Block A, director build).
   Runs BEFORE the real app script. Overrides window.fetch so every /api & /resources
   call is served by REPLAYING real responses captured from the live backend for the
   CN Director (dana-director) persona — "exactly what the admin would see", offline.
   Token __SEED__ is replaced by build_share_director.py with the seed JSON.
   Read-mostly: writes (nudge / assign / progress) return safe acknowledgements and
   persist lesson progress to localStorage so the page is clickable and resets cleanly.
   ============================================================================ */
(function () {
  "use strict";
  var SEED = __SEED__;
  var BY = SEED.byPath || {};
  var LS = "das_share_store_v1";

  function clone(o) { return JSON.parse(JSON.stringify(o)); }
  function loadStore() { try { var r = localStorage.getItem(LS); if (r) return JSON.parse(r); } catch (e) {} return clone(SEED.initialStore); }
  var store = loadStore();
  function persist() { try { localStorage.setItem(LS, JSON.stringify(store)); } catch (e) {} }
  window.__dasStore = function () { return store; };
  window.__dasReset = function () { store = clone(SEED.initialStore); persist(); location.reload(); };
  window.__dasSeed = SEED;

  var realFetch = window.fetch ? window.fetch.bind(window) : null;
  function J(obj, status) { return new Response(JSON.stringify(obj == null ? {} : obj), { status: status || 200, headers: { "Content-Type": "application/json" } }); }
  function HTML(html, status) { return new Response(html || "", { status: status || 200, headers: { "Content-Type": "text/html; charset=utf-8" } }); }

  function filterModules(m, query) {
    if (!m || !m.modules) return { modules: [], total: 0, sources: {} };
    var mods = m.modules.slice();
    if (query.source) mods = mods.filter(function (x) { return x.source === query.source; });
    if (query.role) mods = mods.filter(function (x) { return (x.role_tags || []).indexOf(query.role) >= 0; });
    if (query.product) mods = mods.filter(function (x) { return x.product === query.product; });
    if (query.q) { var ql = query.q.toLowerCase(); mods = mods.filter(function (x) { return (x.title || "").toLowerCase().indexOf(ql) >= 0 || (x.module || "").toLowerCase().indexOf(ql) >= 0; }); }
    return { modules: mods, total: mods.length, sources: m.sources || {} };
  }

  function route(path, method, query, body) {
    // ---------- writes: acknowledge + persist lesson progress ----------
    if (method !== "GET") {
      if (/\/lesson-progress$/.test(path)) {
        store.progress = store.progress || { lessons_done: {} };
        store.progress.lessons_done = store.progress.lessons_done || {};
        var cid = body && body.course_id, ref = body && body.lesson_ref;
        if (cid && ref) { var a = store.progress.lessons_done[cid] || (store.progress.lessons_done[cid] = []); if (a.indexOf(ref) < 0) a.push(ref); }
        persist();
        return { ok: true, progress: store.progress };
      }
      if (/\/nudge-all-overdue$/.test(path)) return { ok: true, count: 0, message: "Reminders logged — delivery requires live roster sync (offline preview)." };
      if (/\/nudge$/.test(path)) { var n = (body && body.user_ids) ? body.user_ids.length : 1; return { ok: true, count: n, message: "Reminder logged for " + n + " staff — delivery requires live roster sync (offline preview)." }; }
      if (/\/assign/.test(path)) return { ok: true, message: "Saved in this preview only (no server)." };
      if (path === "/api/progress") { persist(); return { ok: true }; }
      return { ok: true };
    }

    // ---------- exact captured response (the real director data) ----------
    if (Object.prototype.hasOwnProperty.call(BY, path)) {
      if (path === "/api/modules") return filterModules(BY[path], query);
      return BY[path];
    }

    // ---------- normalized (query-stripped) captured reads ----------
    if (path.indexOf("/api/modules") === 0) return filterModules(BY["/api/modules"], query);
    if (path.indexOf("/api/whats-new") === 0) return BY["/api/whats-new"] || { items: [] };
    if (path.indexOf("/api/whats-next") === 0) return BY["/api/whats-next"] || {};
    if (path.indexOf("/api/regulatory-dates") === 0) return BY["/api/regulatory-dates"] || { deadlines: [], total: 0 };
    if (path.indexOf("/api/flashcards") === 0) return BY["/api/flashcards"] || { flashcards: [] };
    if (path.indexOf("/api/stats/content") === 0) return BY["/api/stats/content"] || {};
    if (path === "/api/icn") return BY["/api/icn"] || { cards: [], total: 0 };
    if (path.indexOf("/api/certificates") === 0) return { certificates: store.certs || [] };
    if (path === "/api/progress") return store.progress || {};

    var gm = path.match(/^\/api\/users\/[^/]+\/gamification$/);
    if (gm) return { xp: 0, streak: 0, level: 1, badges: [], next_badge_at: null };

    // roster by track (fallback if not an exact capture)
    var rt = path.match(/^\/api\/roster\/([^/]+)$/);
    if (rt) { var rk = "/api/roster/" + rt[1]; if (BY[rk]) return BY[rk]; return { track_id: decodeURIComponent(rt[1]), rows: [], summary: {} }; }
    // track by id (fallback)
    var tk = path.match(/^\/api\/tracks\/([^/]+)$/);
    if (tk) { var tkk = "/api/tracks/" + tk[1]; if (BY[tkk]) return BY[tkk]; return J({ detail: "not found" }, 404); }

    // resources: list + html/pdf/report stubs (server-rendered, not bundled)
    if (path === "/resources") return [];
    if (/^\/resources\/[^/]+\/html$/.test(path)) return HTML("<p style='font-family:sans-serif;color:#50665A;padding:16px'>This guide's body isn't bundled in the offline preview. Open the live Studio to read it.</p>");
    if (/^\/resources\/[^/]+\/pdf$/.test(path) || /\/report$/.test(path)) return HTML("<!doctype html><meta charset=utf-8><body style='font-family:sans-serif;padding:40px;color:#14201A;max-width:640px;margin:auto'><h2>Compliance report</h2><p>The printable PDF report is generated by the server and isn't available in this self-contained preview. In the live app this downloads a per-district attestation.</p></body>");

    // ---------- safe empty (any stray call degrades gracefully) ----------
    return { ok: true, items: [], tracks: [], modules: [], courses: [], resources: [], cards: [],
      roster: [], rows: [], deadlines: [], certificates: [], districts: [], projects: [],
      assessments: [], quizzes: [], flashcards: [], users: [], tasks: [], notes: [], dates: [], rules: [] };
  }

  window.fetch = function (url, opts) {
    var u = (typeof url === "string") ? url : (url && url.url) || "";
    var full = u.replace(/^[a-z][a-z0-9+.\-]*:\/\/[^/]*/i, "");   // strip http(s)://host AND file://
    var qi = full.indexOf("?");
    var path = (qi >= 0 ? full.slice(0, qi) : full).split("#")[0];
    var query = {};
    if (qi >= 0) full.slice(qi + 1).split("&").forEach(function (kv) { if (!kv) return; var p = kv.split("="); query[decodeURIComponent(p[0])] = decodeURIComponent((p[1] || "").replace(/\+/g, " ")); });
    if (!/^\/(api|resources|intent|course-img)\b/.test(path)) { return realFetch ? realFetch(url, opts) : Promise.resolve(J({})); }
    var method = ((opts && opts.method) || "GET").toUpperCase();
    var body = null; try { body = (opts && opts.body) ? JSON.parse(opts.body) : null; } catch (e) {}
    try {
      var res = route(path, method, query, body);
      return Promise.resolve(res instanceof Response ? res : J(res));
    } catch (e) {
      console.warn("[das-shim] error", path, e);
      return Promise.resolve(J({ ok: true }));
    }
  };
})();
