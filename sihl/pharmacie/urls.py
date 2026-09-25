from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("medicaments", views.MedicamentViewSet, basename="medicament")
router.register("lots-pharmaceutiques", views.LotPharmaceutiqueViewSet, basename="lot-pharmaceutique")
router.register("mouvements-stock", views.MouvementStockViewSet, basename="mouvement-stock")

urlpatterns = [path("", include(router.urls))]
