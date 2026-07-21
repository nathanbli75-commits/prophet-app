"""
Connecteur Indices Mondiaux — grandes places boursières internationales.
Mode simulation : valeurs réalistes 2026.
Pour le temps réel : brancher un provider comme Alpha Vantage, Twelve Data, Finnhub…
"""
import random
from .base import BaseConnector

# (symbole, nom, région, valeur de référence, devise)
_GLOBAL_INDICES = [
    ("SPX", "S&P 500", "États-Unis", 6250, "USD"),
    ("NDX", "Nasdaq 100", "États-Unis", 22800, "USD"),
    ("DJI", "Dow Jones", "États-Unis", 44200, "USD"),
    ("CAC40", "CAC 40", "France", 7950, "EUR"),
    ("FTSE", "FTSE 100", "Royaume-Uni", 8420, "GBP"),
    ("DAX", "DAX 40", "Allemagne", 19800, "EUR"),
    ("N225", "Nikkei 225", "Japon", 40100, "JPY"),
    ("SSEC", "Shanghai Composite", "Chine", 3380, "CNY"),
]


class GlobalIndicesConnector(BaseConnector):
    name = "global_indices"

    def _fetch_simulated(self, **kwargs) -> dict:
        indices = []
        for sym, nom, region, ref, dev in _GLOBAL_INDICES:
            var = round(random.uniform(-1.8, 1.9), 2)
            indices.append({
                "symbole": sym, "nom": nom, "region": region,
                "valeur": round(ref * (1 + var / 100), 2),
                "variation_jour": var, "devise": dev,
            })
        return {
            "indices": indices,
            "note": "Indices boursiers mondiaux — données simulées réalistes.",
        }

    def _fetch_live(self, **kwargs) -> dict:
        raise NotImplementedError("Connecteur indices mondiaux live non branché.")
