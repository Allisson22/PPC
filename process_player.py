import sysv_ipc
import socket
from multiprocessing import Process, Manager

def affichage_main(socket_player,hand,handplayer,digit):
    message_client(socket_player,f"0 Votre main :\n{handplayer}")
    for i in hand.keys() :
        if int(i) != digit :
            message_client(socket_player,f"0 Joueur {i} :\n{hand[i]}")
    

def message_client(socket_player,message,retour = "Nothing"):
    socket_player.sendall(message.encode())
    reponse = socket_player.recv(1024)
    if retour == "int" :
        try :
            reponse = int(reponse.decode())
        except :
            reponse = message_client(socket_player,message,retour)
    return reponse


def player_main(key,data,socket_player,digit_player) :
    que = sysv_ipc.MessageQueue(key, sysv_ipc.IPC_CREAT)
    on = True
    handplayer = [["inconnu","inconnu"],["inconnu","inconnu"],["inconnu","inconnu"],["inconnu","inconnu"],["inconnu","inconnu"]]
    while on :
        print(2,data["hand"])
        print(message_client(socket_player,f"0 {data['hand']}"))
        print(message_client(socket_player,"1 Nombre de joueurs"))




if __name__ == "__main__" :
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        HOST = "localhost"
        PORT = 1798
        key = 128

        server_socket.bind((HOST, PORT))
        server_socket.listen(1)
        client_socket, address = server_socket.accept()
        with Manager() as manager :
            data = manager.dict()
            data["hand"] = [("bleu",1),("rouge",5),("bleu",2),("jaune",2),("jaune",1)]
            print(1,data["hand"])
            player = Process(target=player_main, args=(key,data,client_socket))
            player.start()
            player.join()