/* ============================================================================
   District / Customer Studio — standalone UI layer (Block B, unified build).
   Injected at the BOTTOM of the real app's <script> so it shares scope.

   The "customer" view of the real app IS both surfaces, switchable via the
   "Previewing as" role selector:
     • CN Director → My Team  (the district training-supervisor / admin view)
     • Cashier     → Learn    (the learner view: gated lessons, quizzes, cert)

   This layer:
     1. Adds sequential gating to the learner course player (no skipping ahead).
     2. Boots as the CN Director and lands on My Team (the admin view) — but the
        role switch gives a fully real learner experience with no extra setup.
     3. Dismisses the simulated first-visit sign-in (no backend to authenticate).
   It does NOT strip any customer surface — both halves are first-class.
   ============================================================================ */
(function () {
  "use strict";

  function dasToast(msg) {
    var t = document.getElementById("das-toast");
    if (!t) { t = document.createElement("div"); t.id = "das-toast"; document.body.appendChild(t); }
    t.textContent = msg; t.classList.add("show");
    clearTimeout(t._t); t._t = setTimeout(function () { t.classList.remove("show"); }, 2400);
  }
  window.__dasToast = dasToast;

  var st = document.createElement("style");
  st.textContent =
    ".cp-rail-lesson.das-locked{opacity:.4;pointer-events:none}" +
    ".cp-btn-next.das-next-locked{opacity:.55;filter:grayscale(.35)}" +
    "#das-toast{position:fixed;left:50%;bottom:26px;transform:translateX(-50%) translateY(16px);opacity:0;transition:.25s;background:#14201A;color:#fff;padding:11px 18px;border-radius:10px;font-weight:600;font-size:14px;z-index:99999;pointer-events:none;box-shadow:0 8px 24px rgba(0,0,0,.25)}" +
    "#das-toast.show{opacity:1;transform:translateX(-50%) translateY(0)}";
  document.head.appendChild(st);

  // ===================== 1. Sequential gating in the learner player =====================
  function _dasFirstIncomplete() {
    if (typeof _cpState === "undefined" || !_cpState) return -1;
    var all = _cpState.allLessons || [];
    for (var i = 0; i < all.length; i++) { if (!_cpIsDone(all[i].courseId, all[i].lessonRef)) return i; }
    return all.length - 1;
  }
  if (typeof cpGoToLesson === "function") {
    var _origGo = cpGoToLesson;
    cpGoToLesson = function (idx) {
      if (typeof _cpState !== "undefined" && _cpState) {
        var fi = _dasFirstIncomplete();
        if (idx > fi) { dasToast("Finish the earlier steps first — that's how the chapter unlocks."); return; }
      }
      return _origGo.call(this, idx);
    };
  }
  if (typeof cpNext === "function") {
    var _origNext = cpNext;
    cpNext = function () {
      if (typeof _cpState !== "undefined" && _cpState) {
        var cur = _cpState.allLessons[_cpState.currentIdx];
        if (cur && !_cpIsDone(cur.courseId, cur.lessonRef)) { dasToast("Finish this step to continue."); return; }
      }
      return _origNext.apply(this, arguments);
    };
  }
  if (typeof _cpRender === "function") {
    var _origRender = _cpRender;
    _cpRender = function () { _origRender.apply(this, arguments); try { _dasApplyLocks(); } catch (e) {} };
  }
  function _dasApplyLocks() {
    if (typeof _cpState === "undefined" || !_cpState) return;
    var fi = _dasFirstIncomplete();
    document.querySelectorAll(".cp-rail-lesson").forEach(function (el, idx) {
      if (idx > fi) { el.classList.add("das-locked"); el.setAttribute("aria-disabled", "true"); var n = el.querySelector(".cp-rl-num"); if (n) n.textContent = "🔒"; }
    });
    var cur = _cpState.allLessons[_cpState.currentIdx];
    var nb = document.getElementById("cp-btn-next");
    if (nb && cur && !_cpIsDone(cur.courseId, cur.lessonRef)) { nb.classList.add("das-next-locked"); nb.title = "Finish this step to continue"; }
  }

  // ===================== 2. Boot as CN Director, land on My Team =====================
  function dismissSignin() {
    try { if (typeof doLogin === "function") doLogin(); } catch (e) {}
    var lm = document.getElementById("login-modal"); if (lm) lm.hidden = true;
    var pj = document.getElementById("pj-signin"); if (pj) pj.hidden = true;
  }
  function landOnMyTeam() {
    dismissSignin();
    try { if (typeof showView === "function") showView("myteam"); } catch (e) {}
    try { if (typeof loadMyTeam === "function") loadMyTeam(); } catch (e) {}
    var sel = document.getElementById("learn-role"); if (sel) sel.value = "CN Director";
  }
  function boot() {
    try {
      if (typeof _demoState === "object" && _demoState) _demoState.learnRole = "CN Director";
      if (typeof setViewMode === "function") setViewMode("customer");
      else if (typeof applyViewMode === "function") applyViewMode();
      if (typeof _learnRoleChanged === "function") { try { _learnRoleChanged("CN Director"); } catch (e) {} }
      dismissSignin();
      var ob = document.getElementById("onboarding-overlay"); if (ob) ob.hidden = true;
      landOnMyTeam();
      setTimeout(landOnMyTeam, 350);
    } catch (e) { console.warn("[das-boot]", e); }
  }
  if (document.readyState === "loading") {
    window.addEventListener("DOMContentLoaded", function () { setTimeout(boot, 120); });
  } else {
    setTimeout(boot, 120);
  }
})();
