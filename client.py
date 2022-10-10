from random import randint
from utils import *
import threading as th
class Client:
    #inicializacao do cliente
    def __init__(self, port):
        self.port = port
        self.client_socket = UDP(False) # False => é cliente
        try:
            lock = th.Lock() 
            send_thread = th.Thread(target= self.sendMessage, args=[lock] )
            rcv_thread = th.Thread(target= self.receiveMessage, args=[lock])
            
            send_thread.daemon =True 
            rcv_thread.daemon= True 

            send_thread.start()
            rcv_thread.start()

            send_thread.join()
            rcv_thread.join()

        except KeyboardInterrupt:
            self.client_socket.close()

    #envia uma mensagem e recebe de volta
    def sendMessage(self,lock):
        while(True):
            # lê mensagem do teclado e envia ao servidor
            msg = input("Digite mensagem a ser enviada ao servidor com no máximo 1000 caracteres: ")
            lock.acquire()
            self.client_socket.rdt_send(msg, SERVER_ADDRESS)
            lock.release()  
        
    def receiveMessage(self, lock):
        while(True):
            lock.acquire()
            data, _ = self.client_socket.rdt_rcv()
            lock.release()
            msg = eval(data.decode())
            print(msg['data'])
if __name__ == "__main__":
    port = randint(3000,3100)
    print(port)
    Client(port)

# Cliente:
# Precisa sempre estar disponível para receber e mandar

# Threads:
# 1. Receber mensagem
# 2. Enviar mensagem