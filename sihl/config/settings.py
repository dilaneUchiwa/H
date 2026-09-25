"""
Configuration Django du SIHL.

Principes du mémoire appliqués ici :
- Autonomie : aucune dépendance à un service externe (pas de CDN payant,
  pas d'API tierce obligatoire).
- Traçabilité : middleware d'audit (sihl.core) branché par défaut.
- Sobriété : dépendances minimales (cf. requirements.txt).
"""

import os
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env(
    DEBUG=(bool, False),
)
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("DJANGO_SECRET_KEY", default="changeme-en-production")
DEBUG = env("DEBUG")
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.postgres",
    "rest_framework",
    "django_filters",
    "sihl.core",
    "sihl.patients",
    "sihl.episodes",
    "sihl.consultations",
    "sihl.prescriptions",
    "sihl.pharmacie",
    "sihl.labo",
    "sihl.hospitalisation",
    "sihl.facturation",
    "sihl.rapports",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "sihl.core.middleware.SessionIdleTimeoutMiddleware",
]

ROOT_URLCONF = "sihl.config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "sihl.config.wsgi.application"

# Chapitre 4.1 : PostgreSQL 16 par défaut. SQLite accepté pour un très
# petit site (<20 postes), cf. DECISIONS.md point 1.
DATABASES = {
    "default": env.db(
        "DATABASE_URL",
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
    )
}

AUTH_USER_MODEL = "core.Utilisateur"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 10}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Chapitre 3.9 : fonction de dérivation lente + sel unique.
# Coût des itérations à calibrer selon le matériel retenu (DECISIONS.md #11).
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
]

LANGUAGE_CODE = "fr-fr"
TIME_ZONE = env("TIME_ZONE", default="Africa/Douala")
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
STORAGES = {
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 25,
}

# Chapitre 3.9, cas d'utilisation 1 : session expirée après 15 min d'inactivité.
SESSION_IDLE_TIMEOUT_SECONDS = env.int("SESSION_IDLE_TIMEOUT_SECONDS", default=15 * 60)
SESSION_COOKIE_AGE = SESSION_IDLE_TIMEOUT_SECONDS
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Chapitre 4.4 : liaison chiffrée poste<->serveur même en local.
CSRF_COOKIE_SECURE = env.bool("COOKIE_SECURE", default=not DEBUG)
SESSION_COOKIE_SECURE = env.bool("COOKIE_SECURE", default=not DEBUG)

# Chapitre 4.3 : durée de réversibilité par défaut d'une fusion de fiches
# patient (DECISIONS.md #8), paramétrable ensuite via ParametreEtablissement.
FUSION_PATIENT_REVERSIBILITE_JOURS = env.int("FUSION_REVERSIBILITE_JOURS", default=90)

# Détection de doublons (DECISIONS.md #7).
DOUBLON_SEUIL_ALERTE = env.float("DOUBLON_SEUIL_ALERTE", default=0.6)
DOUBLON_POIDS_PHONETIQUE = env.float("DOUBLON_POIDS_PHONETIQUE", default=0.5)
DOUBLON_POIDS_TELEPHONE = env.float("DOUBLON_POIDS_TELEPHONE", default=0.35)
DOUBLON_POIDS_NAISSANCE = env.float("DOUBLON_POIDS_NAISSANCE", default=0.15)

# Code établissement utilisé dans le préfixe IPP (CCC-AAAA-NNNNNN-K).
CODE_ETABLISSEMENT = env("CODE_ETABLISSEMENT", default="SIH")

# Chapitre 3.9 : "verrouillage après échecs répétés".
MAX_ECHECS_AUTHENTIFICATION = env.int("MAX_ECHECS_AUTHENTIFICATION", default=5)
DUREE_VERROUILLAGE_MINUTES = env.int("DUREE_VERROUILLAGE_MINUTES", default=15)
