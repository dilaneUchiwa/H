#!/bin/sh
# Point d'entrée du conteneur : migrations, fichiers statiques, puis
# Gunicorn. Un seul fichier exécutable évite les soucis de tokenisation
# de commandes multi-lignes ("&&") par certaines plateformes de déploiement.
set -e

python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py assurer_superutilisateur

exec gunicorn sihl.config.wsgi:application --bind "0.0.0.0:${PORT:-8000}" --workers 3
