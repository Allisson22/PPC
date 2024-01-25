import socket
import sysv_ipc
import time
import os
import threading
import signal
import sys
from multiprocessing import Process, Manager
from random import randint
from process_player import *

#####INITIALISATION DICOS#####

def deck(nb_joueurs, couleurs):
    liste_cartes = []
    for i in range(nb_joueurs):
        for un in range(3):
            liste_cartes.append({couleurs[i], 1})
        for multiples in range(2):
            for nombre in [2, 3, 4]:
                liste_cartes.append({couleurs[i], nombre})
        liste_cartes.append({couleurs[i], 5})
    return liste_cartes


def hand(nb_joueurs, liste_cartes):
    dico_hand = {}
    for i in range(nb_joueurs):
        dico_hand[i] = []
        for compteur in range(5):
            index = randint(0, len(liste_cartes)-1)
            carte_aleatoire = liste_cartes[index]
            dico_hand[i].append(carte_aleatoire)
            liste_cartes.pop(index)
    return dico_hand

def couleurs (nb_joueurs, liste_couleurs) : 
    couleurs_retenues = []

    for i in range (nb_joueurs) :
        couleurs_retenues.append(liste_couleurs[i])
    return couleurs_retenues


def information_token(nb_joueurs):
    nb_token = 3 * nb_joueurs + 3
    return nb_token


def fuze_token():
    nb_token = 3
    return nb_token


def suite(liste_couleurs):
    dico_suite = {}
    for couleur in liste_couleurs:
        dico_suite[f"{couleur}"] = [True, False, False, False, False, False]
    return dico_suite


######MAIN######

if __name__ == '__main__':
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        HOST = "localhost"
        PORT = 6736
        key = 128
        nb_joueurs = 0
        child_processes = []
        liste_couleurs = ["bleu", "rouge", "vert", "noir", "jaune", "orange", "violet","rose"]


        server_socket.bind((HOST, PORT))
        server_socket.listen(1)
        client_socket, address = server_socket.accept()
        print("Connected to client: ", address)
        while nb_joueurs < 2:
            nb_joueurs = int(message_client(client_socket, "1 Nombre de joueurs",["1","2","3","4","5","6","7","8"]))

        with Manager() as manager:
            while True:
                gros_dico = manager.dict()
                gros_dico["couleurs"] = couleurs(nb_joueurs, liste_couleurs)
                gros_dico["deck"] = deck(nb_joueurs, gros_dico["couleurs"])
                gros_dico["hand"] = hand(nb_joueurs, gros_dico["deck"])
                gros_dico["suite"] = suite(gros_dico["couleurs"])
                gros_dico["information_token"] = information_token(nb_joueurs)
                gros_dico["fuse_token"] = fuze_token()
                gros_dico["turn"] = -1
                gros_dico['key'] = key
                gros_dico["nb_joueurs"] = nb_joueurs



                que = sysv_ipc.MessageQueue(key, sysv_ipc.IPC_CREAT)

                p = Process(target=player_main, args=(gros_dico, client_socket, 0))
                p.start()
                child_processes.append(p.pid)

                for i in range(nb_joueurs - 1):
                    client_socket, address = server_socket.accept()
                    print("Connected to client: ", address)
                    p = Process(target=player_main, args=(gros_dico, client_socket, i+1))
                    p.start()
                    child_processes.append(p.pid)
                time.sleep(5)
                gros_dico["turn"] = 0

                """time.sleep(5)
                print(child_processes)
                for pid in child_processes:
                    os.kill(pid, signal.SIGUSR1)"""
                while True :
                    pass
