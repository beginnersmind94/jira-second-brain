/**
 * sw.js — Learning Studio service worker (PLT-1 offline PWA).
 *
 * Strategy:
 *   - Static assets (/static/*): cache-first, update in background.
 *   - App shell (/, /static/index.html): cache-first.
 *   - API calls (/api/*): network-first; on failure return a JSON
 *     {error:"offline",offline:true} stub so the app can degrade gracefully.
 *
 * Scope: / (served from root via /sw.js route in demo_app.py).
 *
 * Background sync tag: "ls-progress-sync"
 *   When the browser fires this sync event the SW tells all clients to flush
 *   their IndexedDB offline-progress queue via a postMessage.
 */

const CACHE_NAME = 'ls-pwa-v1';
const PRECACHE   = ['/', '/static/index.html'];

// ── Lifecycle ─────────────────────────────────────────────────────────────────

self.addEventListener('install', evt => {
  evt.waitUntil(
    caches.open(CACHE_NAME).then(c => c.addAll(PRECACHE))
  );
  self.skipWaiting();
});

self.addEventListener('activate', evt => {
  evt.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    )
  );
  self.clients.claim();
});

// ── Fetch ─────────────────────────────────────────────────────────────────────

self.addEventListener('fetch', evt => {
  const { request } = evt;
  const url = new URL(request.url);

  // Only intercept same-origin GET requests.
  if (request.method !== 'GET' || url.origin !== self.location.origin) return;

  if (url.pathname.startsWith('/api/')) {
    // Network-first: fall back to an offline stub on failure.
    evt.respondWith(
      fetch(request).catch(() =>
        new Response(
          JSON.stringify({ error: 'offline', offline: true }),
          { status: 503, headers: { 'Content-Type': 'application/json' } }
        )
      )
    );
    return;
  }

  // Cache-first for everything else (app shell + static assets).
  evt.respondWith(
    caches.match(request).then(cached => {
      if (cached) {
        // Update in background.
        fetch(request).then(resp => {
          if (resp.ok) caches.open(CACHE_NAME).then(c => c.put(request, resp));
        }).catch(() => {});
        return cached;
      }
      // Not cached — fetch and cache.
      return fetch(request).then(resp => {
        if (resp.ok) {
          const clone = resp.clone();
          caches.open(CACHE_NAME).then(c => c.put(request, clone));
        }
        return resp;
      });
    })
  );
});

// ── Background sync ───────────────────────────────────────────────────────────

self.addEventListener('sync', evt => {
  if (evt.tag === 'ls-progress-sync') {
    // Tell all open clients to flush their IDB offline-progress queue.
    evt.waitUntil(
      self.clients.matchAll({ type: 'window' }).then(clients =>
        clients.forEach(c => c.postMessage({ type: 'FLUSH_PROGRESS_QUEUE' }))
      )
    );
  }
});
