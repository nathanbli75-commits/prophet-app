// ═══ Service Worker GUELANE — RAPIDE et SÛR (stale-while-revalidate) ═══
// Objectif : chargement quasi instantané, tout en restant à jour et sans écran blanc.
//
// Principe :
//  1. On sert IMMÉDIATEMENT la version en cache (ultra rapide).
//  2. EN MÊME TEMPS, on télécharge la version fraîche en arrière-plan pour la prochaine fois.
//  3. Sécurité : si le cache est vide/corrompu, on charge depuis le réseau (pas d'écran blanc).

const CACHE_VERSION = 'guelane-v1.7';   // ← CHANGE ce numéro à chaque déploiement important
const CACHE_NAME = CACHE_VERSION;

// Ressources à mettre en cache dès l'installation (pour un démarrage instantané)
const CORE_ASSETS = [
  './',
  './index.html',
  './manifest.json',
  './icon-192.png',
  './icon-512.png',
  './icon-180.png'
];

// Installation : on pré-charge les ressources essentielles et on active tout de suite
self.addEventListener('install', function(event) {
  event.waitUntil(
    caches.open(CACHE_NAME).then(function(cache) {
      return cache.addAll(CORE_ASSETS).catch(function(){ /* ignore si une ressource manque */ });
    }).then(function(){ return self.skipWaiting(); })
  );
});

// Activation : on supprime les anciens caches et on prend le contrôle
self.addEventListener('activate', function(event) {
  event.waitUntil(
    caches.keys().then(function(names) {
      return Promise.all(
        names.filter(function(n){ return n !== CACHE_NAME; })
             .map(function(n){ return caches.delete(n); })
      );
    }).then(function(){ return self.clients.claim(); })
  );
});

// Récupération : STALE-WHILE-REVALIDATE (cache d'abord = rapide, MAJ en arrière-plan)
self.addEventListener('fetch', function(event) {
  if (event.request.method !== 'GET') return;
  var url = event.request.url;
  if (!url.startsWith('http')) return;

  // Ne pas mettre en cache les appels API vers le backend (toujours frais)
  if (url.indexOf('/api/') !== -1 || url.indexOf('railway.app') !== -1) {
    return; // laisser passer normalement vers le réseau
  }

  event.respondWith(
    caches.open(CACHE_NAME).then(function(cache) {
      return cache.match(event.request).then(function(cached) {
        // Télécharger la version fraîche en arrière-plan
        var fetchPromise = fetch(event.request).then(function(response) {
          if (response && response.status === 200) {
            cache.put(event.request, response.clone());
          }
          return response;
        }).catch(function() {
          return cached; // hors ligne : on garde le cache
        });
        // Servir le cache IMMÉDIATEMENT si disponible (rapide), sinon attendre le réseau
        return cached || fetchPromise;
      });
    })
  );
});
