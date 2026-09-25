# Décisions retenues pour cette implémentation

Le `Plan_Implementation_SIHL.md` laisse 18 points ouverts (⚠️ À DÉCIDER, section 15).
Faute d'un contexte de déploiement réel, les choix suivants ont été retenus pour
pouvoir livrer un code exécutable. Ils sont **modifiables** : chacun est isolé
dans la configuration (`sihl/config/settings.py`, `.env`) ou documenté ci-dessous,
et n'engage pas la conformité au mémoire, qui reste respecté sur tout le reste.

| # | Point ouvert | Décision retenue ici | Où le changer |
|---|---|---|---|
| 1 | PostgreSQL vs SQLite | PostgreSQL 16 par défaut (production), SQLite supporté via `DATABASE_URL` pour dev/petit site | `.env` |
| 2 | Matériel serveur | Non applicable au code ; Docker Compose fonctionne sur les deux (N100 ou RPi5) | `docker-compose.yml` |
| 3 | Versions dépendances | Django 5.0 LTS, DRF 3.15, Vue 3.4 (CDN, sans build) | `requirements.txt` |
| 4 | Tables de paramétrage | Modèles `Service`, `TarifActe`, `CatalogueExamen`, `CategorieCIM11` créés avec schéma minimal extensible | `sihl/*/models.py` |
| 5 | Nomenclature CIM-11 | Sous-ensemble local (table `DiagnosticCIM11` à peupler par import CSV), pas d'appel API externe (principe d'autonomie) | `sihl/consultations/models.py` |
| 6 | Clé de contrôle IPP | Algorithme modulo 97 (type IBAN), simple à vérifier manuellement, documenté dans le code | `sihl/patients/ipp.py` |
| 7 | Seuil détection doublons | Score pondéré : phonétique 0.5, téléphone 0.35, date naissance 0.15 ; seuil d'alerte à 0.6 | `sihl/patients/services.py` |
| 8 | Durée réversibilité fusion | 90 jours, paramétrable via `ParametreEtablissement` | `sihl/core/models.py` |
| 9 | Taille cache hors-ligne | File d'attente du jour = dossiers avec RDV/passage du jour courant uniquement ; purge à minuit | `static/js/sync.js` |
| 10 | Cadre légal | Non tranché ici (dépend du pays réel de déploiement) ; aucune règle légale spécifique codée en dur | — |
| 11 | Coût fonction de hachage | Django `PBKDF2PasswordHasher` par défaut (paramètre `PASSWORD_HASHERS` ajustable selon le CPU du serveur retenu) | `sihl/config/settings.py` |
| 12 | Nombre postes/tablettes | Non applicable au code (dimensionnement matériel) | — |
| 13 | Calendrier déploiement | Non applicable au code (planning) ; ordre des modules respecté dans l'organisation des apps Django | — |
| 14 | Nombre référents techniques | Non applicable au code (organisationnel) ; RBAC prévoit un rôle `referent_technique` cumulable par plusieurs comptes | `sihl/core/models.py` |
| 15 | Périmètre FHIR | Projection de modèle uniquement, comme préconisé par le mémoire (pas de serveur FHIR complet) ; endpoint minimal Patient/Encounter/Observation en lecture seule | `sihl/rapports/fhir.py` |
| 16 | Format export DHIS2 | Export CSV agrégé par défaut (format le plus universellement acceptable sans intégration spécifique) | `sihl/rapports/export.py` |
| 17 | Budget | Non applicable au code | — |
| 18 | Tests automatisés | Suite pytest ajoutée (tests unitaires modèles/services + tests d'API) au-delà des tests d'acceptation du mémoire | `sihl/*/tests.py` |

Ces choix suivent les 7 principes directeurs (sobriété, autonomie, continuité,
non-substitution du soin, unicité, traçabilité, appropriabilité) et peuvent être
révisés sans changer l'architecture.
