// Service Worker PROPHET — permet l'installation en tant qu'application
// PROPHET a besoin d'Internet (les analyses passent par le backend),
// donc on garde une stratégie "réseau d'abord" simple, sans cache agressif.

const CACHE_NAME = 'prophet-v1';

self.addEventListener('install', function(event) {
  self.skipWaiting();
});

self.addEventListener('activate', function(event) {
  // Nettoyer les anciens caches
  event.waitUntil(
    caches.keys().then(function(names) {
      return Promise.all(
        names.filter(function(n) { return n !== CACHE_NAME; })
             .map(function(n) { return caches.delete(n); })
      );
    })
  );
  self.clients.claim();
});

self.addEventListener('fetch', function(event) {
  // Réseau d'abord : PROPHET fonctionne en ligne.
  // On ne met en cache que la page d'accueil pour un affichage rapide.
  event.respondWith(
    fetch(event.request).catch(function() {
      return caches.match(event.request);
    })
  );
});
