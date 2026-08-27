# -*- coding: utf-8 -*-
"""Contrôles de qualité du manifeste, séquence 3 de l'atelier.

Chaque fonction contrôle un critère sur UNE ligne du manifeste et retourne un
booléen : True si la ligne est conforme pour ce critère, False sinon. La
fonction quality_gate agrège ces contrôles et motive sa décision.

Trois fonctions sont fournies comme modèles. Quatre sont à écrire, signalées
par TODO. Chaque fonction à écrire a ses tests : lancez run_tests(ma_fonction)
pour savoir où vous en êtes. Les tests disent ce qui est attendu, pas comment
l'obtenir.

Les seuils sont des décisions, pas des vérités. Ils sont regroupés ici, en
tête de fichier, pour être visibles, discutables et modifiables. Les changer
change le dataset produit.
"""

import re

MIN_DURATION_S = 0.5
MAX_DURATION_S = 20.0
EXPECTED_SAMPLE_RATE = 16000
EXPECTED_CHANNELS = 1
MAX_WORDS_PER_SECOND = 6.0

# Date de référence pour juger qu'une date d'enregistrement est impossible.
# Fixée au jour de l'atelier plutôt qu'à la date d'exécution, pour que le
# résultat du contrôle soit le même quel que soit le jour où on le lance.
REFERENCE_DATE = "2026-08-27"

# Lexique de mots outils français pour l'heuristique de langue. Les mots trop
# courts ou existant aussi en éwé écrit (« le », « me », « de », « en ») sont
# volontairement absents : ils déclencheraient de faux positifs sur les lignes
# réellement éwé.
FRENCH_STOPWORDS = {
    "les", "des", "une", "est", "dans", "pour", "avec", "sur", "pas", "que",
    "qui", "nous", "vous", "elle", "sont", "cette", "mais", "tout", "fait",
    "plus", "aussi", "être", "avoir", "chez", "leur", "notre", "votre",
}

REQUIRED_METADATA_FIELDS = ["speaker_id", "region", "recorded_at", "source"]


def _text(value):
    """Rend une valeur de cellule utilisable comme texte.

    None, NaN et les chaînes vides deviennent "". Tout le reste devient sa
    représentation en chaîne, sans espaces de bord.
    """
    if value is None:
        return ""
    if isinstance(value, float) and value != value:
        return ""
    s = str(value).strip()
    return "" if s.lower() == "nan" else s


def _words(text):
    return re.findall(r"[\w'àâäéèêëîïôöùûüçɔɖƒŋɛ̃]+", str(text).lower(), re.UNICODE)


# --------------------------------------------------------------------------
# Fonctions fournies, à lire comme des modèles avant d'écrire les vôtres.
# --------------------------------------------------------------------------

def check_duration(row, min_s=MIN_DURATION_S, max_s=MAX_DURATION_S):
    """Contrôle que la durée est un nombre compris entre min_s et max_s.

    Entrée : une ligne du manifeste (accès par row["duration_s"]).
    Sortie : True si min_s <= durée <= max_s, False sinon.
    Cas limites : durée absente, non numérique ou NaN → False, une durée
    illisible est une durée suspecte.
    """
    try:
        d = float(row["duration_s"])
    except (TypeError, ValueError, KeyError):
        return False
    if d != d:
        return False
    return min_s <= d <= max_s


def check_sample_rate(row, expected=EXPECTED_SAMPLE_RATE):
    """Contrôle que la fréquence d'échantillonnage est exactement celle attendue.

    Entrée : une ligne du manifeste.
    Sortie : True si sample_rate == expected, False sinon.
    Cas limites : valeur absente ou non numérique → False.
    """
    try:
        return int(row["sample_rate"]) == expected
    except (TypeError, ValueError, KeyError):
        return False


def check_transcription_present(row):
    """Contrôle que la transcription contient du texte.

    Entrée : une ligne du manifeste.
    Sortie : True si la transcription n'est ni vide ni composée d'espaces,
    False sinon.
    Cas limites : None et NaN comptent comme vide.
    """
    return _text(row["transcription"]) != ""


# --------------------------------------------------------------------------
# Fonctions à écrire. Les tests en bas de fichier décrivent le contrat.
# --------------------------------------------------------------------------

def check_channels(row, expected=EXPECTED_CHANNELS):
    """Contrôle que le nombre de canaux est exactement celui attendu.

    Entrée : une ligne du manifeste (row["channels"]).
    Sortie : True si channels == expected, False sinon.
    Cas limites : valeur absente ou non numérique → False.

    Exemple :
        >>> check_channels({"channels": 1})
        True
        >>> check_channels({"channels": 2})
        False
    """
    # TODO : sur le modèle de check_sample_rate.
    raise NotImplementedError


def check_words_per_second(row, max_wps=MAX_WORDS_PER_SECOND):
    """Contrôle que le débit de parole annoncé est physiquement plausible.

    Entrée : une ligne du manifeste (row["transcription"], row["duration_s"]).
    Sortie : False si nombre_de_mots / durée > max_wps, True sinon.
    Cas limites : transcription vide → True (0 mot, débit nul, c'est le rôle
    de check_transcription_present de signaler le vide). Durée nulle, négative
    ou illisible → True, c'est le rôle de check_duration de la signaler ;
    ce contrôle ne juge que le rapport entre les deux.

    Ce contrôle SIGNALE une transcription à vérifier, il ne prouve pas
    qu'elle est fausse. Un débit impossible veut dire : quelqu'un doit
    écouter ce fichier.

    Exemple :
        >>> check_words_per_second({"transcription": "quarante mots " * 20,
        ...                         "duration_s": 0.6})
        False
    """
    # TODO : compter les mots avec _words(...), convertir la durée comme dans
    # check_duration, comparer le rapport au seuil.
    raise NotImplementedError


def check_language_consistency(row):
    """Contrôle que le texte d'une ligne marquée « ee » ressemble bien à de l'éwé.

    Heuristique, pas détection : on compte les mots outils français distincts
    dans la transcription (lexique FRENCH_STOPWORDS). Deux ou plus dans une
    ligne marquée « ee » → la ligne est suspecte → False. Une ligne marquée
    « fr » est toujours acceptée : sans lexique éwé, l'inverse n'est pas
    contrôlable, et on le dit ici plutôt que de le laisser croire.

    Entrée : une ligne du manifeste (row["language"], row["transcription"]).
    Sortie : True si cohérent (ou incontrôlable), False si une ligne « ee »
    contient au moins deux mots outils français distincts.
    Cas limites : transcription vide → True.

    Exemple :
        >>> check_language_consistency({"language": "ee",
        ...     "transcription": "Les enfants sont dans la cour pour jouer."})
        False
    """
    # TODO : ne traiter que le cas language == "ee". Tokeniser avec _words,
    # compter les mots distincts présents dans FRENCH_STOPWORDS.
    raise NotImplementedError


def check_metadata_complete(row):
    """Contrôle que les métadonnées minimales sont présentes et plausibles.

    Entrée : une ligne du manifeste.
    Sortie : True si chaque champ de REQUIRED_METADATA_FIELDS est non vide
    (au sens de _text) ET si recorded_at ne dépasse pas REFERENCE_DATE,
    False sinon.
    Cas limites : un enregistrement daté d'après le jour de l'atelier est
    impossible, donc non conforme. La comparaison de dates au format
    AAAA-MM-JJ peut se faire directement entre chaînes.

    Exemple :
        >>> check_metadata_complete({"speaker_id": "spk_012", "region": "Kara",
        ...     "recorded_at": "2026-01-15", "source": "studio_lome"})
        True
    """
    # TODO : _text(...) pour tester la présence, comparaison de chaînes pour
    # la date.
    raise NotImplementedError


ALL_CHECKS = [
    check_duration,
    check_sample_rate,
    check_transcription_present,
    check_channels,
    check_words_per_second,
    check_language_consistency,
    check_metadata_complete,
]


def quality_gate(row, checks=None):
    """Agrège les contrôles sur une ligne.

    Entrée : une ligne du manifeste, et optionnellement une liste de fonctions
    de contrôle (par défaut ALL_CHECKS).
    Sortie : (accepted, reasons) où accepted vaut True si tous les contrôles
    passent, et reasons liste le nom des contrôles qui ont échoué
    (fonction.__name__). Ligne conforme → (True, []).

    Exemple :
        >>> quality_gate({"duration_s": 3.0, "sample_rate": 8000, ...})
        (False, ['check_sample_rate'])
    """
    if checks is None:
        checks = ALL_CHECKS
    reasons = []
    # TODO : appeler chaque contrôle, collecter le nom de ceux qui échouent,
    # en déduire accepted.
    raise NotImplementedError


# --------------------------------------------------------------------------
# Tests. Chaque cas dit ce qu'il vérifie ; si un cas échoue, relisez le
# contrat de la docstring avant de modifier votre code.
# --------------------------------------------------------------------------

_ROW_OK = {
    "id": "rec_9001", "audio_path": "audio/rec_9001.wav", "duration_s": 4.2,
    "sample_rate": 16000, "channels": 1, "language": "fr",
    "transcription": "La séance commence dans dix minutes.",
    "speaker_id": "spk_007", "region": "Maritime",
    "recorded_at": "2026-03-02", "source": "studio_lome",
}


def _row(**changes):
    r = dict(_ROW_OK)
    r.update(changes)
    return r


TEST_CASES = {
    "check_channels": [
        (_row(), True, "mono attendu, mono trouvé"),
        (_row(channels=2), False, "stéréo au lieu de mono"),
        (_row(channels="deux"), False, "valeur non numérique"),
        (_row(channels=None), False, "valeur absente"),
    ],
    "check_words_per_second": [
        (_row(), True, "débit normal"),
        (_row(transcription=" ".join(["mot"] * 40), duration_s=0.6), False,
         "40 mots en 0,6 s, débit impossible"),
        (_row(transcription="", duration_s=3.0), True,
         "transcription vide, hors du périmètre de ce contrôle"),
        (_row(transcription="quelques mots normaux ici", duration_s=0.0), True,
         "durée nulle, c'est check_duration qui signale"),
        (_row(transcription="sept mots exactement pour cette phrase là",
              duration_s=1.0), False, "7 mots par seconde, au-dessus du seuil"),
    ],
    "check_language_consistency": [
        (_row(), True, "ligne fr, toujours acceptée"),
        (_row(language="ee",
              transcription="Les enfants sont dans la cour pour jouer."),
         False, "marquée ee, texte manifestement français"),
        (_row(language="ee",
              transcription="Meɖo nɔvi nyɔnuvi eve kple nɔvi ŋsuvi eve"),
         True, "marquée ee, texte éwé (ligne du corpus fourni)"),
        (_row(language="ee", transcription=""), True, "vide, incontrôlable"),
    ],
    "check_metadata_complete": [
        (_row(), True, "métadonnées complètes, date passée"),
        (_row(speaker_id=""), False, "speaker_id vide"),
        (_row(speaker_id=float("nan")), False, "speaker_id NaN"),
        (_row(recorded_at="2027-01-10"), False, "date après le jour de l'atelier"),
        (_row(region=""), False, "région vide"),
    ],
    "quality_gate": [
        (_row(), (True, []), "ligne conforme"),
        (_row(sample_rate=8000), (False, ["check_sample_rate"]),
         "un seul contrôle échoue, son nom est le motif"),
        (_row(sample_rate=8000, channels=2),
         (False, ["check_sample_rate", "check_channels"]),
         "deux contrôles échouent, deux motifs, dans l'ordre de ALL_CHECKS"),
    ],
}


def run_tests(fn):
    """Lance les tests d'une fonction et affiche le résultat cas par cas.

    Retourne True si tous les cas passent. Une fonction encore non écrite
    est signalée comme telle, pas comme une erreur.
    """
    cases = TEST_CASES.get(fn.__name__)
    if cases is None:
        print(f"pas de tests pour {fn.__name__}")
        return False
    all_ok = True
    for row, expected, label in cases:
        try:
            got = fn(row)
        except NotImplementedError:
            print(f"  {fn.__name__} : à implémenter ({label})")
            return False
        except Exception as e:
            print(f"  ÉCHEC  {label} : levée de {type(e).__name__}: {e}")
            all_ok = False
            continue
        if got == expected:
            print(f"  ok     {label}")
        else:
            print(f"  ÉCHEC  {label} : attendu {expected!r}, obtenu {got!r}")
            all_ok = False
    return all_ok


if __name__ == "__main__":
    for f in ALL_CHECKS + [quality_gate]:
        if f.__name__ in TEST_CASES:
            print(f.__name__)
            run_tests(f)
