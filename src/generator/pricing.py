"""
Génération de la grille tarifaire (ADR-0003).
"""
from typing import Any


def generate_pricing_grid() -> list[dict[str, Any]]:
    """
    Retourne la grille tarifaire standard par catégorie client et palier de quantité.
    """
    grid = [
        # Détaillants
        {"categorie_client": "detaillant", "palier_min": 1, "palier_max": 9, "remise_pct": 0.0},
        {"categorie_client": "detaillant", "palier_min": 10, "palier_max": 49, "remise_pct": 1.5},
        {"categorie_client": "detaillant", "palier_min": 50, "palier_max": None, "remise_pct": 3.0},

        # Restaurants / Maquis / Bars
        {"categorie_client": "restaurant", "palier_min": 1, "palier_max": 9, "remise_pct": 1.0},
        {"categorie_client": "restaurant", "palier_min": 10, "palier_max": 49, "remise_pct": 2.5},
        {"categorie_client": "restaurant", "palier_min": 50, "palier_max": None, "remise_pct": 4.5},

        # Revendeurs / Supérettes
        {"categorie_client": "revendeur", "palier_min": 1, "palier_max": 9, "remise_pct": 2.0},
        {"categorie_client": "revendeur", "palier_min": 10, "palier_max": 49, "remise_pct": 4.0},
        {"categorie_client": "revendeur", "palier_min": 50, "palier_max": None, "remise_pct": 6.0},

        # PME / Collectivités
        {"categorie_client": "pme", "palier_min": 1, "palier_max": 9, "remise_pct": 2.5},
        {"categorie_client": "pme", "palier_min": 10, "palier_max": 49, "remise_pct": 4.5},
        {"categorie_client": "pme", "palier_min": 50, "palier_max": None, "remise_pct": 7.0},
    ]
    return grid
