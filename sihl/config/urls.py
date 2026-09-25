from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

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
    path("", TemplateView.as_view(template_name="index.html"), name="pwa-shell"),
]
