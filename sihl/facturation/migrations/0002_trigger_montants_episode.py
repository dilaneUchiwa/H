"""
Triggers PostgreSQL maintenant `episodes_episodedesoins.montant_du` et
`montant_paye` (Tableau 11) depuis `facturation_actefacturable` et
`facturation_paiement`. Non installés sur SQLite (cf. DECISIONS.md #1) :
en dev/petit site, ces colonnes ne seront pas recalculées automatiquement.
"""

from django.db import migrations

TRIGGER_SQL = """
CREATE OR REPLACE FUNCTION maj_montant_du_episode() RETURNS TRIGGER AS $$
BEGIN
    UPDATE episodes_episodedesoins
    SET montant_du = (
        SELECT COALESCE(SUM(montant), 0) FROM facturation_actefacturable
        WHERE episode_id = COALESCE(NEW.episode_id, OLD.episode_id)
    )
    WHERE id = COALESCE(NEW.episode_id, OLD.episode_id);
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_maj_montant_du ON facturation_actefacturable;
CREATE TRIGGER trg_maj_montant_du
AFTER INSERT OR UPDATE OR DELETE ON facturation_actefacturable
FOR EACH ROW EXECUTE FUNCTION maj_montant_du_episode();

CREATE OR REPLACE FUNCTION maj_montant_paye_episode() RETURNS TRIGGER AS $$
BEGIN
    UPDATE episodes_episodedesoins
    SET montant_paye = (
        SELECT COALESCE(SUM(montant), 0) FROM facturation_paiement
        WHERE episode_id = COALESCE(NEW.episode_id, OLD.episode_id)
    )
    WHERE id = COALESCE(NEW.episode_id, OLD.episode_id);
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_maj_montant_paye ON facturation_paiement;
CREATE TRIGGER trg_maj_montant_paye
AFTER INSERT OR UPDATE OR DELETE ON facturation_paiement
FOR EACH ROW EXECUTE FUNCTION maj_montant_paye_episode();
"""

REVERSE_SQL = """
DROP TRIGGER IF EXISTS trg_maj_montant_du ON facturation_actefacturable;
DROP FUNCTION IF EXISTS maj_montant_du_episode();
DROP TRIGGER IF EXISTS trg_maj_montant_paye ON facturation_paiement;
DROP FUNCTION IF EXISTS maj_montant_paye_episode();
"""


def installer_trigger(apps, schema_editor):
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute(TRIGGER_SQL)


def desinstaller_trigger(apps, schema_editor):
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute(REVERSE_SQL)


class Migration(migrations.Migration):

    dependencies = [
        ("facturation", "0001_initial"),
        ("episodes", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(installer_trigger, desinstaller_trigger),
    ]
