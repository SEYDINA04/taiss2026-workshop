# Guide d'annotation — Sentiment (version 2, référence animateur, français)

> Dossier animateur uniquement. Ce document est la cible vers laquelle la
> réécriture collective de la séquence 4d doit converger. Il sert d'aide-mémoire
> si une dimension manque au tableau. Il ne se distribue pas : le guide v2 des
> participants est celui qu'ils écrivent eux-mêmes.

Le guide v2 reprend le guide v1 (objectif, trois classes, consigne de saisie)
et ajoute une règle explicite par trou constaté. Les six règles ci-dessous
sont numérotées dans l'ordre où les désaccords les font généralement émerger.

## Règle 1 — Sentiment mixte

Quand une phrase contient un jugement positif et un jugement négatif, annoter
le **jugement final**, celui sur lequel le locuteur conclut. Si aucun des deux
ne conclut, annoter `neutre`.

- « Le service était lent, mais le plat valait vraiment le déplacement. » → `positif`
- « L'hôtel est propre et bien situé, dommage que le bruit gâche les nuits. » → `negatif`

## Règle 2 — Neutre redéfini

`neutre` désigne un **énoncé factuel sans jugement exprimé par le locuteur**,
même si le fait rapporté est une bonne ou une mauvaise chose pour quelqu'un.
Un marqueur d'insistance ou de reproche (« toujours pas », « encore une fois »,
« cette fois ») compte comme un jugement exprimé.

- « Le chantier du pont est terminé depuis la semaine dernière. » → `neutre`
- « Il n'a toujours pas répondu à mon message depuis mardi. » → `negatif`

## Règle 3 — Objet du sentiment

On annote le sentiment **exprimé dans l'énoncé**, y compris quand il est
rapporté d'une autre personne. Le rapporteur n'a pas besoin de le partager.
La prudence du rapporteur (« serait », « selon ») ne neutralise pas le label,
sauf distance explicite (« je n'y crois pas »).

- « Le client a dit qu'il était très satisfait de la livraison. » → `positif`
- « La directrice a déclaré que les résultats la déçoivent beaucoup. » → `negatif`

## Règle 4 — Ironie et sarcasme

Annoter **l'intention, pas la lettre**. Une louange dont le contexte montre
qu'elle signifie l'inverse est annotée selon ce qu'elle signifie.

- « Bravo, troisième coupure de courant de la journée, on avance bien. » → `negatif`

## Règle 5 — Mauvaise nouvelle factuelle

Un fait défavorable énoncé sans jugement reste `neutre`. C'est l'application
de la règle 2 : on annote l'expression du locuteur, pas la désirabilité du fait.
Avec un marqueur de plainte, la phrase devient `negatif`.

- « Le prix du sac de ciment a augmenté de quinze pour cent ce mois-ci. » → `neutre`
- « Le prix du ciment a encore augmenté, ça devient invivable. » → `negatif`

## Règle 6 — Questions et impératifs

Une question ou un ordre est `neutre` par défaut. Si la formulation porte une
charge émotionnelle explicite (reproche, enthousiasme), annoter cette charge.

- « Tu peux me confirmer l'heure de la réunion de demain ? » → `neutre`
- « Vous comptez livrer la commande à quelle heure, cette fois ? » → `negatif`

---

**Note d'animation.** Si la salle propose une règle différente mais cohérente
(par exemple : mixte → toujours `neutre`), l'accepter et la faire appliquer par
tous. La leçon porte sur l'explicitation d'une règle commune, pas sur le choix
de telle règle plutôt que telle autre. Le Kappa monte dès que la règle est
partagée, quelle qu'elle soit.
