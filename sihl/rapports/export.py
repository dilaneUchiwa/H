"""
Export vers le district sanitaire / DHIS2 (chapitre 4.6.1).

Format retenu : CSV agrégé (⚠️ À DÉCIDER #16, DECISIONS.md) — le mémoire ne
spécifie pas le format technique attendu par le district réel (API DHIS2
Tracker vs fichier CSV/JSON). Le CSV agrégé est le plus universellement
acceptable sans intégration spécifique et respecte le principe de
transmission par lots compressés et opportuniste (jamais sur calendrier fixe).
"""

from __future__ import annotations

import csv
import io

from .agregation import rapport_mensuel


def export_csv_dhis2(annee: int, mois: int) -> str:
    rapport = rapport_mensuel(annee, mois)
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["indicateur", "valeur"])
    writer.writerow(["periode", f"{annee}-{mois:02d}"])
    writer.writerow(["consultations", rapport["nombre_consultations"]])
    writer.writerow(["episodes_ouverts", rapport["nombre_episodes_ouverts"]])
    writer.writerow(["admissions", rapport["nombre_admissions"]])
    writer.writerow(["sorties", rapport["nombre_sorties"]])
    writer.writerow(["recettes_totales", rapport["recettes_totales"]])
    for diagnostic in rapport["diagnostics_frequents"]:
        writer.writerow(
            [f"diagnostic_{diagnostic['code_cim11__code']}", diagnostic["nombre"]]
        )
    return buffer.getvalue()
