# Corpus éwé — Instructions pour Babacar

> Document animateur. Le kit est complet à l'exception des contenus éwé,
> qui relèvent d'un locuteur natif. Quatre livrables, détaillés ci-dessous.
> Les structures de fichiers existent déjà, il suffit de remplacer les
> marqueurs `[À REMPLIR PAR BABACAR]`.

## 1. Les 60 transcriptions (gabarit du plan v3)

Fichiers : `taiss2026_workshop/data/transcriptions_ee_round1.csv` (40 lignes)
et `transcriptions_ee_round2.csv` (20 lignes). Ne pas changer les `id`.

- 40 transcriptions pour le round 1, courtes, une à deux lignes
- 20 transcriptions pour le round 2
- Répartition visée : environ un tiers clairement positives, un tiers
  clairement négatives, un tiers ambiguës ou factuelles
- **Inclure délibérément 5 à 8 cas limites** : sentiment mixte, ironie,
  mauvaise nouvelle factuelle, question. Sans eux, le guide v1 ne produira
  pas assez de désaccords et la remontée du Kappa au round 2 sera invisible.
- Registres variés : information, conversation, opinion
- Aucune étiquette fournie, ce sont les participants qui annotent

**Contrainte de calibration, la même que pour le français.** Le round 2 doit
contenir la même proportion de cas limites que le round 1, environ un sur
quatre, et des mêmes types. Si le round 2 est plus facile, la hausse du Kappa
devient un artefact de conception et un participant attentif peut invalider
la démonstration.

Le corpus personnel déjà présent dans `archive/` (ewe_pur.txt) peut servir de
matière première pour le registre informatif, mais les phrases d'opinion et
les cas limites doivent être écrits pour l'exercice : le corpus autobiographique
n'en contient pas.

## 2. Guide v1 éwé — traduction littérale

Fichier : `taiss2026_workshop/guides/annotation_guide_v1_ee.md`.
Traduire le guide français mot à mot, sans l'améliorer. La consigne complète
est en tête du fichier. La littéralité est une décision du plan v3, pas une
économie de moyens.

## 3. Guide v2 éwé de référence — construit dans la langue

Fichier : `taiss2026_animateur/annotation_guide_v2_reference_ee.md`.
Celui-ci, à l'inverse, s'écrit directement en éwé avec des exemples naturels.
La structure des six règles est en tête du fichier.

## 4. Les trois fichiers audio de démonstration

Dossier : `taiss2026_workshop/audio_demo/`. Des fichiers de remplacement
synthétiques y sont posés pour que le notebook et les tests tournent ; ils ne
contiennent pas de parole. Les remplacer par trois vrais enregistrements :

1. `01_conforme.wav` — un enregistrement propre, environ 5 secondes, 16 kHz mono
2. `02_tronque.wav` — un enregistrement coupé à moins d'une seconde
3. `03_transcription_fausse.wav` — un enregistrement dont la transcription
   affichée en séquence 2 ne correspond pas à ce qu'on entend

## Après remplissage

Prévenir Fredy pour la seconde passe du script de pré-annotation
(`taiss2026_animateur/outillage/generate_predictions.py`), qui calculera les
prédictions du modèle sur les 60 phrases éwé et complétera
`model_predictions.csv`.
