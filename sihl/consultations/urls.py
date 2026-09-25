from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("diagnostics-cim11", views.DiagnosticCIM11ViewSet, basename="diagnostic-cim11")
router.register("allergies", views.AllergieViewSet, basename="allergie")
router.register("consultations", views.ConsultationViewSet, basename="consultation")
router.register("diagnostics", views.DiagnosticViewSet, basename="diagnostic")

urlpatterns = [path("", include(router.urls))]
