from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("services", views.ServiceViewSet, basename="service")
router.register("lits", views.LitViewSet, basename="lit")
router.register("sejours", views.SejourViewSet, basename="sejour")
router.register("soins-quotidiens", views.SoinQuotidienViewSet, basename="soin-quotidien")

urlpatterns = [path("", include(router.urls))]
