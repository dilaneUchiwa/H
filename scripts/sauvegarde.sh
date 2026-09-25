#!/usr/bin/env bash
#
# Sauvegarde nocturne — règle 3-2-1 (chapitre 3.9, 4.7) :
#   1. base en production (PostgreSQL, ce script)
#   2. copie quotidienne automatique sur disque externe (DISQUE_LOCAL)
#   3. copie hebdomadaire chiffrée emportée hors site (restic + dépôt distant)
#
# Un exercice de restauration trimestriel est obligatoire (mémoire,
# chapitre 3.9) — voir scripts/restauration_test.sh.
#
# Appelé par cron, ex. tous les jours à 02h00 :
#   0 2 * * * /app/scripts/sauvegarde.sh >> /var/log/sihl-sauvegarde.log 2>&1

set -euo pipefail

HORODATAGE="$(date +%Y%m%d-%H%M%S)"
DISQUE_LOCAL="${SIHL_DISQUE_SAUVEGARDE:-/mnt/sauvegarde}"
DUMP_DIR="${DISQUE_LOCAL}/pg_dumps"
FICHIER_DUMP="${DUMP_DIR}/sihl-${HORODATAGE}.dump"

POSTGRES_DB="${POSTGRES_DB:-sihl}"
POSTGRES_USER="${POSTGRES_USER:-sihl}"
POSTGRES_HOST="${POSTGRES_HOST:-db}"

# restic : dépôt et clé de chiffrement hors serveur (jamais stockée en clair
# sur la machine sauvegardée — chapitre 3.9, chiffrement des sauvegardes).
export RESTIC_REPOSITORY="${SIHL_RESTIC_REPOSITORY:?Variable SIHL_RESTIC_REPOSITORY requise}"
export RESTIC_PASSWORD_FILE="${SIHL_RESTIC_PASSWORD_FILE:?Variable SIHL_RESTIC_PASSWORD_FILE requise}"

mkdir -p "${DUMP_DIR}"

echo "[$(date)] Démarrage sauvegarde pg_dump vers ${FICHIER_DUMP}"
pg_dump --host="${POSTGRES_HOST}" --username="${POSTGRES_USER}" \
    --format=custom --file="${FICHIER_DUMP}" "${POSTGRES_DB}"

echo "[$(date)] pg_dump terminé : $(du -h "${FICHIER_DUMP}" | cut -f1)"

# Copie hebdomadaire chiffrée hors site (restic déduplique : coût marginal
# faible même en exécution quotidienne, ce qui simplifie l'opération).
echo "[$(date)] Envoi restic vers ${RESTIC_REPOSITORY}"
restic backup "${FICHIER_DUMP}" --tag sihl --tag "${HORODATAGE}"

# Purge locale : conserve 14 jours de dumps sur le disque local, restic
# conserve son propre historique selon la politique de rétention ci-dessous.
find "${DUMP_DIR}" -name 'sihl-*.dump' -mtime +14 -delete

# Politique de rétention restic : 14 quotidiennes, 8 hebdomadaires, 12 mensuelles.
restic forget --tag sihl \
    --keep-daily 14 --keep-weekly 8 --keep-monthly 12 --prune

echo "[$(date)] Sauvegarde terminée avec succès."
