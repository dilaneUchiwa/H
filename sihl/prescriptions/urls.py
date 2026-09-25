from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("prescriptions", views.PrescriptionViewSet, basename="prescription")
router.register("lignes-prescription", views.LignePrescriptionViewSet, basename="ligne-prescription")

urlpatterns = [path("", include(router.urls))]
