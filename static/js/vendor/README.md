# Dépendances frontales vendorisées

Principe d'autonomie (chapitre 2, principe 2) : le SIHL ne doit dépendre
d'aucune ressource hébergée hors de l'établissement, y compris en usage
normal (un CDN public est une dépendance réseau externe).

Avant la mise en production, téléchargez et placez ici :

- `vue.global.prod.js` — Vue 3 (build production, runtime complet, sans
  étape de compilation), depuis https://unpkg.com/vue@3/dist/vue.global.prod.js

Ce dossier est servi statiquement par Nginx/WhiteNoise et référencé par
`templates/index.html` en chemin relatif (`/static/js/vendor/vue.global.prod.js`),
jamais depuis un CDN.
