// ═══ Service Worker GUELANE — mises à jour propres et automatiques ═══
// Objectif : chaque nouvelle version REMPLACE TOTALEMENT l'ancienne,
// sans jamais mélanger les versions, et sans que l'utilisateur ait à
// désinstaller/réinstaller quoi que ce soit.

const CACHE_VERSION = 'guelane-v3.21';   // ← CHANGE ce numéro à chaque déploiement
const CACHE_NAME = CACHE_VERSION;

// À l'installation d'une nouvelle version : on l'active tout de suite
self.addEventListener('install', function(event) {
  self.skipWaiting();
});

// À l'activation : on EFFACE TOUS les anciens caches (aucun mélange possible)
self.addEventListener('activate', function(event) {
  event.waitUntil(
    caches.keys().then(function(names) {
      // Supprimer absolument tous les caches qui ne sont pas la version actuelle
      return Promise.all(
        names.map(function(n) {
          if (n !== CACHE_NAME) return caches.delete(n);
        })
      );
    }).then(function() {
      return self.clients.claim();
    })
  );
});

// Stratégie réseau : on privilégie TOUJOURS la version fraîche du serveur.
// Le cache ne sert QUE de secours quand il n'y a pas de connexion.
self.addEventListener('fetch', function(event) {
  if (event.request.method !== 'GET') return;
  var url = event.request.url;
  if (!url.startsWith('http')) return;

  // Les appels au backend (API) ne sont jamais mis en cache
  if (url.indexOf('/api/') !== -1 || url.indexOf('railway.app') !== -1) return;

  // RÉSEAU D'ABORD : on charge la version fraîche, cache en secours hors ligne
  event.respondWith(
    fetch(event.request).then(function(response) {
      // Mettre à jour le cache avec la version fraîche (pour le hors ligne)
      if (response && response.status === 200) {
        var copy = response.clone();
        caches.open(CACHE_NAME).then(function(cache) {
          cache.put(event.request, copy);
        });
      }
      return response;
    }).catch(function() {
      // Pas de réseau : servir depuis le cache
      return caches.match(event.request);
    })
  );
});
