"""
Connecteur BRVM (Bourse Régionale des Valeurs Mobilières — UEMOA).

Mode simulation : données réalistes basées sur la structure réelle de la BRVM
(Sonatel ~20% de la capitalisation, télécoms + finance dominants, ~47 sociétés).

Pour passer en live plus tard :
  1. Obtenir un accès (ex: Orishas Finance API, ou data provider BRVM)
  2. Mettre BRVM_SIMULATION=false dans .env
  3. Implémenter _fetch_live() avec le vrai appel HTTP
"""
import random
from .base import BaseConnector


# Sociétés cotées réelles (symbole, nom, secteur, cours de référence en FCFA)
# Cours indicatifs proches de la réalité 2025-2026, servent de base à la simulation.
_BRVM_STOCKS = [
    ("SNTS", "Sonatel Sénégal", "Télécoms", 25100),
    ("ORAC", "Orange Côte d'Ivoire", "Télécoms", 14200),
    ("SGBC", "Société Générale CI", "Finance", 24500),
    ("ETIT", "Ecobank Transnational", "Finance", 22),
    ("BOAB", "Bank of Africa Bénin", "Finance", 8780),
    ("BICC", "BICICI", "Finance", 28970),
    ("NSBC", "NSIA Banque CI", "Finance", 12500),
    ("CBIBF", "Coris Bank", "Finance", 11800),
    ("SIBC", "Société Ivoirienne de Banque", "Finance", 9400),
    ("PALC", "Palmci", "Agro-industrie", 6900),
    ("SPHC", "Saph", "Agro-industrie", 4150),
    ("SOGC", "Sogb", "Agro-industrie", 5600),
    ("NTLC", "Nestlé Côte d'Ivoire", "Agroalimentaire", 7200),
    ("SLBC", "Solibra", "Agroalimentaire", 128000),
    ("CFAC", "CFAO Motors CI", "Distribution", 720),
    ("TTLC", "Total Énergies CI", "Énergie", 3100),
    ("SHEC", "Vivo Energy CI", "Énergie", 1250),
    ("ABJC", "Servair Abidjan", "Services", 2900),
    ("SDSC", "Sodé Ci (Eaux)", "Utilities", 42000),
    ("CIEC", "CIE (Électricité)", "Utilities", 2600),
]

_BRVM_INDICES = [
    ("BRVM Composite", 285.40),
    ("BRVM 30", 142.80),
    ("BRVM Prestige", 118.20),
    ("BRVM Principal", 96.50),
]


class BRVMConnector(BaseConnector):
    name = "brvm"

    def _rand_var(self) -> float:
        """Variation journalière réaliste (-3% à +3%, biais léger)."""
        return round(random.uniform(-3.0, 3.2), 2)

    def _fetch_simulated(self, symbol: str | None = None, **kwargs) -> dict:
        # Cotation d'un titre précis
        if symbol:
            symbol = symbol.upper()
            match = next((s for s in _BRVM_STOCKS if s[0] == symbol), None)
            if not match:
                return {"error": f"Symbole '{symbol}' introuvable à la BRVM."}
            sym, nom, secteur, ref = match
            var = self._rand_var()
            cours = round(ref * (1 + var / 100), 2)
            return {
                "symbole": sym, "nom": nom, "secteur": secteur,
                "cours": cours, "cours_reference": ref,
                "variation_jour": var,
                "volume": random.randint(500, 50000),
                "devise": "FCFA",
            }

        # Vue marché complète : indices + top titres
        indices = [
            {"nom": n, "valeur": round(v * (1 + self._rand_var() / 100), 2),
             "variation": self._rand_var()}
            for n, v in _BRVM_INDICES
        ]
        stocks = []
        for sym, nom, secteur, ref in _BRVM_STOCKS:
            var = self._rand_var()
            stocks.append({
                "symbole": sym, "nom": nom, "secteur": secteur,
                "cours": round(ref * (1 + var / 100), 2),
                "variation_jour": var,
                "volume": random.randint(500, 50000),
            })
        # Trier par volume décroissant (les plus liquides en tête, Sonatel domine)
        stocks.sort(key=lambda s: s["volume"], reverse=True)
        gainers = sorted(stocks, key=lambda s: s["variation_jour"], reverse=True)[:5]
        losers = sorted(stocks, key=lambda s: s["variation_jour"])[:5]
        return {
            "indices": indices,
            "titres": stocks,
            "top_hausses": gainers,
            "top_baisses": losers,
            "nb_societes": len(_BRVM_STOCKS),
            "devise": "FCFA",
            "note": "Données simulées réalistes — brancher Orishas Finance pour le temps réel.",
        }

    def _fetch_live(self, symbol: str | None = None, **kwargs) -> dict:
        """
        À IMPLÉMENTER quand tu auras l'accès API (ex: Orishas Finance).
        Exemple de structure attendue :

            import httpx
            headers = {"Authorization": f"Bearer {self.api_key}"}
            url = f"https://api.orishas.finance/v1/brvm/quote"
            params = {"symbol": symbol} if symbol else {}
            r = httpx.get(url, headers=headers, params=params, timeout=10)
            r.raise_for_status()
            return r.json()

        Il suffit de mapper la réponse réelle vers le même format que _fetch_simulated.
        """
        raise NotImplementedError(
            "Connecteur BRVM live non branché. Obtenez un accès Orishas Finance, "
            "mettez BRVM_SIMULATION=false, et implémentez cette méthode."
        )
