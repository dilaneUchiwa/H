from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("patients", views.PatientViewSet, basename="patient")
router.register("fusions-patients", views.FusionPatientViewSet, basename="fusion-patient")

urlpatterns = [path("", include(router.urls))]
