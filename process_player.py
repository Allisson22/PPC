import sysv_ipc
import socket
from multiprocessing import Process, Manager
import time
from random import *
import threading

def action_possible(socket_player,digit,data,handplayer):
    message_client(socket_player,"0 C'est votre tour, voud pouvez :\n  Donner informations\n  Jouer une carte sur une suite")
    reponse = message_client(socket_player,"1 information ou jouer ?",["information","jouer"])
    if reponse == "information" :
        if data["information_token"] > 0 :
            l = [f"{i}" for i in range(1,data["nb_joueurs"]+1)]
            l.pop(digit)
            joueur = message_client(socket_player,f"1 Quel Joueur ? (de 1 à {data['nb_joueurs']} sans {digit+1})",l)
            type = message_client(socket_player,"1 couleur ou numéro ?",["couleur","numéro"])
            if type == "couleur" :
                val = message_client(socket_player,f"1 Quelle couleur ? ({data['couleurs']})",data['couleurs'])
            elif type == "numéro" :
                val = message_client(socket_player,"1 Quel numéro ? (de 1 à 5)",["1","2","3","4","5"])
            annoncer_cartes(int(joueur),val,digit,data)
        else :
            message_client(socket_player,"0 Vous n'avez plus de jetons d'information")
            action_possible(socket_player,digit,data)
    if reponse == "jouer" :
        carte = message_client(socket_player,"1 Quelle carte ? (de 1 à 5)",["1","2","3","4","5"])
        jouer_carte(int(carte)-1,digit,data,handplayer)

def jouer_carte(index_carte,digit,data,handplayer):
    (couleur,num) = data["hand"][f"{digit}"].pop(index_carte)
    if data["suite"][couleur][num] == False and data["suite"][couleur][num-1] == True :
        data["suite"][couleur][num] == True
        if num == 5 :
            data["information_token"] += 1
    else :
        data["fuse_token"] -=1
        if num == 5 :
            data["fuse_token"] = 0
    nouvelle_carte = data["deck"].pop(random.randint(0,len(data["deck"]-1)))
    handplayer[index_carte] = ["?","?"]
    data["hand"][f"{digit}"].insert(index_carte,nouvelle_carte)

def annoncer_cartes(joueur,val,digit,data):
    message = f"Joueur {digit+1} a annoncé au Joueur {joueur} ses cartes {val}"
    que = sysv_ipc.MessageQueue(data["key"])
    data["information_token"] -=1
    for i in range(data['nb_joueurs']) :
        if i != digit :
            que.send(message.encode(), type = i)

def receive_message(socket_player,digit,handplayer,data):
    while True :
        que = sysv_ipc.MessageQueue(data["key"])
        message,_ = que.receive(type = digit)
        message = message.decode()
        info = message.split()
        if info[6] == f"{digit+1}":
            val = info[9]
            for i in range(5):
                for j in range(2):
                    if data["hand"][f"{digit}"][i][j] == val:
                        handplayer[i][j] = val
            message_client(socket_player,f"0 Le joueur {info[1]} vous a annoncé vos cartes {val}, voici votre main :\n  {handplayer}")
        else :
            message_client(socket_player,f"0 {message}")


def affichage_main(socket_player,hand,handplayer,digit):
    message_client(socket_player,f"0 Votre main :\n  {handplayer}")
    for i in hand.keys() :
        if int(i) != digit :
            message_client(socket_player,f"0 Joueur {int(i)+1} :\n  {hand[i]}")

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
                for t in range(len(data['couleurs'][j])-1) :
                    message += " "
        message_client(socket_player,message)
    message_client(socket_player,f"0 Votre main :\n  {handplayer}")
    for i in data["hand"].keys() :
        if int(i) != digit :
            message_client(socket_player,f"0 Joueur {int(i)+1} :\n  {data['hand'][i]}")


def message_client(socket_player,message,retour = "Nothing"):
    socket_player.sendall(message.encode())
    reponse = socket_player.recv(1024).decode()
    if retour != "Nothing" and reponse not in retour:
        reponse = message_client(socket_player,message,retour)
    return reponse


def player_main(data,socket_player,digit_player) :
    on = True
    handplayer = [["?","?"],["?","?"],["?","?"],["?","?"],["?","?"]]
    message_client(socket_player,f"0 Vous êtes le joueur {digit_player+1}")
    affichage_main(socket_player,data["hand"],handplayer,digit_player)
    thread1 = threading.Thread(target=receive_message, args=(socket_player,digit_player,handplayer,data))
    thread1.start()
    if data["turn"] == -1 :
        message_client(socket_player,"0 En attente de joueur")
    while data["turn"] == -1 :
        pass
    message_client(socket_player,"0 Le jeu commence !")
    while on :
        if data["turn"] % data["nb_joueurs"] == digit_player :
            affichage_utilitaire(socket_player,data,digit_player,handplayer)
            time.sleep(5)
            action_possible(socket_player,digit_player,data,handplayer)
            data["turn"] +=1

            

