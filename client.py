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
            send_thread = th.Thread(target= self.send_message, args=[lock] )
            rcv_thread = th.Thread(target= self.receive_message, args=[lock])
            write_thread = th.Thread(target= self.read_massage , args = [lock])

            send_thread.daemon =True 
            rcv_thread.daemon= True 

            send_thread.start()
            rcv_thread.start()

            send_thread.join()
            rcv_thread.join()

        except KeyboardInterrupt:
            self.client_socket.close()

    def send_message(self,lock):
        # Checa se há pacotes para ser enviados e os envia
        # Os pacotes a serem enviados podem ser reenvios, ACKS ou novas mensagens

        leave = False
        while not leave:
            lock.acquire()
            self.client_socket.check_pkt_buffer()
            leave = self.client_socket.check_ack('client')
            self.client_socket.check_send_buffer('client')
            lock.release()
            
            
    def receive_message(self, lock):
        # Tenta receber um pacote
        # Cria o ACK referente a esse pacote e adiciona à lista de ACKs a serem enviados
        while(True):
            try:
                pkt, address , time =  self.client_socket.rdt_rcv()
                if pkt:
                    lock.acquire()
                    data, _ = self.client_socket.rdt_rcv()
                    lock.release()
                    msg = eval(data.decode())
                    print(msg['data'])
            
    def read_message(self, lock):
        # Verifica eventos de teclado (input) e adiciona no buffer de mensagens a serem enviadas
        while True:
            try: 
                msg = input()
            except EOFError:
                break
            
            lock.acquire()
            self.client_socket.add_send_buffer(msg)
            lock.release()
            
            if msg == 'bye':
                break

if __name__ == "__main__":
    port = randint(3000,3100)
    print(port)
    Client(port)
