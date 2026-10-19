// Offline-Cache für Brand-Weg. Seite und Daten zuerst aus dem Netz (Updates kommen sofort an), offline aus dem Speicher.
// Weltbilder und Schriften ändern sich nicht: zuerst aus dem Speicher.
const CACHE = "brand-weg-v5";
const SHELL = ["./", "./index.html", "./data.js", "./supabase.js", "./manifest.webmanifest", "./icon-192.png", "./icon-512.png", "./apple-touch-icon.png",
  "./assets/w1.jpg", "./assets/w2.jpg", "./assets/w3.jpg", "./assets/w4.jpg", "./assets/w5.jpg", "./assets/w6.jpg"];
self.addEventListener("install", e => { self.skipWaiting(); e.waitUntil(caches.open(CACHE).then(c => Promise.all(SHELL.map(u => c.add(u).catch(() => null))))); });
self.addEventListener("activate", e => e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim())));
const put = (req, res) => { if (res && (res.ok || res.type === "opaque")) { const copy = res.clone(); caches.open(CACHE).then(c => c.put(req, copy)); } return res; };
self.addEventListener("fetch", e => {
  const req = e.request; if (req.method !== "GET") return;
  const url = new URL(req.url), same = url.origin === self.location.origin, font = /fonts\.(googleapis|gstatic)\.com$/.test(url.hostname);
  if (!same && !font) return; // Supabase geht direkt ans Netz
  if (font || url.pathname.includes("/assets/")) { e.respondWith(caches.match(req).then(hit => hit || fetch(req).then(res => put(req, res)))); return; }
  e.respondWith(fetch(req).then(res => put(req, res)).catch(() => caches.match(req, {ignoreSearch: true}).then(hit => hit || caches.match("./index.html"))));
});
