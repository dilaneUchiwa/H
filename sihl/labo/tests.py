import pytest

from .models import ExamenLabo, ResultatExamen


@pytest.mark.django_db
class TestResultatExamenModel:
    def test_valeur_hors_reference_detectee(self, prescription, catalogue_examen, utilisateur):
        from sihl.prescriptions.models import LignePrescription

        ligne = LignePrescription.objects.create(
            prescription=prescription, type_ligne=LignePrescription.Type.EXAMEN, examen=catalogue_examen
        )
        examen = ExamenLabo.objects.create(ligne_prescription=ligne, catalogue=catalogue_examen)

        resultat = ResultatExamen.objects.create(
            examen=examen, valeur="2.5", unite="g/L", valide_par=utilisateur
        )
        assert resultat.hors_reference is True

        examen.refresh_from_db()
        assert examen.statut == ExamenLabo.Statut.VALIDE

    def test_valeur_dans_la_reference(self, prescription, catalogue_examen, utilisateur):
        from sihl.prescriptions.models import LignePrescription

        ligne = LignePrescription.objects.create(
            prescription=prescription, type_ligne=LignePrescription.Type.EXAMEN, examen=catalogue_examen
        )
        examen = ExamenLabo.objects.create(ligne_prescription=ligne, catalogue=catalogue_examen)
        resultat = ResultatExamen.objects.create(
            examen=examen, valeur="0.9", unite="g/L", valide_par=utilisateur
        )
        assert resultat.hors_reference is False
