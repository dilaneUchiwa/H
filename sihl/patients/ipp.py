"""
Génération de l'Identifiant Patient Permanent (IPP) — chapitre 3.7.1.

Format : ``CCC-AAAA-NNNNNN-K``
  - CCC : code établissement (3 caractères)
  - AAAA : année de création du dossier
  - NNNNNN : numéro séquentiel sur 6 chiffres, par établissement et par année
  - K : clé de contrôle

Le mémoire ne fixe pas l'algorithme de la clé de contrôle (⚠️ À DÉCIDER #6,
cf. DECISIONS.md). Choix retenu ici : **modulo 97**, comme pour les IBAN.
Il est simple à vérifier manuellement (calcul de tête possible à l'accueil)
et détecte 100% des erreurs à un chiffre et la quasi-totalité des
transpositions de deux chiffres adjacents.
"""

from __future__ import annotations

IPP_SEPARATEUR = "-"


def _partie_numerique(code_etablissement: str, annee: int, sequence: int) -> int:
    """Convertit CCC+AAAA+NNNNNN en un entier unique pour le calcul modulo 97."""
    base_alpha_numerique = "".join(
        str(ord(c) - 55) if c.isalpha() else c for c in code_etablissement.upper()
    )
    return int(f"{base_alpha_numerique}{annee:04d}{sequence:06d}")


def calculer_cle_controle(code_etablissement: str, annee: int, sequence: int) -> int:
    return 98 - (_partie_numerique(code_etablissement, annee, sequence) * 100) % 97


def generer_ipp(code_etablissement: str, annee: int, sequence: int) -> str:
    cle = calculer_cle_controle(code_etablissement, annee, sequence)
    return IPP_SEPARATEUR.join(
        [code_etablissement.upper(), f"{annee:04d}", f"{sequence:06d}", f"{cle:02d}"]
    )


def verifier_ipp(ipp: str) -> bool:
    """Revalide la clé de contrôle d'un IPP saisi manuellement."""
    try:
        code_etablissement, annee, sequence, cle = ipp.split(IPP_SEPARATEUR)
        return calculer_cle_controle(code_etablissement, int(annee), int(sequence)) == int(cle)
    except (ValueError, AttributeError):
        return False
