import socket
import sysv_ipc
import time
import os
import threading
import signal
import sys
from multiprocessing import Process, Manager
from random import randint

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

#####COMMUNICATION######

def message_client(socket_player, message, retour="Nothing"):
    socket_player.sendall(message.encode())
    reponse = socket_player.recv(1024)
    if retour == "int":
        try:
            reponse = int(reponse.decode())
        except:
            reponse = message_client(socket_player, message, retour)
    return reponse

def stop_jeu(socket_player):
    sig = signal.SIGUSR1
    print(os.getpid(), "j'attends")
    signal.sigwait([sig])
    message_client(socket_player, '0 Fermeture')
    print(os.getpid(), "je meurs")
    time.sleep(5)
    os.kill(os.getpid(), signal.SIGTERM)

def player_main(data, socket_player, que):
    on = True
    thread = threading.Thread(target=stop_jeu, args=(socket_player, ))
    thread.start()
    while on:
        message_client(socket_player, '0 Waiting')
        print(data)
        time.sleep(5)



######MAIN######

if __name__ == '__main__':
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        HOST = "localhost"
        PORT = 6729
        key = 128
        nb_joueurs = 0
        child_processes = []
        liste_couleurs = ["bleu", "rouge", "vert", "noir", "jaune", "orange", "violet"]


        server_socket.bind((HOST, PORT))
        server_socket.listen(1)
        client_socket, address = server_socket.accept()
        print("Connected to client: ", address)
        while nb_joueurs < 2:
            nb_joueurs = message_client(client_socket, "1 Nombre de joueurs", "int")

        with Manager() as manager:
            while True:
                gros_dico = manager.dict()
                gros_dico["couleurs"] = couleurs(nb_joueurs, liste_couleurs)
                gros_dico["deck"] = deck(nb_joueurs, gros_dico["couleurs"])
                gros_dico["hand"] = hand(nb_joueurs, gros_dico["deck"])
                gros_dico["suite"] = suite(gros_dico["couleurs"])
                gros_dico["information_token"] = information_token(nb_joueurs)
                gros_dico["fuze_token"] = fuze_token()
                gros_dico["turn"] = 0
                gros_dico['key'] = key

                key = gros_dico.get('key')
                if key is not None:
                    que = sysv_ipc.MessageQueue(key, sysv_ipc.IPC_CREAT)

                p = Process(target=player_main, args=(gros_dico, client_socket, que))
                p.start()
                child_processes.append(p.pid)
                message_client(client_socket, "0 Vous êtes le joueur 0")

                for i in range(nb_joueurs - 1):
                    client_socket, address = server_socket.accept()
                    print("Connected to client: ", address)
                    p = Process(target=player_main, args=(gros_dico, client_socket, que))
                    p.start()
                    child_processes.append(p.pid)
                    message_client(client_socket, f"0 Vous êtes le joueur {i + 1}")

                gros_dico["turn"] = 1

                time.sleep(5)
                print(child_processes)
                for pid in child_processes:
                    os.kill(pid, signal.SIGUSR1)
                while True :
                    pass
