"""
Connecteur Indices Africains — principales bourses du continent.
Mode simulation : valeurs réalistes 2026.
Pour le temps réel : brancher un provider comme African Markets, ou les APIs des bourses.
"""
import random
from .base import BaseConnector

# (symbole, nom, pays, valeur de référence, devise locale)
_AFRICAN_INDICES = [
    ("JSE-ALSI", "JSE All Share", "Afrique du Sud", 92500, "ZAR"),
    ("NGX-ASI", "NGX All-Share", "Nigeria", 105800, "NGN"),
    ("GSE-CI", "GSE Composite", "Ghana", 4980, "GHS"),
    ("EGX30", "EGX 30", "Égypte", 31200, "EGP"),
    ("NSE20", "Nairobi NSE 20", "Kenya", 2140, "KES"),
    ("MASI", "MASI Casablanca", "Maroc", 16800, "MAD"),
    ("BRVMC", "BRVM Composite", "UEMOA", 285, "FCFA"),
    ("SEMDEX", "SEMDEX Maurice", "Maurice", 2650, "MUR"),
]


class AfricanIndicesConnector(BaseConnector):
    name = "african_indices"

    def _fetch_simulated(self, **kwargs) -> dict:
        indices = []
        for sym, nom, pays, ref, dev in _AFRICAN_INDICES:
            var = round(random.uniform(-2.2, 2.5), 2)
            indices.append({
                "symbole": sym, "nom": nom, "pays": pays,
                "valeur": round(ref * (1 + var / 100), 2),
                "variation_jour": var, "devise": dev,
            })
        return {
            "indices": indices,
            "note": "Indices boursiers africains — données simulées réalistes.",
        }

    def _fetch_live(self, **kwargs) -> dict:
        raise NotImplementedError("Connecteur indices africains live non branché.")
