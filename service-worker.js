// ═══ Service Worker GUELANE ═══
//
// Objectif : l'application s'ouvre INSTANTANÉMENT, et la nouvelle
// version se télécharge en arrière-plan sans faire attendre.
//
// Pourquoi ce changement : la version précédente attendait le réseau
// pour CHAQUE fichier, sans limite de temps. Sur une connexion mobile
// lente, l'ouverture traînait et l'écran « pas de connexion » pouvait
// s'afficher alors que la connexion était bonne — la requête n'avait
// simplement pas encore répondu.

const CACHE_VERSION = 'guelane-v3.97';   // ← CHANGE ce numéro à chaque déploiement
const CACHE_NAME = CACHE_VERSION;

// Au-delà de ce délai, on sert la version en cache plutôt que d'attendre.
const DELAI_RESEAU = 4000;   // 4 secondes

// Installation : la nouvelle version prend la main tout de suite
self.addEventListener('install', function(event) {
  self.skipWaiting();
});

// Activation : on efface tous les anciens caches (aucun mélange de versions)
self.addEventListener('activate', function(event) {
  event.waitUntil(
    caches.keys().then(function(names) {
      return Promise.all(names.map(function(n) {
        if (n !== CACHE_NAME) return caches.delete(n);
      }));
    }).then(function() {
      return self.clients.claim();
    })
  );
});

// Course entre le réseau et le délai : on ne bloque jamais indéfiniment
function reseauAvecDelai(request) {
  return new Promise(function(resolve, reject) {
    var fini = false;
    var minuteur = setTimeout(function() {
      if (!fini) { fini = true; reject(new Error('delai')); }
    }, DELAI_RESEAU);

    fetch(request).then(function(rep) {
      if (fini) return;
      fini = true; clearTimeout(minuteur); resolve(rep);
    }).catch(function(e) {
      if (fini) return;
      fini = true; clearTimeout(minuteur); reject(e);
    });
  });
}

function mettreEnCache(request, response) {
  if (!response || response.status !== 200 || response.type === 'opaque') return;
  var copie = response.clone();
  caches.open(CACHE_NAME).then(function(cache) {
    cache.put(request, copie).catch(function(){});
  });
}

self.addEventListener('fetch', function(event) {
  if (event.request.method !== 'GET') return;
  var url = event.request.url;
  if (!url.startsWith('http')) return;

  // Les appels au backend ne passent jamais par le cache
  if (url.indexOf('/api/') !== -1 || url.indexOf('railway.app') !== -1) return;

  var estPage = event.request.mode === 'navigate'
             || (event.request.headers.get('accept') || '').indexOf('text/html') !== -1;

  if (estPage) {
    // ── PAGE : réseau d'abord, mais avec un délai maximum ──
    event.respondWith(
      reseauAvecDelai(event.request).then(function(rep) {
        mettreEnCache(event.request, rep);
        return rep;
      }).catch(function() {
        return caches.match(event.request).then(function(c) {
          return c || caches.match('./index.html') || Response.error();
        });
      })
    );
    return;
  }

  // ── AUTRES FICHIERS : cache d'abord, rafraîchi en arrière-plan ──
  event.respondWith(
    caches.match(event.request).then(function(enCache) {
      var reseau = fetch(event.request).then(function(rep) {
        mettreEnCache(event.request, rep);
        return rep;
      }).catch(function() {
        return enCache;
      });
      return enCache || reseau;
    })
  );
});

// Permet à la page de demander l'activation immédiate d'une mise à jour
self.addEventListener('message', function(event) {
  if (event.data === 'SKIP_WAITING') self.skipWaiting();
});
