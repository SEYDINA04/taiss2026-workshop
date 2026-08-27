# Rapport de vérification — kit technique atelier TAISS 2026

Vérifications exécutées le 27 août 2026 (nuit précédant l'atelier), machine de
production du kit, Python 3.13, pandas 3.0.3, scikit-learn 1.9.0, numpy 2.5.1.
Chaque point de la liste du prompt a été réellement exécuté ; les valeurs
ci-dessous sont mesurées, pas déclarées. Script : `kit_build/verify_all.py`,
sortie : 14/14 contrôles conformes.

## La liste du prompt, point par point

**1. Le notebook s'exécute de bout en bout avec les TODO remplis.**
Conforme. `notebook_corrige.ipynb`, 27 cellules de code exécutées dans l'ordre
sous nbclient, zéro erreur. Barrière de qualité complète : 200 lignes en
entrée, **123 conservées** (exactement les 123 lignes propres du manifeste),
53 rejets par contrôles ligne à ligne, 20 doublons, 5 mojibake. Les 11
artefacts du dossier final `taiss2026_sentiment_ee-fr_v1.0/` sont produits.

**2. Le notebook s'exécute aussi avec les TODO non remplis.**
Conforme. `notebook_atelier.ipynb` tel que livré : 27 cellules exécutées,
zéro exception. La barrière tourne en mode dégradé assumé (3 contrôles actifs,
4 ignorés et nommés dans le rapport de qualité), 154 lignes conservées, et
toutes les séquences avales aboutissent : les 11 artefacts sont produits, y
compris splits et carte. Aucune casse en chaîne.

**3. Quantités exactes de défauts dans raw_manifest.csv.**
Conforme, comptage indépendant par `count_defects.py` (lecture seule du CSV) :
doublons exacts 12/12, doublons approximatifs 8/8, durées aberrantes 6/6,
sample_rate 8000 7/7, channels 2 5/5, langue incohérente 6/6, transcription
vide 9/9, débit impossible 6/6 (dont l'hommage 40 mots / 0,6 s), mojibake 5/5,
speaker manquant 15/15, date future 4/4. Six lignes cumulent deux défauts.

**4. Entre 55 et 65 % de lignes propres.**
Conforme : **123/200 = 61,5 %**.

**5. Les six types de cas limites couverts, décompte par type.**
Conforme : mixte 3, ironie 3, rapporté 3, neutre flou 2, mauvaise nouvelle
factuelle 2, question 2 — chaque trou du guide v1 est déclenché par au moins
deux phrases du corpus.

**6. Même proportion de cas limites dans les deux rounds.**
Conforme : round 1 = 10/40 = 25 %, round 2 = 5/20 = 25 %, types identiques.

**7. La simulation deux annotateurs montre une hausse du Kappa.**
Conforme, mesuré par `simulate_annotators.py` (graine 90210) :

| Condition | Accord brut | Kappa |
|---|---|---|
| guide v1 sur round 1 (protocole atelier) | 77,5 % | **0,661** |
| guide v2 sur round 2 (protocole atelier) | 95,0 % | **0,924** |
| guide v1 sur round 2 (contrôle) | 70,0 % | 0,535 |
| guide v2 sur round 1 (contrôle) | 92,5 % | 0,885 |

Delta du protocole : **+0,264**, corroboré dans les deux sens de contrôle.
L'accord brut v1 tombe dans la fourchette 70–80 % annoncée en séquence 4c.

**8. Kappa d'agreement.py vérifié contre un exemple à la main.**
Conforme : exemple 10 items, po = 0,8, pe = 0,34, kappa main = 0,696969697,
kappa scikit-learn = 0,696969697, écart < 1e-9.

**9. Guide v1 : une page, des silences, pas d'erreurs.**
Conforme : 25 lignes, 180 mots. Scan lexical : aucun des termes des six trous
(ironie, mixte, rapporté, question, impératif, nouvelle, insistance) n'y
figure — les trous sont des silences. Le guide définit correctement les trois
classes, la définition de neutre est vague sans être fausse.

**10. Aucune phrase éwé générée.**
Conforme, vérifié mécaniquement : les 20 lignes éwé légitimes du manifeste
proviennent verbatim de `archive/ewe_pur.txt` (corpus fourni par Babacar,
assertion ligne à ligne) ; les 6 lignes marquées « ee » à texte français sont
le défaut planté ; les 120 lignes des fichiers de round éwé sont à 100 % des
placeholders `[À REMPLIR PAR BABACAR]` ; la ligne éwé du jeu de tests des
scripts est extraite du même corpus.

**11. Aucune clé d'API en dur.**
Conforme : scan par motifs sur les 52 fichiers des deux dossiers, zéro
suspect. `generate_predictions.py` lit `ANTHROPIC_API_KEY` dans
l'environnement et refuse de démarrer sans elle.

**12. Les deux chemins de récupération des labels fonctionnent.**
Conforme, testés hors notebook sur la fonction extraite du notebook : chemin
Sheet (CSV publié) avec lignes dans le désordre et label accentué « Négatif  »
→ réaligné sur les ids attendus et normalisé ; chemin manuel → validé ;
absence des deux → message d'orientation, retour None, aucune exception.

## Contrôles au-delà de la liste

- **UTF-8** : tous les CSV relus en UTF-8 strict, caractères éwé intacts
  (ɔ ɖ ƒ ŋ ɛ ã) — mesuré.
- **Notebook** : aucun emoji, aucune installation de paquet, imports limités à
  pandas + scripts du kit + bibliothèque standard — mesuré. Sections titrées
  avec horaires, consigne et temps imparti en encadré en tête de chaque
  section, cellules d'exercice au format attendu/test/déblocage, longueurs de
  cellules markdown variées — relu cellule par cellule sur les exports
  exécutés.
- **Accord modèle/consensus** dans le corrigé : 96 % sur 50 phrases
  consensuelles, désaccords concentrés sur les cas limites tranchés par le
  guide v2 — c'est le matériau de discussion voulu pour la séquence 5.
- **Splits** : 91/16/16 lignes (74/13/13 %), **zéro locuteur commun** entre
  train et test, mesuré dans les deux exécutions.
- **Prédictions du modèle** : 60 prédictions fr en zéro-shot réel
  (claude-fable-5, consigne sans règles de cas limites), 56/60 en accord avec
  le gold v2 ; les 4 écarts sont tous des cas limites (chantier terminé lu
  positif, deux hausses de prix lues négatives, reproche interrogatif manqué).

## Écarts et compléments par rapport à l'arborescence du prompt

Fichiers ajoutés, tous côté animateur ou racine, rien dans le dossier
participant : `instructions_corpus_ewe.md`, `google_sheet_gabarit.md`,
`outillage/` (scripts de régénération, dont `generate_predictions.py` exigé
par la spécification section 10, et `manifest_defects.json`, registre des
positions de défauts), `labels_simules/gold_v2_fr.csv` et les 4 CSV de labels
simulés, `audio_demo/README.md`. Le dossier participant suit l'arborescence
du prompt à l'identique, plus ce README audio.

## Dépendances externes restantes (bloquantes pour le jour J)

1. **Corpus éwé de Babacar** : 60 transcriptions dans les fichiers de round,
   traduction littérale du guide v1, guide v2 de référence éwé — structures et
   consignes en place, voir `taiss2026_animateur/instructions_corpus_ewe.md`.
2. **Seconde passe des prédictions** (`generate_predictions.py --language ee`)
   une fois le corpus livré.
3. **Trois vrais fichiers audio** à la place des placeholders synthétiques.
4. **Google Sheet** à créer et publier selon `google_sheet_gabarit.md`, et
   **URL publique du zip** à coller dans `DATA_URL` du notebook (le repli
   local et le téléversement manuel fonctionnent sans elle).

## Livrables

- `taiss2026_workshop/` — dossier participant, 24 fichiers, aucun corrigé
- `taiss2026_animateur/` — dossier animateur, 26 fichiers
- `taiss2026_workshop.zip` — 327 Ko, archive testée (`unzip -t` sans erreur),
  prête à déposer sur une URL publique
