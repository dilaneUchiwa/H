import pytest

from .models import Allergie, Consultation, Diagnostic


@pytest.mark.django_db
class TestConsultationModel:
    def test_creation_consultation(self, episode, utilisateur):
        consultation = Consultation.objects.create(
            episode=episode, medecin=utilisateur, motif="Fièvre"
        )
        assert consultation.pk is not None
        assert consultation.episode == episode

    def test_diagnostic_lie_a_consultation(self, episode, utilisateur, diagnostic_cim11):
        consultation = Consultation.objects.create(episode=episode, medecin=utilisateur, motif="Fièvre")
        diagnostic = Diagnostic.objects.create(consultation=consultation, code_cim11=diagnostic_cim11)
        assert diagnostic in consultation.diagnostics.all()


@pytest.mark.django_db
class TestAllergieModel:
    def test_allergie_visible_sur_le_patient(self, patient):
        Allergie.objects.create(patient=patient, libelle="Pénicilline", severite="SEVERE")
        assert patient.allergies.count() == 1
