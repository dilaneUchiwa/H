/**
 * Service worker de la coquille PWA : met en cache les fichiers statiques
 * de l'application (pas les données santé, gérées par sync.js/IndexedDB)
 * pour que l'écran reste utilisable même sans liaison serveur.
 */

const CACHE_COQUILLE = "sihl-shell-v1";
const FICHIERS_COQUILLE = [
    "/",
    "/static/css/app.css",
    "/static/js/app.js",
    "/static/js/sync.js",
    "/static/js/vendor/vue.global.prod.js",
    "/static/manifest.webmanifest",
];

self.addEventListener("install", (event) => {
    event.waitUntil(
        caches.open(CACHE_COQUILLE).then((cache) => cache.addAll(FICHIERS_COQUILLE))
    );
    self.skipWaiting();
});

self.addEventListener("activate", (event) => {
    event.waitUntil(
        caches.keys().then((cles) =>
            Promise.all(cles.filter((c) => c !== CACHE_COQUILLE).map((c) => caches.delete(c)))
        )
    );
});

self.addEventListener("fetch", (event) => {
    if (event.request.method !== "GET") return;
    if (event.request.url.includes("/api/")) return; // Les données passent par sync.js.

    event.respondWith(
        caches.match(event.request).then((reponse) => reponse || fetch(event.request))
    );
});
