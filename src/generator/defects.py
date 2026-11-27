"""
Gestionnaire d'injection et de journalisation des anomalies qualité (DEF-01 à DEF-12).
Enregistre chaque injection dans le fichier de vérité terrain 'defauts_injectes.csv'.
"""
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class InjectedDefect:
    flux: str             # 'caisse' | 'b2b' | 'stock'
    ligne: int            # numéro de ligne dans le fichier source (1-based sans en-tête)
    type_defaut: str      # 'DEF-01' à 'DEF-12'
    regle_visee: str      # 'EF-07', 'RG-19', etc.
    champ: str            # nom du champ altéré
    valeur_initiale: str
    valeur_alteree: str
    description: str


class DefectRecorder:
    """Enregistre tous les défauts injectés pour constituer la vérité terrain."""

    def __init__(self) -> None:
        self.defects: list[InjectedDefect] = []

    def record(
        self,
        flux: str,
        ligne: int,
        type_defaut: str,
        regle_visee: str,
        champ: str,
        valeur_initiale: str,
        valeur_alteree: str,
        description: str,
    ) -> None:
        self.defects.append(
            InjectedDefect(
                flux=flux,
                ligne=ligne,
                type_defaut=type_defaut,
                regle_visee=regle_visee,
                champ=champ,
                valeur_initiale=str(valeur_initiale),
                valeur_alteree=str(valeur_alteree),
                description=description,
            )
        )

    def to_rows(self) -> list[dict[str, str]]:
        return [asdict(d) for d in self.defects]
