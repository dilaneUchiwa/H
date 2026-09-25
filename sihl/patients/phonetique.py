"""
Clé phonétique adaptée aux patronymes locaux (bantous, peuls, arabes) —
chapitre 3.7.2. Soundex/Metaphone standards sont mal calibrés sur ces
patronymes : le mémoire préconise un algorithme adapté avec substitutions de
digrammes/trigrammes fréquents, complété par une table de correspondance
locale des graphies alternatives (voir ``CorrespondanceGraphie``).

Les substitutions ci-dessous reprennent l'extrait de code cité dans le
mémoire (``sihl/patients/services.py``) : NG→N, MB→B, TCH→C, etc.
"""

from __future__ import annotations

import re
import unicodedata

# Substitutions appliquées dans l'ordre, sur la chaîne en majuscules.
# Trigrammes avant digrammes avant lettres simples pour éviter les
# recouvrements (ex. TCH doit être substitué avant CH).
SUBSTITUTIONS: list[tuple[str, str]] = [
    ("TCH", "C"),
    ("DJ", "J"),
    ("NG", "N"),
    ("NY", "N"),
    ("MB", "B"),
    ("MP", "P"),
    ("ND", "D"),
    ("NT", "T"),
    ("KH", "K"),
    ("GH", "G"),
    ("PH", "F"),
    ("TH", "T"),
    ("CH", "S"),
    ("OU", "U"),
    ("AI", "E"),
    ("AU", "O"),
    ("EU", "U"),
    ("Y", "I"),
    ("Q", "K"),
    ("C", "K"),
    ("Z", "S"),
    ("X", "KS"),
]

VOYELLES = set("AEIOU")


def _sans_accents(texte: str) -> str:
    forme_decomposee = unicodedata.normalize("NFKD", texte)
    return "".join(c for c in forme_decomposee if not unicodedata.combining(c))


def _normaliser(texte: str) -> str:
    texte = _sans_accents(texte or "").upper()
    texte = re.sub(r"[^A-Z]", "", texte)
    return texte


def cle_phonetique(nom: str) -> str:
    """
    Calcule une clé phonétique tolérante aux variantes orthographiques
    courantes dans la zone de déploiement. Ne remplace pas une correspondance
    de graphies connues (cf. ``CorrespondanceGraphie``), qui reste prioritaire.
    """
    texte = _normaliser(nom)
    if not texte:
        return ""

    for motif, remplacement in SUBSTITUTIONS:
        texte = texte.replace(motif, remplacement)

    # Supprime les doublons consécutifs de lettres (ex. ABBAS -> ABAS).
    texte = re.sub(r"(.)\1+", r"\1", texte)

    # Supprime les voyelles sauf en première position (proche de Soundex),
    # ce qui absorbe la plupart des variations de transcription des voyelles.
    if texte:
        tete, reste = texte[0], texte[1:]
        reste = "".join(c for c in reste if c not in VOYELLES)
        texte = tete + reste

    return texte[:8]


def similarite_phonetique(nom_a: str, prenom_a: str, nom_b: str, prenom_b: str) -> float:
    """Retourne un score entre 0 et 1 basé sur les clés phonétiques nom+prénom."""
    cle_a = cle_phonetique(nom_a) + "|" + cle_phonetique(prenom_a)
    cle_b = cle_phonetique(nom_b) + "|" + cle_phonetique(prenom_b)
    if cle_a == cle_b and cle_a != "|":
        return 1.0
    # Similarité partielle : clé de nom seule identique.
    if cle_phonetique(nom_a) == cle_phonetique(nom_b) and cle_phonetique(nom_a):
        return 0.6
    return 0.0
