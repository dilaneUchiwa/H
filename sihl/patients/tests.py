import datetime

import pytest

from .ipp import calculer_cle_controle, generer_ipp, verifier_ipp
from .models import Patient
from .phonetique import cle_phonetique
from .services import rechercher_doublons


class TestIPP:
    def test_generation_et_verification(self):
        ipp = generer_ipp("SIH", 2026, 1)
        assert ipp.startswith("SIH-2026-000001-")
        assert verifier_ipp(ipp)

    def test_detecte_erreur_saisie(self):
        ipp = generer_ipp("SIH", 2026, 1)
        ipp_altere = ipp[:-1] + str((int(ipp[-1]) + 1) % 100)
        assert not verifier_ipp(ipp_altere)

    def test_cle_stable(self):
        assert calculer_cle_controle("SIH", 2026, 42) == calculer_cle_controle("SIH", 2026, 42)


class TestPhonetique:
    def test_substitutions_mémoire(self):
        # Extrait du mémoire : NG->N, MB->B, TCH->C doivent rapprocher les variantes.
        assert cle_phonetique("Ngoma") == cle_phonetique("Noma")
        assert cle_phonetique("Mbala") == cle_phonetique("Bala")

    def test_variantes_orthographiques_arabes(self):
        assert cle_phonetique("Mohamed")[0] == cle_phonetique("Mohammed")[0]


@pytest.mark.django_db
class TestPatientModel:
    def test_attribution_ipp_sequentielle(self):
        p1 = Patient.objects.create(nom="Ngoma", prenom="Awa", sexe="F")
        p2 = Patient.objects.create(nom="Mballa", prenom="Jean", sexe="M")
        assert p1.ipp != p2.ipp
        assert verifier_ipp(p1.ipp)
        assert verifier_ipp(p2.ipp)

    def test_cle_phonetique_non_modifiable_manuellement(self):
        patient = Patient.objects.create(nom="Mbala", prenom="Awa", sexe="F")
        assert patient.cle_phonetique == cle_phonetique("Mbala")
        patient.cle_phonetique = "FORCÉ"
        patient.save()
        # Recalculée à chaque écriture, jamais conservée telle quelle.
        assert patient.cle_phonetique == cle_phonetique("Mbala")


@pytest.mark.django_db
class TestDetectionDoublons:
    def test_score_eleve_sur_telephone_et_phonetique(self):
        Patient.objects.create(
            nom="Ngoma", prenom="Awa", telephone="699000000",
            date_naissance=datetime.date(1990, 1, 1), sexe="F",
        )
        candidats = rechercher_doublons(
            nom="Noma", prenom="Awa", telephone="699000000",
            date_naissance=datetime.date(1990, 1, 1),
        )
        assert len(candidats) == 1
        assert candidats[0].score >= 0.6

    def test_aucun_doublon_si_rien_ne_correspond(self):
        Patient.objects.create(nom="Ngoma", prenom="Awa", sexe="F")
        candidats = rechercher_doublons(nom="Kamdem", prenom="Paul", telephone="699999999")
        assert candidats == []
