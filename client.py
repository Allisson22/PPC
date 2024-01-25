import socket

HOST = "localhost"
PORT = 6812


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((HOST, PORT))
        on = True
        while on :
            mess = client_socket.recv(1024).decode()
            val, message = mess[0], mess[2:]
            print(message)
            if int(val) == 1 :
                rep = input("réponse> ")
                client_socket.sendall(rep.encode())
            elif (message == "Le deck est vide" or message == "Tous les fuze token ont été utilisés" or message == "Un 5 a été défaussé") :
                on = False
            else :
                client_socket.sendall('Nothing'.encode())
            
