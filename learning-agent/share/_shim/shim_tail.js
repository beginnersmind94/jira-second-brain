/* ============================================================================
   Cashier Training Studio — standalone UI layer (Block B).
   Injected at the BOTTOM of the real app's <script> so it shares scope and can
   wrap the app's own functions / read its let-scoped state.
   Does three things:
     1. Removes the district-management surface (cashier-only scope).
     2. Adds sequential gating to the course player (no skipping ahead).
     3. Lands the trainer on the LEARNER view first (the thing they asked to see).
   ============================================================================ */
(function () {
  "use strict";

  function ctsToast(msg) {
    var t = document.getElementById("cts-toast");
    if (!t) { t = document.createElement("div"); t.id = "cts-toast"; document.body.appendChild(t); }
    t.textContent = msg; t.classList.add("show");
    clearTimeout(t._t); t._t = setTimeout(function () { t.classList.remove("show"); }, 2200);
  }
  window.__ctsToast = ctsToast;

  // ---- inject CSS (gating affordances + toast) ----
  var st = document.createElement("style");
  st.textContent =
    ".cp-rail-lesson.cts-locked{opacity:.4;pointer-events:none}" +
    ".cp-btn-next.cts-next-locked{opacity:.55;filter:grayscale(.35)}" +
    "#cts-toast{position:fixed;left:50%;bottom:26px;transform:translateX(-50%) translateY(16px);opacity:0;transition:.25s;background:#14201A;color:#fff;padding:11px 18px;border-radius:10px;font-weight:600;font-size:14px;z-index:99999;pointer-events:none;box-shadow:0 8px 24px rgba(0,0,0,.25)}" +
    "#cts-toast.show{opacity:1;transform:translateX(-50%) translateY(0)}";
  document.head.appendChild(st);

  // ===================== 1. Remove district management =====================
  if (typeof applyViewMode === "function") {
    var _origAVM = applyViewMode;
    applyViewMode = function () {
      _origAVM.apply(this, arguments);
      var tm = document.getElementById("tab-manage"); if (tm) tm.hidden = true;     // "Districts" nav
      var ib = document.getElementById("inbox-btn"); if (ib) ib.hidden = true;       // approvals inbox (district)
    };
  }
  if (typeof showView === "function") {
    var _origShow = showView;
    var BLOCKED = { manage: 1, district: 1, projects: 1, roster: 1, "csv-upload": 1, "project-dashboard": 1 };
    showView = function (name) {
      if (BLOCKED[name]) name = (typeof _viewMode !== "undefined" && _viewMode === "customer") ? "learn" : "library";
      return _origShow.call(this, name);
    };
  }

  // ===================== 2. Sequential gating in the player =====================
  function _ctsFirstIncomplete() {
    if (typeof _cpState === "undefined" || !_cpState) return -1;
    var all = _cpState.allLessons || [];
    for (var i = 0; i < all.length; i++) {
      if (!_cpIsDone(all[i].courseId, all[i].lessonRef)) return i;
    }
    return all.length - 1; // everything done → last
  }
  if (typeof cpGoToLesson === "function") {
    var _origGo = cpGoToLesson;
    cpGoToLesson = function (idx) {
      if (typeof _cpState !== "undefined" && _cpState) {
        var fi = _ctsFirstIncomplete();
        if (idx > fi) { ctsToast("Finish the earlier steps first — that's how the chapter unlocks."); return; }
      }
      return _origGo.call(this, idx);
    };
  }
  if (typeof cpNext === "function") {
    var _origNext = cpNext;
    cpNext = function () {
      if (typeof _cpState !== "undefined" && _cpState) {
        var cur = _cpState.allLessons[_cpState.currentIdx];
        if (cur && !_cpIsDone(cur.courseId, cur.lessonRef)) {
          ctsToast("Finish this step to continue."); return;
        }
      }
      return _origNext.apply(this, arguments);
    };
  }
  if (typeof _cpRender === "function") {
    var _origRender = _cpRender;
    _cpRender = function () {
      _origRender.apply(this, arguments);
      try { _ctsApplyLocks(); } catch (e) {}
    };
  }
  function _ctsApplyLocks() {
    if (typeof _cpState === "undefined" || !_cpState) return;
    var fi = _ctsFirstIncomplete();
    var rail = document.querySelectorAll(".cp-rail-lesson");
    rail.forEach(function (el, idx) {
      if (idx > fi) {
        el.classList.add("cts-locked"); el.setAttribute("aria-disabled", "true");
        var n = el.querySelector(".cp-rl-num"); if (n) n.textContent = "🔒";
      }
    });
    var cur = _cpState.allLessons[_cpState.currentIdx];
    var curDone = cur && _cpIsDone(cur.courseId, cur.lessonRef);
    var nb = document.getElementById("cp-btn-next");
    if (nb && !curDone) { nb.classList.add("cts-next-locked"); nb.title = "Finish this step to continue"; }
  }

  // ===================== 3. Land on the learner view first =====================
  function _ctsBoot() {
    try {
      if (typeof setViewMode === "function") setViewMode("customer");
      else if (typeof applyViewMode === "function") applyViewMode();
    } catch (e) {}
  }
  if (document.readyState === "loading") {
    window.addEventListener("DOMContentLoaded", function () { setTimeout(_ctsBoot, 40); });
  } else {
    setTimeout(_ctsBoot, 40);
  }
})();
