# -*- coding: utf-8 -*-
"""Solutions de référence des quatre fonctions TODO et de quality_gate.

Servent au notebook corrigé, au repli du notebook participant et à la
vérification avant livraison. Jamais distribuées aux participants.
"""

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "taiss2026_workshop" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import quality_check as qc  # noqa: E402


def check_channels(row, expected=qc.EXPECTED_CHANNELS):
    try:
        return int(row["channels"]) == expected
    except (TypeError, ValueError, KeyError):
        return False


check_channels.__doc__ = qc.check_channels.__doc__


def check_words_per_second(row, max_wps=qc.MAX_WORDS_PER_SECOND):
    words = qc._words(qc._text(row["transcription"]))
    if not words:
        return True
    try:
        d = float(row["duration_s"])
    except (TypeError, ValueError, KeyError):
        return True
    if d != d or d <= 0:
        return True
    return len(words) / d <= max_wps


check_words_per_second.__doc__ = qc.check_words_per_second.__doc__


def check_language_consistency(row):
    if qc._text(row.get("language") if isinstance(row, dict) else row["language"]) != "ee":
        return True
    tokens = qc._words(qc._text(row["transcription"]))
    hits = {t for t in tokens if t in qc.FRENCH_STOPWORDS}
    return len(hits) < 2


check_language_consistency.__doc__ = qc.check_language_consistency.__doc__


def check_metadata_complete(row):
    for field in qc.REQUIRED_METADATA_FIELDS:
        if qc._text(row[field]) == "":
            return False
    return qc._text(row["recorded_at"]) <= qc.REFERENCE_DATE


check_metadata_complete.__doc__ = qc.check_metadata_complete.__doc__


def quality_gate(row, checks=None):
    if checks is None:
        checks = SOLVED_CHECKS
    reasons = [c.__name__ for c in checks if not c(row)]
    return (len(reasons) == 0, reasons)


quality_gate.__doc__ = qc.quality_gate.__doc__

SOLVED_CHECKS = [
    qc.check_duration,
    qc.check_sample_rate,
    qc.check_transcription_present,
    check_channels,
    check_words_per_second,
    check_language_consistency,
    check_metadata_complete,
]


def install():
    """Injecte les solutions dans le module quality_check.

    Après appel, qc.ALL_CHECKS et qc.quality_gate se comportent comme si un
    participant avait tout résolu correctement.
    """
    qc.check_channels = check_channels
    qc.check_words_per_second = check_words_per_second
    qc.check_language_consistency = check_language_consistency
    qc.check_metadata_complete = check_metadata_complete
    qc.quality_gate = quality_gate
    qc.ALL_CHECKS = list(SOLVED_CHECKS)
    return qc


if __name__ == "__main__":
    install()
    print("tests des solutions de référence :")
    ok = True
    for fn in [check_channels, check_words_per_second,
               check_language_consistency, check_metadata_complete,
               quality_gate]:
        print(fn.__name__)
        ok = qc.run_tests(fn) and ok
    print("\ntous les tests passent" if ok else "\nDES TESTS ÉCHOUENT")
    sys.exit(0 if ok else 1)
