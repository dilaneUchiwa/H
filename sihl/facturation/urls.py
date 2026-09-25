from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("tarifs-actes", views.TarifActeViewSet, basename="tarif-acte")
router.register("actes-factures", views.ActeFacturableViewSet, basename="acte-facturable")
router.register("paiements", views.PaiementViewSet, basename="paiement")
router.register("journal-caisse", views.JournalCaisseViewSet, basename="journal-caisse")

urlpatterns = [path("", include(router.urls))]
