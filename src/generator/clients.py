"""
Génération des 300 clients et de leurs catégories.
"""
import random
from typing import Any
from src.generator.catalog import STORE_LOCATIONS


CLIENT_CATEGORIES = {
    "detaillant": 0.50,    # 150 clients
    "restaurant": 0.25,    # 75 clients
    "revendeur": 0.15,     # 45 clients
    "pme": 0.10,           # 30 clients
}

NAMES_DETAILLANT = [
    "Boutique Sainte Rita", "Alimentation Mawuena", "Ets La Benediction", "Boutique Le Salut",
    "Boutique El-Shaddai", "Alimentation Divine Grace", "Ets Koffi & Freres", "Boutique Adawlato Star",
    "Ets Dieu Merci", "Alimentation Kpota", "Boutique La Paix", "Ets Espoir Plus", "Boutique Akofa",
    "Alimentation Chez Maman Akossiwa", "Boutique Sika", "Ets Fofo & Soeur", "Boutique Amen",
    "Alimentation Enyonam", "Ets Assiyeye Commerce", "Boutique Mawulolo", "Boutique Le Tresor",
]

NAMES_RESTAURANT = [
    "Maquis Le Palmier", "Bar-Resto Le Refuge", "Restaurant Saveurs Locales", "Maquis Le Boulevard",
    "Terrasse Chez Da-Koko", "Bar Dancing Le Flamboyant", "Cafeteria La Bonne Soupe", "Maquis 33 Export",
    "Resto Bar Akwaba", "Maquis Escale Gourmande", "Bar Le Rond-Point", "Restaurant O-Marche",
    "Maquis Le Relais des Amis", "Terrasse Blue Lagoon", "Bar Resto La Detente", "Cafet Le Manguier",
]

NAMES_REVENDEUR = [
    "Superette Pax", "Alimentation Generale Le Bon Choix", "Superette Bel Air", "Commerce General Express",
    "Superette La Providence", "Alimentation Proxi", "Supermarche Espace Frais", "Ets Agoro Distribution",
    "Alimentation Nyekonakpoe", "Superette Concorde", "Ets Central Market", "Distribution Moderne",
]

NAMES_PME = [
    "Hotel Bel Azur", "Cantine College Saint-Joseph", "Societe de Services", "Hotel Le Pelican",
    "Residence Les Cocotiers", "Clinique Internationale Esperance (Restauration)", "Complexe Scolaire La Sagesse",
    "Entreprise BTP Bat-Services (Base-vie)", "Hotel Palm Beach", "Centre Hospitalier Sainte-Monique",
]


def generate_clients(seed: int = 42, target_count: int = 300) -> list[dict[str, Any]]:
    """Génère 300 clients."""
    rng = random.Random(seed)
    clients: list[dict[str, Any]] = []

    category_targets = {
        "detaillant": int(target_count * CLIENT_CATEGORIES["detaillant"]),
        "restaurant": int(target_count * CLIENT_CATEGORIES["restaurant"]),
        "revendeur": int(target_count * CLIENT_CATEGORIES["revendeur"]),
        "pme": int(target_count * CLIENT_CATEGORIES["pme"]),
    }
    # Correction d'éventuels arrondis
    diff = target_count - sum(category_targets.values())
    category_targets["detaillant"] += diff

    client_id_counter = 1

    name_pools = {
        "detaillant": NAMES_DETAILLANT,
        "restaurant": NAMES_RESTAURANT,
        "revendeur": NAMES_REVENDEUR,
        "pme": NAMES_PME,
    }

    for cat, count in category_targets.items():
        pool = name_pools[cat]
        for i in range(count):
            base_name = pool[i % len(pool)]
            cycle = (i // len(pool)) + 1
            ville, quartier = rng.choice(STORE_LOCATIONS)

            if cycle > 1:
                raison_sociale = f"{base_name} {cycle} ({quartier})"
            else:
                raison_sociale = f"{base_name} ({quartier})"

            client_id = f"CLI-{client_id_counter:04d}"
            clients.append({
                "client_id": client_id,
                "raison_sociale": raison_sociale,
                "categorie": cat,
                "ville": ville,
                "quartier": quartier,
                "date_effet": "2024-01-01",
            })
            client_id_counter += 1

    # Mélanger de façon stable pour une distribution homogène
    rng.shuffle(clients)
    return clients
