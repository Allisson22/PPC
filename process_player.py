import sysv_ipc
import socket
from multiprocessing import Process, Manager
import time

def action_possible(socket_player,nb_player,couleurs):
    message_client(socket_player,"0 C'est votre tour, voud pouvez :\n  Donner informations\n  Jouer une carte sur une suite")
    reponse = message_client(socket_player,"1 information ou jouer ?",["information","jouer"])
    if reponse == "information" :
        joueur = message_client(socket_player,f"1 Quel Joueur ? (de 1 à {nb_player})",[f"{i}" for i in range(1,nb_player+1)])
        type = message_client(socket_player,"1 couleur ou numéro ?",["couleur","numéro"])
        if type == "couleur" :
            val = message_client(socket_player,"1 Quelle couleur ? ({couleurs})",couleurs)
        elif type == "numéro" :
            val = message_client(socket_player,"1 Quel numéro ? (de 1 à 5)",["1","2","3","4","5"])
        annoncer_cartes(joueur,val)
    if reponse == "jouer" :
        carte = message_client(socket_player,"1 Quelle carte ? (de 1 à 5)",["1","2","3","4","5"])
        jouer_carte(carte)


def affichage_main(socket_player,hand,handplayer,digit):
    message_client(socket_player, "0 ============================================")
    message_client(socket_player,f"0 Votre main :\n{handplayer}")
    for i in hand.keys() :
        if int(i) != digit :
            message_client(socket_player,f"0 Joueur {i} :\n{hand[i]}")
    

def message_client(socket_player,message,retour = "Nothing"):
    socket_player.sendall(message.encode())
    reponse = socket_player.recv(1024)
    if retour != "Nothing" and reponse not in retour:
        reponse = message_client(socket_player,message,retour)
    return reponse


def player_main(key,data,socket_player,digit_player) :
    que = sysv_ipc.MessageQueue(key, sysv_ipc.IPC_CREAT)
    on = True
    handplayer = [["inconnu","inconnu"],["inconnu","inconnu"],["inconnu","inconnu"],["inconnu","inconnu"],["inconnu","inconnu"]]
    while on :
        affichage_main(socket_player,data["hand"],handplayer,digit_player)
        time.sleep(100000)
        





if __name__ == "__main__" :
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        HOST = "localhost"
        PORT = 1799
        key = 128

        server_socket.bind((HOST, PORT))
        server_socket.listen(1)
        client_socket, address = server_socket.accept()
        with Manager() as manager :
            data = manager.dict()
            data["hand"] = {"0" : [("bleu",1),("rouge",5),("bleu",2),("jaune",2),("jaune",1)], "1" : [("bleu",1),("rouge",5),("bleu",2),("jaune",2),("jaune",1)], "2" : [("bleu",1),("rouge",5),("bleu",2),("jaune",2),("jaune",1)] }
            player = Process(target=player_main, args=(key,data,client_socket,1))
            player.start()
            player.join()