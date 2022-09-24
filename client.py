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
            msg = input("Digite mensagem a ser enviada ao servidor: ")
            self.client_socket.rdt_send(msg, server_address)

            # recebe mensagem enviada
            data, _ = self.client_socket.rdt_rcv()
            msg = eval(data.decode())

            print("Mensagem enviada: " + msg['data'])

if __name__ == "__main__":
    port = randint(3000,3100)
    print(port)
    Client(port)
    