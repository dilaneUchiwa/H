FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Vue 3 est vendorisé dans l'image au moment du build (réseau de build
# Render), jamais rechargé depuis un CDN au runtime par le navigateur de
# l'établissement : conforme au principe d'autonomie (chapitre 2) tout en
# évitant d'imposer un téléchargement manuel avant déploiement.
RUN mkdir -p static/js/vendor \
    && curl -fsSL -o static/js/vendor/vue.global.prod.js \
       https://unpkg.com/vue@3/dist/vue.global.prod.js

RUN chmod +x scripts/docker-entrypoint.sh

EXPOSE 8000

CMD ["./scripts/docker-entrypoint.sh"]
