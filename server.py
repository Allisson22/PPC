from random import *

nb_joueurs = 2

couleurs = ["bleu", "rouge", "vert", "noir", "jaune", "orange"]

def deck(nb_joueurs):
    liste_cartes = []
    for i in range (nb_joueurs) :
        for un in range (3):
            liste_cartes.append({couleurs[i], 1})
        for multiples in range (2):
            for nombre in [2,3,4] :
                liste_cartes.append({couleurs[i],nombre})
        liste_cartes.append({couleurs[i],5})
    return liste_cartes


def hand(nb_joueurs, liste_cartes):
    dico_hand = {}
    for i in range(nb_joueurs):
        dico_hand[i] = []
        for compteur in range (5):
            index = randint(1, len(liste_cartes)-1)
            carte_aleatoire = liste_cartes[index]
            dico_hand[i].append(carte_aleatoire)
            liste_cartes.pop(index)
    return dico_hand


def information_token(nb_joueurs):
    nb_token = 3*nb_joueurs + 3
    return nb_token


def fuze_token():
    nb_token = 3
    return nb_token


def suite():
    dico_suite = {}
    for i in range (5):
        dico_suite[i] = [True,False,False,False,False,False]
    return dico_suite

gros_dico = {}
gros_dico["deck"] = deck(nb_joueurs)
gros_dico["hand"] = hand(2,deck(2))
gros_dico["suite"] = suite()
gros_dico["information_token"] = information_token(nb_joueurs)
gros_dico["fuze_token"] = fuze_token()
print(gros_dico)