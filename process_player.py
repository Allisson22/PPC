import sysv_ipc
import socket
from multiprocessing import Process, Manager




def player_main(key,data,socket_player) :
    que = sysv_ipc.MessageQueue(key, sysv_ipc.IPC_CREAT)
    on = True
    while on :
        print(2,data["hand"])
        mess = f"0 {data[f'hand']}"
        socket_player.sendall(mess.encode())
        _ = socket_player.recv(1024)
        mess = "1 Nombre de joueurs"
        socket_player.sendall(mess.encode())
        mess = client_socket.recv(1024).decode()
        print(mess)




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