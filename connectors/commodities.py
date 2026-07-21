"""
Connecteur Matières Premières — focus sur celles clés pour l'Afrique de l'Ouest.
Le cacao et le coton sont cruciaux : la Côte d'Ivoire est 1er producteur mondial de cacao.
Mode simulation : valeurs réalistes 2026 (cacao très volatil ~5000 USD/t, Brent ~85 USD).
"""
import random
from .base import BaseConnector

# (symbole, nom, valeur de référence, unité, volatilité %, note West Africa)
_COMMODITIES = [
    ("COCOA", "Cacao", 5300, "USD/tonne", 4.5, "🇨🇮 Côte d'Ivoire 1er producteur mondial (~40%)"),
    ("COTTON", "Coton", 0.72, "USD/livre", 2.5, "Culture clé zone CFA (Bénin, Mali, Burkina)"),
    ("GOLD", "Or", 3990, "USD/once", 1.5, "Mali, Burkina, Ghana : gros producteurs"),
    ("BRENT", "Pétrole Brent", 85, "USD/baril", 3.0, "Nigeria, Angola exportateurs"),
    ("COFFEE", "Café Robusta", 4100, "USD/tonne", 3.5, "Côte d'Ivoire, Ouganda producteurs"),
    ("RUBBER", "Caoutchouc", 1.85, "USD/kg", 2.8, "Côte d'Ivoire 1er producteur africain"),
    ("CASHEW", "Noix de cajou", 1250, "USD/tonne", 2.2, "Côte d'Ivoire 1er exportateur mondial brut"),
    ("PALM", "Huile de palme", 1050, "USD/tonne", 2.6, "Culture importante Afrique de l'Ouest"),
]


class CommoditiesConnector(BaseConnector):
    name = "commodities"

    def _fetch_simulated(self, **kwargs) -> dict:
        items = []
        for sym, nom, ref, unite, vol, note in _COMMODITIES:
            var = round(random.uniform(-vol, vol), 2)
            items.append({
                "symbole": sym, "nom": nom,
                "prix": round(ref * (1 + var / 100), 3 if ref < 10 else 2),
                "variation_jour": var, "unite": unite,
                "pertinence_afrique": note,
            })
        return {
            "matieres": items,
            "note": "Matières premières — données simulées réalistes, focus Afrique de l'Ouest.",
        }

    def _fetch_live(self, **kwargs) -> dict:
        raise NotImplementedError("Connecteur matières premières live non branché.")
