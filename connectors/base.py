"""
Interface commune à tous les connecteurs PROPHET.

Principe : chaque connecteur (BRVM, Wave, Orange Money…) hérite de BaseConnector.
Tant que la vraie API n'est pas branchée, `simulation = True` et le connecteur
renvoie des données simulées réalistes. Le jour où tu obtiens tes clés, tu passes
`simulation = False` et tu implémentes la méthode `_fetch_live()`. Le reste du code
(endpoints, modules PROPHET) ne change pas.
"""
from abc import ABC, abstractmethod
from datetime import datetime


class BaseConnector(ABC):
    name: str = "base"

    def __init__(self, simulation: bool = True, api_key: str | None = None):
        self.simulation = simulation
        self.api_key = api_key

    @abstractmethod
    def _fetch_simulated(self, **kwargs) -> dict:
        """Données simulées réalistes (toujours implémenté)."""
        ...

    def _fetch_live(self, **kwargs) -> dict:
        """Vrai appel API — à implémenter le jour où la clé est disponible."""
        raise NotImplementedError(
            f"Le connecteur '{self.name}' n'est pas encore branché sur l'API réelle. "
            f"Passez simulation=False et implémentez _fetch_live()."
        )

    def fetch(self, **kwargs) -> dict:
        """Point d'entrée unique. Choisit simulé ou live selon le mode."""
        payload = self._fetch_simulated(**kwargs) if self.simulation else self._fetch_live(**kwargs)
        return {
            "connector": self.name,
            "mode": "simulation" if self.simulation else "live",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "data": payload,
        }
