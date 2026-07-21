// ═══ Service Worker GUELANE — mise à jour au prochain démarrage ═══
// Stratégie "réseau d'abord" : l'app cherche TOUJOURS la dernière version en ligne,
// et ne se rabat sur le cache que si Internet est absent.
// Une nouvelle version s'installe en arrière-plan et s'active au PROCHAIN lancement
// de l'application — jamais pendant que l'utilisateur s'en sert.

const CACHE_VERSION = 'guelane-v1.1';   // ← CHANGE ce numéro à chaque déploiement important
const CACHE_NAME = CACHE_VERSION;

// Installation : la nouvelle version s'installe mais N'ÉCRASE PAS tout de suite l'ancienne.
// Elle "attend" que toutes les fenêtres de l'app soient fermées (prochain démarrage).
self.addEventListener('install', function(event) {
  // Pas de skipWaiting() : on laisse la version actuelle finir tranquillement.
});

// Activation : se déclenche au prochain démarrage, quand l'ancienne version n'est plus utilisée.
// On nettoie alors les anciens caches.
self.addEventListener('activate', function(event) {
  event.waitUntil(
    caches.keys().then(function(names) {
      return Promise.all(
        names.filter(function(n) { return n !== CACHE_NAME; })
             .map(function(n) { return caches.delete(n); })
      );
    }).then(function() {
      return self.clients.claim();
    })
  );
});

// Récupération : réseau d'abord, cache en secours (hors ligne)
self.addEventListener('fetch', function(event) {
  if (event.request.method !== 'GET') return;
  event.respondWith(
    fetch(event.request).then(function(response) {
      if (response && response.status === 200 && event.request.url.startsWith('http')) {
        var copy = response.clone();
        caches.open(CACHE_NAME).then(function(cache) {
          cache.put(event.request, copy);
        });
      }
      return response;
    }).catch(function() {
      return caches.match(event.request);
    })
  );
});
