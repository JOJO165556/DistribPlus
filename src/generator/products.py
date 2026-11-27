"""
Génération des 500 produits référentiels et des correspondances externes.
Garantit la reproductibilité via un seed fixe (ENF-13).
"""
import random
from typing import Any
from src.generator.catalog import CATEGORIES, PRODUCT_TEMPLATES


def generate_products(seed: int = 42, target_count: int = 500) -> list[dict[str, Any]]:
    """Génère target_count produits répartis de façon équilibrée sur les 12 catégories."""
    rng = random.Random(seed)
    products: list[dict[str, Any]] = []

    per_category = target_count // len(CATEGORIES)
    remainder = target_count % len(CATEGORIES)

    prod_idx = 1
    for cat_i, category in enumerate(CATEGORIES):
        count = per_category + (1 if cat_i < remainder else 0)
        templates = PRODUCT_TEMPLATES.get(category, [])

        for i in range(count):
            tpl = templates[i % len(templates)]
            variant_suffix = ""
            if i >= len(templates):
                v_num = (i // len(templates)) + 1
                variant_suffix = f" Var.{v_num}"

            nom_base, unite, c_min, c_max, m_min, m_max = tpl
            libelle = f"{nom_base}{variant_suffix} ({unite})"

            # Coût standard arrondi à 50 FCFA près
            raw_cout = rng.randint(c_min, c_max)
            cout_std = int(round(raw_cout / 50.0) * 50)

            # Marge brute
            marge_pct = rng.uniform(m_min, m_max)
            # Prix de base = coût standard * (1 + marge), arrondi à 50 FCFA
            prix_base = int(round((cout_std * (1.0 + marge_pct)) / 50.0) * 50)

            # Date d'effet initiale pour le référentiel maître
            date_effet = "2024-01-01"

            product_id = f"PROD-{prod_idx:04d}"
            products.append({
                "produit_id": product_id,
                "libelle": libelle,
                "categorie": category,
                "cout_standard": cout_std,
                "prix_base": prix_base,
                "date_effet": date_effet,
                "unite": unite,
            })
            prod_idx += 1

    return products


def generate_product_mappings(
    products: list[dict[str, Any]],
    seed: int = 42,
    orphan_pct: float = 0.02,
) -> tuple[list[dict[str, str]], dict[str, dict[str, str]]]:
    """
    Génère la table ref.correspondances_produits pour les 3 sources :
    - caisse: P-00xxx
    - b2b: SKU-xxx-X
    - stock: ART-00xxx
    Environ orphan_pct (2%) des références n'ont pas de mapping valide (DEF-06 / RG-03).
    Retourne (lignes_correspondance, lookup_par_source).
    """
    rng = random.Random(seed)
    mappings: list[dict[str, str]] = []
    
    # lookup[source][produit_id] = ref_externe
    lookup_by_source: dict[str, dict[str, str]] = {
        "caisse": {},
        "b2b": {},
        "stock": {},
    }

    for idx, p in enumerate(products, start=1):
        pid = p["produit_id"]

        # Format Caisse (ex: P-00123)
        ref_caisse = f"P-{idx:05d}"
        lookup_by_source["caisse"][pid] = ref_caisse
        mappings.append({
            "type_entite": "PRODUIT",
            "source": "caisse",
            "reference_externe": ref_caisse,
            "entite_id": pid,
        })

        # Format B2B (ex: SKU-123-A)
        suffix = chr(ord('A') + (idx % 26))
        ref_b2b = f"SKU-{idx:03d}-{suffix}"
        lookup_by_source["b2b"][pid] = ref_b2b
        mappings.append({
            "type_entite": "PRODUIT",
            "source": "b2b",
            "reference_externe": ref_b2b,
            "entite_id": pid,
        })

        # Format Stock (ex: ART-00123)
        ref_stock = f"ART-{idx:05d}"
        lookup_by_source["stock"][pid] = ref_stock
        mappings.append({
            "type_entite": "PRODUIT",
            "source": "stock",
            "reference_externe": ref_stock,
            "entite_id": pid,
        })

    # Suppression volontaire de ~orphan_pct dans la table de correspondance
    # pour simuler le catalogue de défauts DEF-06 (RG-03 : référence inconnue dans le master)
    nb_to_remove = int(len(mappings) * orphan_pct)
    indices_to_remove = set(rng.sample(range(len(mappings)), nb_to_remove))

    filtered_mappings = [
        m for i, m in enumerate(mappings) if i not in indices_to_remove
    ]

    return filtered_mappings, lookup_by_source
