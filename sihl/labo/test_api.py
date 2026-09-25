import pytest

from sihl.prescriptions.models import LignePrescription


@pytest.mark.django_db
class TestExamenLaboAPI:
    def test_creation_examen_et_resultat_via_api(self, client_authentifie, prescription, catalogue_examen, superutilisateur):
        ligne = LignePrescription.objects.create(
            prescription=prescription, type_ligne=LignePrescription.Type.EXAMEN, examen=catalogue_examen
        )
        reponse = client_authentifie.post(
            "/api/examens-labo/", {"ligne_prescription": ligne.pk, "catalogue": catalogue_examen.pk}
        )
        assert reponse.status_code == 201
        examen_id = reponse.data["id"]

        reponse_resultat = client_authentifie.post(
            "/api/resultats-examens/", {"examen": examen_id, "valeur": "0.95", "unite": "g/L"}
        )
        assert reponse_resultat.status_code == 201
        assert reponse_resultat.data["valide_par"] == superutilisateur.pk
        assert reponse_resultat.data["hors_reference"] is False

    def test_catalogue_lecture_seule(self, client_authentifie, catalogue_examen):
        reponse = client_authentifie.post(
            "/api/catalogue-examens/", {"code": "nouveau", "libelle": "Nouveau"}
        )
        assert reponse.status_code == 405
