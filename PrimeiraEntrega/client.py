from random import randint
from utils import *

class Client:
    def __init__(self, port):
        self.port = port
        self.client_socket = UDP(False)
        self.sendMessage()

    def sendMessage(self):
        while(True):
            # lê mensagem do teclado e envia ao servidor
            msg = input("manda uma mensagenzinha pro server: ")
            self.client_socket.rdt_send(msg.encode(), server_address)

            # recebe mensagem enviada
            data, _ = self.client_socket.rdt_rcv()
            print(data.decode())
if __name__ == "__main__":
    port = randint(3000,3100)
    print(port)
    Client(port)
    