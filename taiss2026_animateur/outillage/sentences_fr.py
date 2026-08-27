# -*- coding: utf-8 -*-
"""Corpus français de l'atelier : 60 phrases calibrées contre les six trous du guide v1.

Chaque entrée porte :
- text        : la transcription telle qu'annotée par les participants
- round       : 1 (40 phrases) ou 2 (20 phrases)
- category    : 'positif' | 'negatif' | 'neutre' | 'limite'
- limite_type : None ou l'un de {'mixte','neutre_flou','rapporte','ironie',
                'mauvaise_nouvelle','question'}
- gold_v2     : label de référence une fois les règles v2 appliquées
- a_v1, b_v1  : labels que produisent les deux annotateurs synthétiques sous
                le guide v1. Pour les phrases claires ils suivent gold_v2,
                le bruit résiduel est injecté ailleurs (simulate_annotators.py).

La calibration vise : sous v1, désaccord concentré sur les cas limites ;
sous v2, convergence vers gold_v2. La proportion de cas limites est identique
dans les deux rounds (25 %), types compris, pour que la hausse du Kappa ne
soit pas un artefact de difficulté.
"""

POS, NEG, NEU = "positif", "negatif", "neutre"


def _clear(text, rnd, cat):
    return dict(text=text, round=rnd, category=cat, limite_type=None,
                gold_v2=cat, a_v1=cat, b_v1=cat)


def _limite(text, rnd, ltype, gold, a_v1, b_v1):
    return dict(text=text, round=rnd, category="limite", limite_type=ltype,
                gold_v2=gold, a_v1=a_v1, b_v1=b_v1)


SENTENCES = [
    # ---------------- ROUND 1 : 12 positives claires ----------------
    _clear("Le nouveau marché de Hédzranawoé est vraiment bien organisé, on trouve tout sans se fatiguer.", 1, POS),
    _clear("Franchement, l'équipe a fait un travail remarquable sur ce projet.", 1, POS),
    _clear("La connexion est redevenue stable, ça fait plaisir de travailler dans ces conditions.", 1, POS),
    _clear("Ma fille a réussi son concours d'entrée, toute la maison est en joie.", 1, POS),
    _clear("Ce tailleur coud très bien, je recommande les yeux fermés.", 1, POS),
    _clear("L'accueil à la clinique était chaleureux et rapide, je suis reparti rassuré.", 1, POS),
    _clear("Le concert d'hier soir était magnifique, les gens ont dansé jusqu'au bout.", 1, POS),
    _clear("Grâce à la nouvelle pompe, on a de l'eau propre tous les matins, c'est un grand soulagement.", 1, POS),
    _clear("Son restaurant mérite sa réputation, le poisson braisé est excellent.", 1, POS),
    _clear("Je suis très fier du travail des jeunes de notre quartier.", 1, POS),
    _clear("La formation m'a beaucoup apporté, je me sens enfin à l'aise avec l'ordinateur.", 1, POS),
    _clear("Quelle belle surprise, le colis est arrivé deux jours en avance.", 1, POS),

    # ---------------- ROUND 1 : 12 négatives claires ----------------
    _clear("Le service était vraiment décevant, on a attendu deux heures pour rien.", 1, NEG),
    _clear("Cette route est un calvaire, les nids-de-poule ont abîmé ma moto.", 1, NEG),
    _clear("Je suis très déçu par la qualité du tissu, il s'est déchiré au premier lavage.", 1, NEG),
    _clear("L'application plante sans arrêt, c'est devenu inutilisable.", 1, NEG),
    _clear("On nous a encore menti sur les délais, j'en ai assez de ces promesses.", 1, NEG),
    _clear("La viande n'était pas fraîche, tout le monde a été malade le soir.", 1, NEG),
    _clear("Ce chauffeur conduit n'importe comment, j'ai eu peur pendant tout le trajet.", 1, NEG),
    _clear("Les coupures d'eau rendent la vie impossible dans le quartier.", 1, NEG),
    _clear("Le professeur humilie les élèves devant toute la classe, c'est inacceptable.", 1, NEG),
    _clear("J'ai perdu toute ma récolte de maïs à cause des chenilles.", 1, NEG),
    _clear("Le guichetier m'a parlé avec un mépris que je n'oublierai pas.", 1, NEG),
    _clear("Trois pannes en une semaine, ce groupe électrogène est une catastrophe.", 1, NEG),

    # ---------------- ROUND 1 : 6 neutres franches ----------------
    _clear("La réunion du comité est prévue jeudi à neuf heures dans la salle habituelle.", 1, NEU),
    _clear("Le magasin ouvre de huit heures à dix-huit heures, du lundi au samedi.", 1, NEU),
    _clear("Le bus de Kpalimé passe par Adéta avant de rejoindre la gare routière.", 1, NEU),
    _clear("L'atelier de couture se trouve juste derrière la station-service.", 1, NEU),
    _clear("Il faut compter environ trois heures de route entre Lomé et Atakpamé.", 1, NEU),
    _clear("Le dossier demandé comporte une photocopie de la carte d'identité et deux photos.", 1, NEU),

    # ---------------- ROUND 1 : 10 cas limites ----------------
    # mixte : A lit la proposition finale, B applique un biais de négativité
    _limite("Le service était lent, mais le plat valait vraiment le déplacement.",
            1, "mixte", POS, a_v1=POS, b_v1=NEG),
    _limite("L'hôtel est propre et bien situé, dommage que le bruit de la rue gâche les nuits.",
            1, "mixte", NEG, a_v1=NEG, b_v1=NEG),
    # neutre_flou : fait à teinte implicite ; A range dans neutre, B suit la teinte
    _limite("Le chantier du pont est terminé depuis la semaine dernière.",
            1, "neutre_flou", NEU, a_v1=NEU, b_v1=POS),
    _limite("Il n'a toujours pas répondu à mon message depuis mardi.",
            1, "neutre_flou", NEG, a_v1=NEU, b_v1=NEG),
    # rapporte : A annote le contenu rapporté, B refuse car ce n'est pas le locuteur
    _limite("Le client a dit qu'il était très satisfait de la livraison.",
            1, "rapporte", POS, a_v1=POS, b_v1=NEU),
    _limite("Selon ma voisine, le nouveau dispensaire serait une vraie réussite.",
            1, "rapporte", POS, a_v1=POS, b_v1=NEU),
    # ironie : A lit les marqueurs au premier degré, B lit l'intention
    _limite("Bravo, troisième coupure de courant de la journée, on avance bien.",
            1, "ironie", NEG, a_v1=POS, b_v1=NEG),
    _limite("Magnifique, le taxi est encore tombé en panne en plein soleil.",
            1, "ironie", NEG, a_v1=NEG, b_v1=NEG),
    # mauvaise_nouvelle : fait négatif énoncé sans jugement
    _limite("Le prix du sac de ciment a augmenté de quinze pour cent ce mois-ci.",
            1, "mauvaise_nouvelle", NEU, a_v1=NEG, b_v1=NEU),
    # question : reproche implicite porté par « cette fois »
    _limite("Vous comptez livrer la commande à quelle heure, cette fois ?",
            1, "question", NEG, a_v1=NEU, b_v1=NEG),

    # ---------------- ROUND 2 : 6 positives claires ----------------
    _clear("La coopérative a doublé sa production, tout le monde est motivé.", 2, POS),
    _clear("Le nouveau moulin fait gagner un temps précieux aux femmes du village.", 2, POS),
    _clear("J'ai adoré la pièce de théâtre, les comédiens étaient excellents.", 2, POS),
    _clear("Le médecin a pris le temps de tout expliquer, je suis sorti rassuré et confiant.", 2, POS),
    _clear("Cette bourse va changer la vie de mon fils, on est très reconnaissants.", 2, POS),
    _clear("Le stade rénové est superbe, les gradins étaient pleins et joyeux.", 2, POS),

    # ---------------- ROUND 2 : 6 négatives claires ----------------
    _clear("Encore une réunion annulée à la dernière minute, on perd notre temps.", 2, NEG),
    _clear("Le colis est arrivé cassé et personne ne veut me rembourser.", 2, NEG),
    _clear("Cette imprimante est une plaie, elle bloque une feuille sur deux.", 2, NEG),
    _clear("Les moustiques ont rendu la soirée insupportable malgré les spirales.", 2, NEG),
    _clear("Je regrette cet achat, la batterie se vide en une heure.", 2, NEG),
    _clear("Le carrefour est devenu dangereux, deux accidents rien que cette semaine.", 2, NEG),

    # ---------------- ROUND 2 : 3 neutres franches ----------------
    _clear("La pharmacie de garde change chaque dimanche à minuit.", 2, NEU),
    _clear("Le formulaire se retire au deuxième étage, bureau douze.", 2, NEU),
    _clear("La saison des pluies commence généralement vers la mi-avril dans la région.", 2, NEU),

    # ---------------- ROUND 2 : 5 cas limites, mêmes types ----------------
    _limite("La salle était bondée et bruyante, mais la conférence elle-même était passionnante.",
            2, "mixte", POS, a_v1=POS, b_v1=NEG),
    _limite("Formidable, la pluie a choisi exactement l'heure de la cérémonie.",
            2, "ironie", NEG, a_v1=POS, b_v1=NEG),
    _limite("La station a annoncé une hausse du prix du carburant pour septembre.",
            2, "mauvaise_nouvelle", NEU, a_v1=NEG, b_v1=NEU),
    _limite("Tu peux me confirmer l'heure de la réunion de demain ?",
            2, "question", NEU, a_v1=NEU, b_v1=NEU),
    _limite("La directrice a déclaré que les résultats de cette année la déçoivent beaucoup.",
            2, "rapporte", NEG, a_v1=NEG, b_v1=NEU),
]


def sanity_check():
    r1 = [s for s in SENTENCES if s["round"] == 1]
    r2 = [s for s in SENTENCES if s["round"] == 2]
    assert len(r1) == 40 and len(r2) == 20, (len(r1), len(r2))

    def dist(rows):
        out = {}
        for s in rows:
            out[s["category"]] = out.get(s["category"], 0) + 1
        return out

    d1, d2 = dist(r1), dist(r2)
    assert d1 == {"positif": 12, "negatif": 12, "neutre": 6, "limite": 10}, d1
    assert d2 == {"positif": 6, "negatif": 6, "neutre": 3, "limite": 5}, d2
    # même proportion de cas limites dans les deux rounds
    assert d1["limite"] / 40 == d2["limite"] / 20 == 0.25

    types_r1 = sorted(s["limite_type"] for s in r1 if s["limite_type"])
    types_r2 = sorted(s["limite_type"] for s in r2 if s["limite_type"])
    assert set(types_r2) <= set(types_r1)
    # chaque trou du guide est déclenché par au moins deux phrases sur le corpus
    from collections import Counter
    total = Counter(types_r1) + Counter(types_r2)
    assert all(v >= 2 for v in total.values()), total
    assert set(total) == {"mixte", "neutre_flou", "rapporte", "ironie",
                          "mauvaise_nouvelle", "question"}
    texts = [s["text"] for s in SENTENCES]
    assert len(set(texts)) == 60, "doublon dans les phrases calibrées"
    return {"round1": d1, "round2": d2, "types": dict(total)}


if __name__ == "__main__":
    print(sanity_check())
