// One More — service worker. App shell is cached so the app opens instantly / offline; the page itself is network-first so
// updates arrive on the next launch. MediaPipe runtime + model are cached on first use (they are large, ~10 MB).
const VERSION = "rv-1";
const SHELL = ["./", "./index.html", "./manifest.json", "../counting/icons/icon-192.png", "../counting/icons/icon-512.png", "../counting/icons/maskable-512.png"];
self.addEventListener("install", e => { e.waitUntil(caches.open(VERSION).then(c => c.addAll(SHELL)).then(() => self.skipWaiting())); });
self.addEventListener("activate", e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== VERSION).map(k => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener("fetch", e => {
  const url = new URL(e.request.url);
  if (e.request.method !== "GET") return;
  const isShell = url.origin === location.origin;
  const isAsset = /cdn\.jsdelivr\.net\/npm\/@mediapipe|storage\.googleapis\.com\/mediapipe-models/.test(url.href);
  if (isShell) {
    // network first, cache fallback (so a new deploy shows up on the next open, but offline still works)
    e.respondWith(fetch(e.request).then(r => { const copy = r.clone(); caches.open(VERSION).then(c => c.put(e.request, copy)); return r; })
      .catch(() => caches.match(e.request).then(r => r || caches.match("./index.html"))));
  } else if (isAsset) {
    // cache first: the model and wasm never change for a pinned version
    e.respondWith(caches.match(e.request).then(r => r || fetch(e.request).then(res => { const copy = res.clone(); caches.open(VERSION + "-assets").then(c => c.put(e.request, copy)); return res; })));
  }
});
