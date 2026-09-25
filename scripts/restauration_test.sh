#!/usr/bin/env bash
#
# Exercice de restauration trimestriel obligatoire (chapitre 3.9, 4.9).
# Exigence non fonctionnelle : restauration complète < 30 min par un agent
# formé (Tableau ch. 4.9). Restaure vers une base de test distincte,
# JAMAIS vers la base de production.

set -euo pipefail

DUMP_A_RESTAURER="${1:?Usage: restauration_test.sh <chemin_du_dump>}"
BASE_TEST="sihl_test_restauration"

echo "[$(date)] Recréation de la base de test ${BASE_TEST}"
dropdb --if-exists "${BASE_TEST}"
createdb "${BASE_TEST}"

DEBUT=$(date +%s)
pg_restore --dbname="${BASE_TEST}" "${DUMP_A_RESTAURER}"
FIN=$(date +%s)

DUREE=$((FIN - DEBUT))
echo "[$(date)] Restauration terminée en ${DUREE}s (exigence : < 1800s)"

if [ "${DUREE}" -gt 1800 ]; then
    echo "ATTENTION : durée de restauration au-delà de l'exigence de 30 minutes." >&2
    exit 1
fi

echo "Exercice de restauration réussi. Base de test : ${BASE_TEST}"
