import sysv_ipc
import socket
from multiprocessing import Process, Manager
import time
from random import *
import threading
import signal
import os

def action_possible(socket_player,digit,data,handplayer):
    message_client(socket_player,"0 C'est votre tour, vous pouvez :\n  Donner informations\n  Jouer une carte sur une suite")
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
            action_possible(socket_player,digit,data,handplayer)
    if reponse == "jouer" :        
        carte = message_client(socket_player,f"1 Quelle carte ? (de 1 à {len(data['hand'][f'{digit}'])})",[f'{i}' for i in range(1,len(data['hand'][f'{digit}'])+1)])
        jouer_carte(int(carte)-1,digit,data,handplayer,socket_player)

def jouer_carte(index_carte,digit,data,handplayer,socket_player):
    pioche = data["deck"]
    main_joueur = data["hand"]
    (couleur,num) = main_joueur[f"{digit}"][index_carte]
    if data["suite"][couleur][num] == False and data["suite"][couleur][num-1] == True :
        suite_correcte = data["suite"]
        suite_correcte[couleur][num] = True
        data["suite"] = suite_correcte
        if num == 5 :
            data["information_token"] += 1
            message_client(socket_player,f"0 Vous avez posé un {num} {couleur}\n  +1 jeton d'information")
        else :
            message_client(socket_player,f"0 Vous avez posé un {num} {couleur}")
    else :
        data["fuse_token"] -=1
        message_client(socket_player,f"0 Vous avez posé un {num} {couleur}\n  -1 jeton d'amorçage")
        if num == 5 :
            data["fuse_token"] = 0
    if len(pioche) != 0 :
        nouvelle_carte = pioche.pop(randint(0,len(pioche)-1))
        data["deck"] = pioche
        handplayer[index_carte] = ["?","?"]
        main_joueur[f"{digit}"][index_carte] = nouvelle_carte
        data["hand"] = main_joueur
    else :
        handplayer.pop([index_carte])
        main_joueur[f"{digit}"].pop([index_carte])

    que = sysv_ipc.MessageQueue(data["key"])
    message = f"Joueur {digit+1} a joué un {num} {couleur}"
    for i in range(data['nb_joueurs']) :
        if i != digit :
            que.send(message.encode(), type = i+1)

def annoncer_cartes(joueur,val,digit,data):
    message = f"Joueur {digit+1} a annoncé au Joueur {joueur} ses cartes {val}"
    que = sysv_ipc.MessageQueue(data["key"])
    data["information_token"] -=1
    for i in range(data['nb_joueurs']) :
        if i != digit :
            que.send(message.encode(), type = i+1)

def receive_message(socket_player,digit,handplayer,data):
    while True :
        que = sysv_ipc.MessageQueue(data["key"])
        message,_ = que.receive(type = digit+1)
        message = message.decode()
        info = message.split()
        message_client(socket_player,f"0 ###")
        if info[3] == "annoncé" and info[6] == f"{digit+1}":
            val = info[9]
            for i in range(len(data["hand"][f"{digit}"])):
                for j in range(2):
                    if str(data["hand"][f"{digit}"][i][j]) == str(val):
                        handplayer[i][j] = val
            message_client(socket_player,f"0 Le joueur {info[1]} vous a annoncé vos cartes {val}, voici votre main :\n  {handplayer}")
        else :
            message_client(socket_player,f"0 {message}")
        message_client(socket_player,f"0 ###")



def affichage_main(socket_player,hand,handplayer,digit):
    message_client(socket_player,f"0 Votre main :\n  {handplayer}")
    for i in hand.keys() :
        if int(i) != digit :
            message_client(socket_player,f"0 Joueur {int(i)+1} :\n  {hand[i]}")

def affichage_utilitaire(socket_player,data,digit,handplayer):
    message_client(socket_player,"0 ===============================================================================================")
    message_client(socket_player,f"0 Il reste {data['fuse_token']} jetons d'amorçage, {data['information_token']} jetons d'information")
    message_client(socket_player,f"0 Voici l'état des suites :")
    for i in range(6):
        message = "0 "
        for j in range(len(data["couleurs"])) :
            if i == 0:
                message += f"{data['couleurs'][j]}  "
            else :
                if data["suite"][data['couleurs'][j]][i] == True :
                    message += f"{i}  "
                else :
                    message += "   "
                for _ in range(len(data['couleurs'][j])-1) :
                    message += " "
        message_client(socket_player,message)
    message_client(socket_player,f"0 Votre main :\n  {handplayer}")
    for i in data["hand"].keys() :
        if int(i) != digit :
            message_client(socket_player,f"0 Joueur {int(i)+1} :\n  {data['hand'][i]}")
    message_client(socket_player,"0 ===============================================================================================")


def message_client(socket_player,message,retour = "Nothing"):
    socket_player.sendall(message.encode())
    reponse = socket_player.recv(1024).decode()
    if retour != "Nothing" and reponse not in retour:
        reponse = message_client(socket_player,message,retour)
    return reponse


def player_main(data,socket_player,digit_player,sem_server,sem_player) :
    on = True
    def handler(sig, _):
            if sig == signal.SIGUSR1 :
                if data["victoire"] :
                    message_client(socket_player, '0 Vous avez GAGNÉ !!!!!')
                    os.kill(os.getpid(), signal.SIGKILL)
                else :
                    message_client(socket_player, '0 Le deck est vide')
                    os.kill(os.getpid(), signal.SIGKILL)
            if sig == signal.SIGUSR2 :
                message_client(socket_player, '0 Un 5 a été défaussé')
                os.kill(os.getpid(), signal.SIGKILL)
            if sig == signal.SIGINT :
                message_client(socket_player, "0 Tous les jetons d'amorçage ont été utilisés")
                os.kill(os.getpid(), signal.SIGKILL)

    signal.signal(signal.SIGUSR1, handler)
    signal.signal(signal.SIGUSR2, handler)
    signal.signal(signal.SIGINT, handler)
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
            sem_player.acquire()
            affichage_utilitaire(socket_player,data,digit_player,handplayer)
            action_possible(socket_player,digit_player,data,handplayer)
            message_client(socket_player,"0 Fin de votre tour")
            data["turn"] +=1
            sem_server.release()

            

