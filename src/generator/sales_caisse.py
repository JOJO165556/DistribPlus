"""
Générateur du flux Ventes Caisse (CSV, séparateur ';', UTF-8).
Injection des anomalies qualité et journalisation dans la vérité terrain.
"""
from datetime import datetime, timedelta
import random
from typing import Any
from src.generator.defects import DefectRecorder


def generate_caisse_sales(
    products: list[dict[str, Any]],
    clients: list[dict[str, Any]],
    lookup_caisse: dict[str, str],
    defect_recorder: DefectRecorder,
    seed: int = 42,
    start_date: str = "2024-01-01",
    nb_days: int = 60,
    avg_lines_per_day: int = 150,
) -> list[dict[str, Any]]:
    """
    Génère les lignes de vente caisse avec injection des défauts cibles.
    """
    rng = random.Random(seed)
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")

    rows: list[dict[str, Any]] = []
    ticket_counter = 1

    # Produits éligibles pour la caisse (tous)
    product_keys = list(lookup_caisse.keys())
    product_map = {p["produit_id"]: p for p in products}

    # Clients éligibles
    known_client_ids = [c["client_id"] for c in clients]

    current_dt = start_dt
    for day in range(nb_days):
        day_date = current_dt + timedelta(days=day)
        # Dimanche : boutique fermee
        if day_date.weekday() == 6:
            continue

        # Nombre de tickets ce jour (environ 25 à 40 tickets de 2 à 8 lignes)
        day_lines_target = int(rng.gauss(avg_lines_per_day, 20))
        lines_generated_today = 0

        while lines_generated_today < day_lines_target:
            ticket_id = f"TCK-{day_date.strftime('%Y%m%d')}-{ticket_counter:04d}"
            ticket_counter += 1

            # Heure d'ouverture : 07h30 à 18h30
            heure = rng.randint(7, 18)
            minute = rng.randint(0, 59)
            base_time = day_date.replace(hour=heure, minute=minute)

            # Client : 45% anonyme comptoir, 55% client enregistré
            if rng.random() < 0.45:
                client_code = ""
            else:
                client_code = rng.choice(known_client_ids)

            # Nombre de lignes par ticket
            nb_lines = rng.randint(1, 6)

            for line_no in range(1, nb_lines + 1):
                pid = rng.choice(product_keys)
                prod = product_map[pid]
                ref_caisse = lookup_caisse[pid]
                designation = prod["libelle"]
                prix_unitaire_fcfa = prod["prix_base"]

                # Quantité : petits détaillants et particuliers (1 à 15 unités/cartons)
                quantite = rng.choices([1, 2, 3, 5, 10, 20], weights=[40, 25, 15, 10, 7, 3])[0]

                # Remise (0% par défaut, parfois 1% à 3% pour gros volume)
                remise_pct = 0.0
                if quantite >= 10 and client_code:
                    remise_pct = rng.choice([1.0, 1.5, 2.0, 3.0])

                # Statut : 98% VALIDE, 2% ANNULE
                statut = "VALIDE" if rng.random() < 0.98 else "ANNULE"

                row = {
                    "ticket_id": ticket_id,
                    "ligne_no": line_no,
                    "date_vente": base_time.strftime("%d/%m/%Y %H:%M"),
                    "ref_produit_caisse": ref_caisse,
                    "designation": designation,
                    "client_code": client_code,
                    "quantite": quantite,
                    "prix_unitaire": f"{prix_unitaire_fcfa:.2f}".replace(".", ","),
                    "remise_pct": f"{remise_pct:.2f}".replace(".", ","),
                    "statut": statut,
                }
                rows.append(row)
                lines_generated_today += 1

    # Injection des anomalies selon les taux cibles de specification-sources.md §6
    total_rows = len(rows)
    line_index = 1

    final_rows: list[dict[str, Any]] = []

    for r in rows:
        row = dict(r)
        # DEF-01 : Champ obligatoire vide (1%)
        if rng.random() < 0.01:
            field_to_blank = rng.choice(["quantite", "date_vente", "ref_produit_caisse"])
            old_val = row[field_to_blank]
            row[field_to_blank] = ""
            defect_recorder.record(
                flux="caisse",
                ligne=line_index,
                type_defaut="DEF-01",
                regle_visee="EF-07",
                champ=field_to_blank,
                valeur_initiale=str(old_val),
                valeur_alteree="",
                description="Champ obligatoire laisse vide",
            )

        # DEF-03 : Dates en formats mixtes ou illisibles (0.5%)
        elif rng.random() < 0.005:
            old_val = row["date_vente"]
            bad_date = rng.choice(["2024-05-12 14:00", "32/01/2024 10:00", "date_invalide", "12-05-2024"])
            row["date_vente"] = bad_date
            defect_recorder.record(
                flux="caisse",
                ligne=line_index,
                type_defaut="DEF-03",
                regle_visee="RG-20",
                champ="date_vente",
                valeur_initiale=str(old_val),
                valeur_alteree=bad_date,
                description="Format de date non conforme",
            )

        # DEF-04 : Montants avec separateurs incoherents (0.5%)
        elif rng.random() < 0.005:
            old_val = row["prix_unitaire"]
            # Ex: point au lieu de virgule, ou espace inattendu
            bad_price = str(old_val).replace(",", ".")
            if rng.random() < 0.5:
                bad_price = " " + bad_price
            row["prix_unitaire"] = bad_price
            defect_recorder.record(
                flux="caisse",
                ligne=line_index,
                type_defaut="DEF-04",
                regle_visee="RG-21",
                champ="prix_unitaire",
                valeur_initiale=str(old_val),
                valeur_alteree=bad_price,
                description="Separateur decimal ou format montant incoherent",
            )

        # DEF-05 : Casse et espaces parasites dans les references (0.5%)
        elif rng.random() < 0.005 and row["ref_produit_caisse"]:
            old_val = row["ref_produit_caisse"]
            bad_ref = f"  {old_val.lower()} "
            row["ref_produit_caisse"] = bad_ref
            defect_recorder.record(
                flux="caisse",
                ligne=line_index,
                type_defaut="DEF-05",
                regle_visee="EF-09",
                champ="ref_produit_caisse",
                valeur_initiale=str(old_val),
                valeur_alteree=bad_ref,
                description="Espaces et casse parasites dans la reference",
            )

        # DEF-06 : Reference sans correspondance (2% des refs)
        elif rng.random() < 0.015:
            old_val = row["ref_produit_caisse"]
            orphan_ref = f"P-99{rng.randint(100, 999)}"
            row["ref_produit_caisse"] = orphan_ref
            defect_recorder.record(
                flux="caisse",
                ligne=line_index,
                type_defaut="DEF-06",
                regle_visee="RG-03",
                champ="ref_produit_caisse",
                valeur_initiale=str(old_val),
                valeur_alteree=orphan_ref,
                description="Reference produit inexistante dans le referentiel",
            )

        # DEF-07 : Quantite <= 0 ou prix negatif (0.3%)
        elif rng.random() < 0.003:
            if rng.random() < 0.5:
                old_val = row["quantite"]
                bad_qty = rng.choice([0, -2, -10])
                row["quantite"] = bad_qty
                defect_recorder.record(
                    flux="caisse",
                    ligne=line_index,
                    type_defaut="DEF-07",
                    regle_visee="RG-10",
                    champ="quantite",
                    valeur_initiale=str(old_val),
                    valeur_alteree=str(bad_qty),
                    description="Quantite negative ou nulle",
                )
            else:
                old_val = row["prix_unitaire"]
                bad_price = "-1500,00"
                row["prix_unitaire"] = bad_price
                defect_recorder.record(
                    flux="caisse",
                    ligne=line_index,
                    type_defaut="DEF-07",
                    regle_visee="RG-10",
                    champ="prix_unitaire",
                    valeur_initiale=str(old_val),
                    valeur_alteree=bad_price,
                    description="Prix unitaire negatif",
                )

        # DEF-08 : Remise hors [0; 100%] (0.2%)
        elif rng.random() < 0.002:
            old_val = row["remise_pct"]
            bad_remise = rng.choice(["150,00", "-5,00", "200,00"])
            row["remise_pct"] = bad_remise
            defect_recorder.record(
                flux="caisse",
                ligne=line_index,
                type_defaut="DEF-08",
                regle_visee="RG-10",
                champ="remise_pct",
                valeur_initiale=str(old_val),
                valeur_alteree=bad_remise,
                description="Remise en dehors des bornes [0; 100%]",
            )

        # DEF-09 : Date de vente future (0.1%)
        elif rng.random() < 0.001:
            old_val = row["date_vente"]
            future_date = "15/10/2030 14:00"
            row["date_vente"] = future_date
            defect_recorder.record(
                flux="caisse",
                ligne=line_index,
                type_defaut="DEF-09",
                regle_visee="RG-20",
                champ="date_vente",
                valeur_initiale=str(old_val),
                valeur_alteree=future_date,
                description="Date de transaction dans le futur",
            )

        # DEF-12 : Client inconnu du referentiel (1%)
        elif rng.random() < 0.01 and row["client_code"]:
            old_val = row["client_code"]
            unknown_cli = f"CLI-99{rng.randint(10, 99)}"
            row["client_code"] = unknown_cli
            defect_recorder.record(
                flux="caisse",
                ligne=line_index,
                type_defaut="DEF-12",
                regle_visee="RG-02",
                champ="client_code",
                valeur_initiale=str(old_val),
                valeur_alteree=unknown_cli,
                description="Code client non reference",
            )

        final_rows.append(row)
        line_index += 1

        # DEF-02 : Ligne dupliquee (0.5%)
        if rng.random() < 0.005:
            dup_row = dict(row)
            final_rows.append(dup_row)
            defect_recorder.record(
                flux="caisse",
                ligne=line_index,
                type_defaut="DEF-02",
                regle_visee="RG-19",
                champ="ticket_id + ligne_no",
                valeur_initiale="unique",
                valeur_alteree=f"{row['ticket_id']}_{row['ligne_no']}",
                description="Ligne de vente dupliquee avec la meme cle",
            )
            line_index += 1

    return final_rows
