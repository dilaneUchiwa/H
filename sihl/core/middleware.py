import time

from django.contrib.auth import logout
from django.conf import settings


class SessionIdleTimeoutMiddleware:
    """
    Déconnecte l'agent après SESSION_IDLE_TIMEOUT_SECONDS d'inactivité
    (chapitre 3.9, cas d'utilisation 1 : 15 minutes par défaut).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            derniere_activite = request.session.get("derniere_activite")
            maintenant = time.time()
            if derniere_activite is not None:
                if maintenant - derniere_activite > settings.SESSION_IDLE_TIMEOUT_SECONDS:
                    logout(request)
            request.session["derniere_activite"] = maintenant
        return self.get_response(request)
