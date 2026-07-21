// ═══ Service Worker GUELANE — version sécurisée anti-écran-blanc ═══
// RÈGLE D'OR : on ne met JAMAIS en cache la page HTML principale.
// Elle est TOUJOURS chargée fraîche depuis le réseau, ce qui évite tout
// risque d'écran blanc dû à une version cassée en cache.
// Le cache ne sert qu'aux icônes et petites ressources, uniquement en secours hors ligne.

const CACHE_VERSION = 'guelane-v1.4';   // ← CHANGE ce numéro à chaque déploiement important
const CACHE_NAME = CACHE_VERSION;

// Installation : activation immédiate de cette version saine
self.addEventListener('install', function(event) {
  self.skipWaiting();
});

// Activation : on supprime TOUS les anciens caches (nettoyage complet)
self.addEventListener('activate', function(event) {
  event.waitUntil(
    caches.keys().then(function(names) {
      return Promise.all(names.map(function(n) { return caches.delete(n); }));
    }).then(function() {
      return self.clients.claim();
    })
  );
});

// Récupération
self.addEventListener('fetch', function(event) {
  if (event.request.method !== 'GET') return;

  var url = event.request.url;
  var isHTML = event.request.mode === 'navigate' ||
               event.request.destination === 'document' ||
               url.endsWith('/') || url.endsWith('index.html');

  // Pour la PAGE HTML : réseau uniquement (jamais de cache) → jamais d'écran blanc
  if (isHTML) {
    event.respondWith(
      fetch(event.request).catch(function() {
        // Si vraiment hors ligne, on tente une éventuelle copie, sinon message simple
        return caches.match(event.request).then(function(cached){
          return cached || new Response(
            '<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head><body style="font-family:sans-serif;background:#0a2050;color:#fff;display:flex;align-items:center;justify-content:center;height:100vh;margin:0;text-align:center;padding:20px;"><div><h2>Pas de connexion</h2><p>GUELANE a besoin d\'Internet. Reconnectez-vous et rouvrez l\'application.</p></div></body></html>',
            { headers: { 'Content-Type': 'text/html; charset=utf-8' } }
          );
        });
      })
    );
    return;
  }

  // Pour les autres ressources (icônes...) : réseau d'abord, cache en secours
  event.respondWith(
    fetch(event.request).then(function(response) {
      if (response && response.status === 200 && url.startsWith('http')) {
        var copy = response.clone();
        caches.open(CACHE_NAME).then(function(cache) { cache.put(event.request, copy); });
      }
      return response;
    }).catch(function() {
      return caches.match(event.request);
    })
  );
});
