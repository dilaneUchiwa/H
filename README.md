# SIHL — Système d'Information Hospitalier Léger

Implémentation du plan décrit dans `Plan_Implementation_SIHL.md` (dérivé du
mémoire *Memoire_M2_SIH_Leger.docx*). Les choix laissés ouverts par le
mémoire (18 points ⚠️ À DÉCIDER) sont documentés et tranchés dans
**`DECISIONS.md`** — à relire avant toute mise en production réelle.

## Stack (chapitre 4.1)

Debian · PostgreSQL 16 · Python 3 / Django + DRF · PWA (Vue 3, sans build) ·
Nginx + Gunicorn · Docker Compose · pg_dump + restic.

## Structure du projet

```
sihl/
  config/          settings, urls, wsgi
  core/            M8 — utilisateurs, rôles/RBAC, JournalAudit, middleware session
  patients/        M1 — identification, IPP, doublons, fusion
  episodes/        EpisodeDeSoins (entité intermédiaire patient↔consultation)
  consultations/   M2 — consultation, CIM-11, allergies
  prescriptions/   M3 — prescription et lignes de prescription
  labo/            M3 — catalogue examens, résultats
  pharmacie/       M4 — médicaments, lots, mouvements de stock
  facturation/      M5 — tarifs, actes facturés, paiements, journal de caisse
  hospitalisation/ M6 — services, lits, séjours, soins quotidiens
  rapports/        M7 — agrégats district, export DHIS2 (CSV), projection FHIR
static/js/sync.js  mécanisme hors-ligne (chapitre 3.8/4.5)
templates/         coquille PWA
scripts/           sauvegarde.sh, restauration_test.sh
```

## Démarrage (développement, SQLite)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env          # ajuster au besoin ; DATABASE_URL absent -> SQLite
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Déploiement (production, PostgreSQL, chapitre 4.1/4.2)

```bash
cp .env.example .env          # renseigner DATABASE_URL, SECRET_KEY, etc.
docker compose up -d --build
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

Les triggers PostgreSQL de dénormalisation (`stock_courant`, `montant_du`,
`montant_paye` — Tableau 11) ne s'installent qu'en environnement
PostgreSQL ; ils sont ignorés silencieusement sous SQLite (dev).

Avant la mise en production, téléchargez Vue 3 dans
`static/js/vendor/vue.global.prod.js` (voir `static/js/vendor/README.md`) :
principe d'autonomie, aucune dépendance à un CDN externe en usage normal.

## Tests

```bash
pytest
```

## Sauvegarde (règle 3-2-1, chapitre 3.9)

`scripts/sauvegarde.sh` (à brancher sur cron) exécute `pg_dump` puis
`restic` vers un dépôt chiffré hors site. `scripts/restauration_test.sh`
sert à l'exercice de restauration trimestriel obligatoire.

## Ce que ce dépôt ne couvre pas

Conformément à `DECISIONS.md`, restent hors code (organisationnels ou
dépendants du contexte réel de déploiement) : le choix matériel du serveur,
le calendrier de déploiement, le budget, le nombre de référents techniques,
le cadre légal applicable. La périmètre FHIR reste volontairement une
projection de modèle en lecture seule, jamais un serveur FHIR complet — un
choix explicite du mémoire.
