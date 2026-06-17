/* ============================================================================
   District-Admin Studio — standalone UI layer (Block B, director build).
   Injected at the BOTTOM of the real app's <script> so it shares scope.
   Boots the app as the CN DIRECTOR (customer view + "CN Director" role) and lands
   on "My Team" — the district training-supervisor surface (roster, compliance %,
   overdue, assign training, compliance calendar). No content-authoring / trainer
   pipeline is shown (that's the trainer's job and stays hidden in customer view).
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
    "#das-toast{position:fixed;left:50%;bottom:26px;transform:translateX(-50%) translateY(16px);opacity:0;transition:.25s;background:#14201A;color:#fff;padding:11px 18px;border-radius:10px;font-weight:600;font-size:14px;z-index:99999;pointer-events:none;box-shadow:0 8px 24px rgba(0,0,0,.25)}" +
    "#das-toast.show{opacity:1;transform:translateX(-50%) translateY(0)}";
  document.head.appendChild(st);

  // The real app shows a simulated first-visit sign-in over the view. There's no
  // backend to authenticate against in the offline file, so dismiss it (the app's
  // own doLogin() path) and the admin lands straight on their district.
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
      // 1. Be the CN Director (customer-side supervisor), not a trainer/author.
      if (typeof _demoState === "object" && _demoState) _demoState.learnRole = "CN Director";
      if (typeof setViewMode === "function") setViewMode("customer");
      else if (typeof applyViewMode === "function") applyViewMode();
      if (typeof _learnRoleChanged === "function") { try { _learnRoleChanged("CN Director"); } catch (e) {} }
      // dismiss the simulated sign-in + learner first-run overlay so nothing covers the supervisor view
      dismissSignin();
      var ob = document.getElementById("onboarding-overlay"); if (ob) ob.hidden = true;
      // 2. Land on My Team (the thing the admin opens the product for).
      landOnMyTeam();
      // 3. Re-assert once more after the app's own async boot settles.
      setTimeout(landOnMyTeam, 350);
    } catch (e) { console.warn("[das-boot]", e); }
  }

  if (document.readyState === "loading") {
    window.addEventListener("DOMContentLoaded", function () { setTimeout(boot, 120); });
  } else {
    setTimeout(boot, 120);
  }
})();
