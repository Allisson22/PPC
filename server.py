from random import *
from multiprocessing import Process, Manager
import socket
import sysv_ipc

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

def client_handler(s, a):
    with s:
        print("Connected to client: ", a)
        data = s.recv(1024)
        while len(data):
            s.sendall(data)
            data = s.recv(1024)
        print("Disconnecting from client: ", a)
            


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
                gros_dico["hand"] = hand(2,deck(2))
                gros_dico["suite"] = suite()
                gros_dico["information_token"] = information_token(nb_joueurs)
                gros_dico["fuze_token"] = fuze_token()

                p = Process(target=player_main, args=(client_socket, address))
                p.start()
             
        for i in range (nb_joueurs-1):
            client_socket, address = server_socket.accept()
            p = Process(target=player_main, args=(client_socket, address, i+1))
            p.start()






