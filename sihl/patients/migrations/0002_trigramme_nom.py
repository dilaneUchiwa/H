"""
Extension pg_trgm et index trigramme sur PATIENT(nom, prenom) — chapitre
3.6, Tableau 12 : recherche tolérante aux fautes de saisie. Non installé
sous SQLite (cf. DECISIONS.md #1) : la recherche y reste basée sur
`icontains` (voir patients/views.py), moins tolérante aux fautes.
"""

from django.db import migrations


def installer_extension_et_index(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    schema_editor.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")
    schema_editor.execute(
        "CREATE INDEX IF NOT EXISTS idx_patient_trgm_nom_prenom "
        "ON patients_patient USING gin ((nom || ' ' || prenom) gin_trgm_ops);"
    )


def desinstaller_index(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    schema_editor.execute("DROP INDEX IF EXISTS idx_patient_trgm_nom_prenom;")


class Migration(migrations.Migration):

    dependencies = [
        ("patients", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(installer_extension_et_index, desinstaller_index),
    ]
