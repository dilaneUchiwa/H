from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("utilisateurs", views.UtilisateurViewSet, basename="utilisateur")
router.register("roles", views.RoleViewSet, basename="role")
router.register("journal-audit", views.JournalAuditViewSet, basename="journal-audit")

urlpatterns = [
    path("", include(router.urls)),
    path("moi/", views.moi, name="moi"),
    path("connexion/", views.connexion, name="connexion"),
    path("deconnexion/", views.deconnexion, name="deconnexion"),
]
