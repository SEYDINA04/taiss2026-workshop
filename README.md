# Atelier TAISS 2026 — Data Engineering for AI

De la donnée brute à un dataset de confiance. Atelier pratique de deux heures :
inspecter un manifeste de corpus vocal, écrire des règles de qualité, annoter
le sentiment, mesurer la fiabilité des annotations avec le Kappa, puis
empaqueter un dataset documenté.

Lomé, 27 août 2026 · animé par Babacar Ndao, Afriklang.

## Contenu du dépôt

### `taiss2026_workshop/` — dossier participant

Ce qui est distribué en salle, sans corrigés.

- `notebook_atelier.ipynb` : le fil de la séance, sept sections
- `data/` : le manifeste et les phrases à annoter (FR et EE)
- `guides/` : le guide d'annotation v1
- `scripts/quality_check.py` : contrôles de qualité, quatre fonctions à écrire
- `scripts/agreement.py` : accord brut, Kappa, matrice de confusion (fourni)
- `templates/` : gabarit de la carte du dataset
- `audio_demo/` : les trois extraits joués en ouverture

### `taiss2026_animateur/` — dossier animateur

Le filet de sécurité, à ne pas distribuer.

- `notebook_corrige.ipynb` : version résolue du notebook
- `annotation_guide_v2_reference_*.md` : les six règles cibles
- `defauts_manifest_solution.md` : les onze défauts plantés, avec leurs identifiants
- `fiche_minutage.md` : horaires et formulations à dire mot pour mot
- `google_sheet_gabarit.md` : collecte des labels
- `instructions_corpus_ewe.md` : ce qui reste à fournir en éwé
- `labels_simules/simulate_annotators.py` : simulation de calibration (Kappa v1 vs v2)
- `outillage/` : scripts de régénération de tout le kit

### Racine

- `rapport_verification.md` : contrôles exécutés, valeurs mesurées
- `Afriklang_TAISS2026_Deck_Atelier.pdf` : le deck de support

## Démarrage

Ouvrir `taiss2026_workshop/notebook_atelier.ipynb` dans Google Colab et
exécuter les deux premières cellules. Aucune installation, tout tourne avec
`pandas` et `scikit-learn`.
