import sysv_ipc
import socket
from multiprocessing import Process, Manager
import time
from random import *

def action_possible(socket_player,nb_player,couleurs,digit,data,key):
    message_client(socket_player,"0 C'est votre tour, voud pouvez :\n  Donner informations\n  Jouer une carte sur une suite")
    reponse = message_client(socket_player,"1 information ou jouer ?",["information","jouer"])
    if reponse == "information" :
        if data["information_token"] > 0 :
            l = [f"{i}" for i in range(1,nb_player+1)]
            l.pop(digit)
            joueur = message_client(socket_player,f"1 Quel Joueur ? (de 1 à {nb_player} sans {digit+1})",l)
            type = message_client(socket_player,"1 couleur ou numéro ?",["couleur","numéro"])
            if type == "couleur" :
                val = message_client(socket_player,f"1 Quelle couleur ? ({couleurs})",couleurs)
            elif type == "numéro" :
                val = message_client(socket_player,"1 Quel numéro ? (de 1 à 5)",["1","2","3","4","5"])
            annoncer_cartes(int(joueur)-1,val,digit,key,nb_player,data)
        else :
            message_client(socket_player,"0 Vous n'avez plus de jetons d'information")
            action_possible(socket_player,nb_player,couleurs,digit,data,key)
    if reponse == "jouer" :
        carte = message_client(socket_player,"1 Quelle carte ? (de 1 à 5)",["1","2","3","4","5"])
        jouer_carte(int(carte)-1,digit,data)

def jouer_carte(index_carte,digit,data):
    (couleur,num) = data["hand"][f"{digit}"].pop(index_carte)
    if data["suite"][couleur][num] == False and data["suite"][couleur][num-1] == True :
        data["suite"][couleur][num] == True
    else :
        data["fuse_token"] -=1
        if num == 5 :
            #annoncer au main_server que c'est fini
            pass
    nouvelle_carte = data["deck"].pop(random.randint(0,len(data["deck"]-1)))
    data["hand"][f"{digit}"].insert(index_carte,nouvelle_carte)

def annoncer_cartes(joueur,val,digit,key,nb_player,data):
    message = f"Joueur {digit} a annoncé au Joueur {joueur} ses cartes {val}"
    que = sysv_ipc.MessageQueue(key)
    data["information_token"] -=1
    for i in range(nb_player) :
        if i != digit :
            que.send(message.encode(), type = i)

def receive_message(socket_player,key,digit,handplayer,hand):
    while True :
        que = sysv_ipc.MessageQueue(key)
        message = que.receive(type = digit).decode()
        info = message.split()
        if info[6] == f"{digit}":
            val = info[9]
            for i in range(5):
                for j in range(2):
                    if hand[i][j] == val:
                        handplayer[i][j] = val
            message_client(socket_player,f"0 Le joueur {info[1]} vous a annoncé vos cartes {val}, voici votre main :\n  {handplayer}")
        else :
            message_client(socket_player,f"0 {message}")


def affichage_main(socket_player,hand,handplayer,digit):
    message_client(socket_player,f"0 Votre main :\n  {handplayer}")
    for i in hand.keys() :
        if int(i) != digit :
            message_client(socket_player,f"0 Joueur {i} :\n  {hand[i]}")

def affichage_utilitaire(socket_player,data,digit,handplayer):
    message_client(socket_player,f"0 Il reste {data['fuse_token']} jetons d'amorçage, {data['information_token']} jetons d'information")
    message_client(socket_player,f"0 Voici l'état des suites :")
    for i in range(6):
        message = "0 "
        for j in range(len(data["couleurs"])) :
            if i == 1:
                message += f"{data['couleurs'][j]}  "
            else :
                if data["suite"][data['couleurs'][j]] == True :
                    message += f"{i}  "
                else :
                    message += "   "
                for t in range(len(data['couleurs'][j])) :
                    message += " "
        message_client(socket_player,message)
    message_client(socket_player,f"0 Votre main :\n  {handplayer}")
    for i in data["hand"].keys() :
        if int(i) != digit :
            message_client(socket_player,f"0 Joueur {i} :\n  {data['hand'][i]}")


    

def message_client(socket_player,message,retour = "Nothing"):
    socket_player.sendall(message.encode())
    reponse = socket_player.recv(1024).decode()
    if retour != "Nothing" and reponse not in retour:
        reponse = message_client(socket_player,message,retour)
    return reponse


def player_main(key,data,socket_player,digit_player) :
    on = True
    handplayer = [["?","?"],["?","?"],["?","?"],["?","?"],["?","?"]]
    nb_player = 4
    couleurs =  ["bleu","rouge","jaune","vert"]
    while on :
        affichage_main(socket_player,data["hand"],handplayer,digit_player)
        time.sleep(15)
        action_possible(socket_player,nb_player,couleurs,digit_player,data,key)
        time.sleep(10000)
        





if __name__ == "__main__" :
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        HOST = "localhost"
        PORT = 1800
        key = 128

        server_socket.bind((HOST, PORT))
        server_socket.listen(1)
        client_socket, address = server_socket.accept()
        que = sysv_ipc.MessageQueue(key, sysv_ipc.IPC_CREAT)
        with Manager() as manager :
            data = manager.dict()
            data["hand"] = {"0" : [("bleu",1),("rouge",5),("bleu",2),("jaune",2),("jaune",1)], "1" : [("bleu",1),("rouge",5),("bleu",2),("jaune",2),("jaune",1)], "2" : [("bleu",1),("rouge",5),("bleu",2),("jaune",2),("jaune",1)] }
            player = Process(target=player_main, args=(key,data,client_socket,1))
            player.start()
            player.join()