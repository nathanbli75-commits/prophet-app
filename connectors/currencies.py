"""
Connecteur Devises — taux de change centrés sur le FCFA.
Rappel important : le FCFA (XOF) est arrimé à l'euro à taux FIXE.
  1 EUR = 655,957 FCFA (parité fixe garantie par le Trésor français).
Donc EUR/FCFA ne varie pas. En revanche USD/FCFA varie selon EUR/USD.
Mode simulation : EUR/USD réaliste (~1.14), les autres paires en découlent.
"""
import random
from .base import BaseConnector

# Parité fixe officielle
FCFA_PER_EUR = 655.957


class CurrenciesConnector(BaseConnector):
    name = "currencies"

    def _fetch_simulated(self, **kwargs) -> dict:
        # EUR/USD fluctue de façon réaliste autour de 1.14
        eur_usd = round(random.uniform(1.12, 1.16), 4)
        var_eurusd = round(random.uniform(-0.6, 0.6), 2)
        # USD/FCFA en découle (parité EUR/FCFA fixe)
        usd_fcfa = round(FCFA_PER_EUR / eur_usd, 2)

        # Quelques devises régionales/africaines vs USD (indicatif)
        pairs = [
            {"paire": "EUR/FCFA", "taux": FCFA_PER_EUR, "variation_jour": 0.0,
             "note": "Parité FIXE garantie"},
            {"paire": "USD/FCFA", "taux": usd_fcfa, "variation_jour": round(-var_eurusd, 2),
             "note": "Varie selon EUR/USD"},
            {"paire": "EUR/USD", "taux": eur_usd, "variation_jour": var_eurusd,
             "note": "Paire de référence mondiale"},
            {"paire": "GBP/FCFA", "taux": round(usd_fcfa * random.uniform(1.24, 1.28), 2),
             "variation_jour": round(random.uniform(-0.7, 0.7), 2), "note": ""},
            {"paire": "USD/NGN", "taux": round(random.uniform(1480, 1560), 1),
             "variation_jour": round(random.uniform(-1.5, 1.5), 2), "note": "Naira nigérian"},
            {"paire": "USD/GHS", "taux": round(random.uniform(14.5, 15.8), 2),
             "variation_jour": round(random.uniform(-1.2, 1.2), 2), "note": "Cedi ghanéen"},
            {"paire": "USD/ZAR", "taux": round(random.uniform(17.8, 18.9), 2),
             "variation_jour": round(random.uniform(-1.0, 1.0), 2), "note": "Rand sud-africain"},
        ]
        return {
            "paires": pairs,
            "parite_fixe_eur_fcfa": FCFA_PER_EUR,
            "note": "Devises — EUR/FCFA fixe, autres paires simulées de façon réaliste.",
        }

    def _fetch_live(self, **kwargs) -> dict:
        raise NotImplementedError("Connecteur devises live non branché.")
