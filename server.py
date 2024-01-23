from random import *
from multiprocessing import Process, Manager
import socket
import sysv_ipc
import signal
import os
#####INITIALISATION DICOS#####

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

#####COMMUNICATION######

child_processes = []

def message_client(socket_player,message,retour = "Nothing"):
    socket_player.sendall(message.encode())
    reponse = socket_player.recv(1024)
    if retour == "int" :
        try :
            reponse = int(reponse.decode())
        except :
            reponse = message_client(socket_player,message,retour)
    return reponse


def player_main(key,data,socket_player) :
    que = sysv_ipc.MessageQueue(key, sysv_ipc.IPC_CREAT)
    on = True
    while on :
        print(2,data["hand"])
        print(message_client(socket_player,f"0 {data['hand']}"))
        print(message_client(socket_player,"1 Nombre de joueurs"))
            
def stop_handler(signum, frame):
    print("Received signal to stop the game.")
    for pid in child_processes:
        os.kill(pid, signal.SIGTERM)
    sys.exit(0)


######MAIN######

if __name__ == '__main__':
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        HOST = "localhost"
        PORT = 6666
        key = 128

        server_socket.bind((HOST, PORT))
        server_socket.listen(1)
        client_socket, address = server_socket.accept()
        with client_socket:
            print("Connected to client: ", address)
            while nb_joueurs < 2 :
                nb_joueurs = message_client(client_socket,"1 Nombre de joueurs", "int")
            with Manager() as manager:
                gros_dico = manager.dict()
                gros_dico = {}
                gros_dico["deck"] = deck(nb_joueurs)
                gros_dico["hand"] = hand(nb_joueurs,deck(nb_joueurs))
                gros_dico["suite"] = suite()
                gros_dico["information_token"] = information_token(nb_joueurs)
                gros_dico["fuze_token"] = fuze_token()
                gros_dico["turn"] = 0

                p = Process(target=player_main, args=(os.getpid(), key, gros_dico, client_socket, signal.SIGTERM, 0))
                p.start()
                child_processes.append(p.pid)

                for i in range(nb_joueurs - 1):
                    client_socket, address = server_socket.accept()
                    p = Process(target=player_main, args=(os.getpid(), key, gros_dico, client_socket, signal.SIGTERM, i + 1))
                    p.start()
                    child_processes.append(p.pid)

                gros_dico["turn"] = 1



                






