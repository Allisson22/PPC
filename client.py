import socket

HOST = "localhost"
PORT = 6761


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((HOST, PORT))
        on = True
        while on :
            mess = client_socket.recv(1024).decode()
            print(mess)
            val, message = mess[0], mess[2:]
            print(message)
            if int(val) == 1 :
                rep = input("réponse> ")
                client_socket.sendall(rep.encode())
            elif (message == "Fermeture") :
                 on = False
                
            else :
                client_socket.sendall('Nothing'.encode())
            

