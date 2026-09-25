from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("catalogue-examens", views.CatalogueExamenViewSet, basename="catalogue-examen")
router.register("examens-labo", views.ExamenLaboViewSet, basename="examen-labo")
router.register("resultats-examens", views.ResultatExamenViewSet, basename="resultat-examen")

urlpatterns = [path("", include(router.urls))]
