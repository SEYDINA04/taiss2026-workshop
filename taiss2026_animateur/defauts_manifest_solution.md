# Les onze défauts plantés — solution animateur

> Ne pas divulguer avant la restitution de la séquence 2. Ce document liste
> chaque défaut, sa quantité exacte et les identifiants concernés, pour
> compléter au tableau ce que la salle n'a pas trouvé.
>
> Vue d'ensemble : 200 lignes, 123 propres (61,5 %), 77 défectueuses, six
> lignes cumulent deux défauts. Les 60 phrases calibrées de la séquence 4 et
> les 20 vraies lignes éwé sont toutes propres et survivent au nettoyage.


## Doublons exacts — 12 lignes

12 lignes strictement identiques à une autre, identifiant compris. `drop_duplicates` les retire ; les identifiants listés sont ceux des lignes dupliquées, chaque copie partage l'identifiant de son original.

Identifiants : `rec_0050`, `rec_0051`, `rec_0058`, `rec_0068`, `rec_0071`, `rec_0092`, `rec_0101`, `rec_0169`, `rec_0170`

## Doublons approximatifs — 8 lignes

8 lignes qui ne diffèrent de leur original que par une majuscule, un espace en fin de texte, un espace doublé ou la casse de la région. Invisibles pour `drop_duplicates` brut, capturés après normalisation minuscules + espaces.

Identifiants : `rec_0032`, `rec_0037`, `rec_0059`, `rec_0060`, `rec_0083`, `rec_0129`, `rec_0134`, `rec_0146`

## Durées aberrantes — 6 lignes

3 lignes à 0,2 s et 3 lignes à 47 s. Les 0,2 s portent une transcription d'un seul mot : leur débit reste sous le seuil, c'est bien le contrôle de durée qui doit les attraper, pas celui de débit.

Identifiants : `rec_0013`, `rec_0024`, `rec_0057`, `rec_0100`, `rec_0168`, `rec_0175`

## Fréquence incohérente — 7 lignes

7 lignes à 8000 Hz au lieu de 16000. Deux cumulent un speaker_id manquant, une cumule une transcription vide.

Identifiants : `rec_0007`, `rec_0094`, `rec_0097`, `rec_0136`, `rec_0158`, `rec_0167`, `rec_0176`

## Canaux incohérents — 5 lignes

5 lignes en stéréo là où le corpus est mono. Une cumule un speaker_id manquant, une cumule un encodage cassé.

Identifiants : `rec_0040`, `rec_0054`, `rec_0078`, `rec_0113`, `rec_0163`

## Langue mal renseignée — 6 lignes

6 lignes marquées `ee` dont la transcription est manifestement du français, au moins deux mots outils français distincts chacune. Les 20 vraies lignes éwé du manifeste ne déclenchent pas l'heuristique.

Identifiants : `rec_0066`, `rec_0075`, `rec_0118`, `rec_0120`, `rec_0151`, `rec_0164`

## Transcription vide — 9 lignes

9 lignes sans texte, dont une cumule la fréquence à 8000 Hz.

Identifiants : `rec_0002`, `rec_0028`, `rec_0072`, `rec_0117`, `rec_0122`, `rec_0131`, `rec_0173`, `rec_0176`, `rec_0179`

## Débit impossible — 6 lignes

6 lignes au-dessus de 6 mots par seconde, dont l'hommage au plan : 40 mots annoncés sur 0,6 s. Les durées de ces lignes restent dans la plage normale, seul le rapport mots/durée les trahit.

Identifiants : `rec_0006`, `rec_0019`, `rec_0031`, `rec_0126`, `rec_0165`, `rec_0174`

## Encodage cassé — 5 lignes

5 lignes en mojibake réel, UTF-8 relu en latin-1 (« é » devenu « Ã© »), dont une cumulée avec la stéréo. Détection : présence de « Ã » ou « â€ ».

Identifiants : `rec_0003`, `rec_0054`, `rec_0064`, `rec_0140`, `rec_0171`

## Identifiant locuteur manquant — 15 lignes

15 lignes sans speaker_id : 11 pures, 2 cumulées avec la fréquence, 1 avec la stéréo, 1 avec une date future.

Identifiants : `rec_0001`, `rec_0018`, `rec_0023`, `rec_0053`, `rec_0076`, `rec_0097`, `rec_0106`, `rec_0124`, `rec_0125`, `rec_0154`, `rec_0158`, `rec_0161`, `rec_0162`, `rec_0163`, `rec_0178`

## Date impossible — 4 lignes

4 lignes enregistrées après le jour de l'atelier (2026-09-30, 2026-12-15, 2027-01-10, 2027-03-05). Référence de comparaison fixée au 27 août 2026 dans les contrôles, pour rester reproductible.

Identifiants : `rec_0055`, `rec_0076`, `rec_0077`, `rec_0089`

## Ce que la barrière de la séquence 3 attrape, et le reste

Les sept contrôles ligne à ligne attrapent durées, fréquence, canaux, langue, vides, débit, métadonnées et dates. Les doublons et le mojibake se traitent au niveau du tableau entier, le notebook fournit ces deux opérations déjà écrites dans la cellule d'application de la barrière : personne n'a à les coder, mais la distinction ligne contre tableau vaut d'être dite à voix haute.
