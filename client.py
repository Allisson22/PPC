import socket

HOST = "localhost"
PORT = 6816

def choix() :
    rep = input("réponse> ")
    if rep == "":
        rep = choix()
    return rep


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((HOST, PORT))
        on = True
        while on :
            mess = client_socket.recv(1024).decode()
            val, message = mess[0], mess[2:]
            print(message)
            if int(val) == 1 :
                rep = choix()
                client_socket.sendall(rep.encode())
            elif int(val) == 2 :
                on = False
            else :
                client_socket.sendall('Nothing'.encode())
            
