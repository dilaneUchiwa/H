from django.contrib import admin
from django.urls import include, path
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import TemplateView

# ensure_csrf_cookie : la PWA est une page unique sans <form> Django, donc
# aucun {% csrf_token %} n'est rendu nulle part ; sans ce décorateur le
# cookie csrftoken n'existe jamais et le premier POST (connexion) échoue.
coquille_pwa = ensure_csrf_cookie(TemplateView.as_view(template_name="index.html"))

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("sihl.core.urls")),
    path("api/", include("sihl.patients.urls")),
    path("api/", include("sihl.episodes.urls")),
    path("api/", include("sihl.consultations.urls")),
    path("api/", include("sihl.prescriptions.urls")),
    path("api/", include("sihl.pharmacie.urls")),
    path("api/", include("sihl.labo.urls")),
    path("api/", include("sihl.hospitalisation.urls")),
    path("api/", include("sihl.facturation.urls")),
    path("api/", include("sihl.rapports.urls")),
    path("", coquille_pwa, name="pwa-shell"),
]
