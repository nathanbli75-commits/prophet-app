"""
Actualités financières réelles pour GUELANE via NewsData.io.

Pour activer : obtenir une clé gratuite sur https://newsdata.io et la mettre dans .env :
  NEWSDATA_API_KEY=pub_xxxxxxxxxxxx

Sans clé, l'endpoint renvoie configured=false et le frontend garde son affichage existant.

Plan gratuit : 200 requêtes/jour, actualités avec ~12h de décalage, usage commercial autorisé.
On met en cache les résultats pour économiser les crédits (rafraîchi toutes les 30 min).
"""
import os
import json
import time
import urllib.request
import urllib.parse

NEWSDATA_API_KEY = os.environ.get("NEWSDATA_API_KEY", "")
NEWSDATA_URL = "https://newsdata.io/api/1/latest"

# Cache simple en mémoire pour économiser les crédits API
_cache = {"data": None, "ts": 0}
_CACHE_TTL = 1800  # 30 minutes


def is_configured() -> bool:
    return bool(NEWSDATA_API_KEY)


def fetch_news(query: str = "finance OR bourse OR BRVM OR économie", force: bool = False) -> dict:
    """
    Récupère les actualités financières et économiques d'Afrique de l'Ouest francophone.
    Combine plusieurs requêtes pour maximiser le volume. Cache 30 min.
    """
    if not NEWSDATA_API_KEY:
        return {"configured": False, "mode": "non configuré", "articles": []}

    now = time.time()
    if not force and _cache["data"] and (now - _cache["ts"] < _CACHE_TTL):
        return _cache["data"]

    # Pays d'Afrique de l'Ouest francophone (max 5 par requête en plan gratuit)
    # On fait 2 requêtes pour couvrir plus de pays et plus de sujets.
    requetes = [
        {
            "q": "finance OR bourse OR BRVM OR économie OR banque OR investissement OR UEMOA",
            "country": "ci,sn,ml,bf,bj",
            "language": "fr",
        },
        {
            "q": "entreprise OR marché OR fintech OR mobile money OR croissance OR PME OR startup",
            "country": "ci,sn,tg,ne,gn",  # + Togo, Niger, Guinée
            "language": "fr",
        },
    ]

    articles = []
    seen_titres = set()
    erreurs = 0

    for params in requetes:
        params["apikey"] = NEWSDATA_API_KEY
        url = NEWSDATA_URL + "?" + urllib.parse.urlencode(params)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "GUELANE/1.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                raw = json.loads(resp.read().decode("utf-8"))
        except Exception:
            erreurs += 1
            continue
        for a in raw.get("results", []):
            titre = a.get("title", "")
            if not titre or titre in seen_titres:
                continue
            seen_titres.add(titre)
            articles.append({
                "titre": titre,
                "description": a.get("description", "") or "",
                "source": a.get("source_id", "") or a.get("source_name", ""),
                "date": a.get("pubDate", ""),
                "lien": a.get("link", ""),
                "image": a.get("image_url", "") or "",
                "categorie": (a.get("category") or ["business"])[0] if a.get("category") else "business",
            })

    # Si les deux requêtes échouent, renvoyer le cache existant ou une erreur douce
    if erreurs == len(requetes):
        if _cache["data"]:
            return _cache["data"]
        return {"configured": True, "mode": "erreur", "articles": []}

    result = {"configured": True, "mode": "live (NewsData.io)", "articles": articles[:30]}
    _cache["data"] = result
    _cache["ts"] = now
    return result
