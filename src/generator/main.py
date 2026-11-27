"""
Point d'entrée du générateur de données.
Génération déterministe des référentiels maîtres, du flux caisse et de la vérité terrain.
"""
import argparse
import csv
from pathlib import Path
import sys

from src.generator.products import generate_products, generate_product_mappings
from src.generator.clients import generate_clients
from src.generator.pricing import generate_pricing_grid
from src.generator.sales_caisse import generate_caisse_sales
from src.generator.defects import DefectRecorder


def write_csv(path: Path, rows: list[dict], fieldnames: list[str], delimiter: str = ",") -> None:
    """Écrit un fichier CSV de manière déterministe avec encodage UTF-8."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=delimiter)
        writer.writeheader()
        writer.writerows(rows)


def run_generator(
    seed: int = 42,
    nb_days: int = 60,
    nb_products: int = 500,
    nb_clients: int = 300,
    out_dir: Path = Path("data/inbox"),
) -> dict[str, int]:
    """Exécute la chaîne de génération complète."""
    out_dir.mkdir(parents=True, exist_ok=True)
    recorder = DefectRecorder()

    # Référentiels maîtres
    products = generate_products(seed=seed, target_count=nb_products)
    clients = generate_clients(seed=seed, target_count=nb_clients)
    pricing_grid = generate_pricing_grid()
    mappings, lookup_by_source = generate_product_mappings(products, seed=seed, orphan_pct=0.02)

    # Export produits_master.csv
    prod_fields = ["produit_id", "libelle", "categorie", "cout_standard", "prix_base", "date_effet"]
    prod_rows = [
        {k: p[k] for k in prod_fields} for p in products
    ]
    write_csv(out_dir / "produits_master.csv", prod_rows, prod_fields)

    # Export clients_master.csv
    cli_fields = ["client_id", "raison_sociale", "categorie", "ville", "quartier", "date_effet"]
    write_csv(out_dir / "clients_master.csv", clients, cli_fields)

    # Export correspondances_produits.csv
    map_fields = ["type_entite", "source", "reference_externe", "entite_id"]
    write_csv(out_dir / "correspondances_produits.csv", mappings, map_fields)

    # Export grille_tarifaire.csv
    pricing_fields = ["categorie_client", "palier_min", "palier_max", "remise_pct"]
    write_csv(out_dir / "grille_tarifaire.csv", pricing_grid, pricing_fields)

    # Flux Ventes Caisse (CSV ';')
    caisse_sales = generate_caisse_sales(
        products=products,
        clients=clients,
        lookup_caisse=lookup_by_source["caisse"],
        defect_recorder=recorder,
        seed=seed,
        nb_days=nb_days,
        avg_lines_per_day=150,
    )
    caisse_fields = [
        "ticket_id",
        "ligne_no",
        "date_vente",
        "ref_produit_caisse",
        "designation",
        "client_code",
        "quantite",
        "prix_unitaire",
        "remise_pct",
        "statut",
    ]
    write_csv(out_dir / "ventes_caisse.csv", caisse_sales, caisse_fields, delimiter=";")

    # Vérité terrain (defauts_injectes.csv)
    defects = recorder.to_rows()
    defect_fields = [
        "flux",
        "ligne",
        "type_defaut",
        "regle_visee",
        "champ",
        "valeur_initiale",
        "valeur_alteree",
        "description",
    ]
    write_csv(out_dir / "defauts_injectes.csv", defects, defect_fields)

    return {
        "nb_produits": len(products),
        "nb_clients": len(clients),
        "nb_correspondances": len(mappings),
        "nb_grille": len(pricing_grid),
        "nb_ventes_caisse": len(caisse_sales),
        "nb_defauts_injectes": len(defects),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Générateur de données")
    parser.add_argument("--seed", type=int, default=42, help="Graine aléatoire fixe (défaut: 42)")
    parser.add_argument("--nb-days", type=int, default=60, help="Nombre de jours d'historique (défaut: 60)")
    parser.add_argument("--products", type=int, default=500, help="Nombre de produits (défaut: 500)")
    parser.add_argument("--clients", type=int, default=300, help="Nombre de clients (défaut: 300)")
    parser.add_argument("--out-dir", type=Path, default=Path("data/inbox"), help="Dossier de destination")

    args = parser.parse_args()
    summary = run_generator(
        seed=args.seed,
        nb_days=args.nb_days,
        nb_products=args.products,
        nb_clients=args.clients,
        out_dir=args.out_dir,
    )

    print("Génération terminée avec succès")
    for k, v in summary.items():
        print(f"  * {k}: {v}")


if __name__ == "__main__":
    main()
