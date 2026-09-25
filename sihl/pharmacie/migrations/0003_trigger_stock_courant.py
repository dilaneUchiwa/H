"""
Trigger PostgreSQL maintenant `pharmacie_medicament.stock_courant`
(Tableau 11) à partir des écritures sur `pharmacie_mouvementstock`.

Le mémoire est explicite : cette colonne est en lecture seule côté
application et doit être maintenue par déclencheur, jamais par le code
métier. Sur SQLite (dev/petit site, cf. DECISIONS.md #1), ce trigger n'est
pas installé : `MouvementStock.save()` reste alors la seule source de
vérité pour le stock du lot, mais `stock_courant` ne sera pas recalculé
automatiquement — usage PostgreSQL recommandé dès qu'un trigger est requis.
"""

from django.db import migrations

TRIGGER_SQL = """
CREATE OR REPLACE FUNCTION maj_stock_courant_medicament() RETURNS TRIGGER AS $$
BEGIN
    UPDATE pharmacie_medicament
    SET stock_courant = (
        SELECT COALESCE(SUM(quantite_restante), 0)
        FROM pharmacie_lotpharmaceutique
        WHERE medicament_id = (
            SELECT medicament_id FROM pharmacie_lotpharmaceutique WHERE id = NEW.lot_id
        )
    )
    WHERE id = (SELECT medicament_id FROM pharmacie_lotpharmaceutique WHERE id = NEW.lot_id);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_maj_stock_courant ON pharmacie_mouvementstock;
CREATE TRIGGER trg_maj_stock_courant
AFTER INSERT ON pharmacie_mouvementstock
FOR EACH ROW EXECUTE FUNCTION maj_stock_courant_medicament();
"""

REVERSE_SQL = """
DROP TRIGGER IF EXISTS trg_maj_stock_courant ON pharmacie_mouvementstock;
DROP FUNCTION IF EXISTS maj_stock_courant_medicament();
"""


def installer_trigger(apps, schema_editor):
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute(TRIGGER_SQL)


def desinstaller_trigger(apps, schema_editor):
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute(REVERSE_SQL)


class Migration(migrations.Migration):

    dependencies = [
        ("pharmacie", "0002_initial"),
    ]

    operations = [
        migrations.RunPython(installer_trigger, desinstaller_trigger),
    ]
