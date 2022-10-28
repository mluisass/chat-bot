from random import randint
from utils import *
import threading as th
class Client:
    def __init__(self):
        # Inicia o socket
        self.client_socket = UDP(False) # False => é cliente

        try:
            lock = th.Lock() 
            send_thread = th.Thread(target= self.send_message, args=[lock] )
            rcv_thread = th.Thread(target= self.receive_message, args=[lock])
            input_thread = th.Thread(target= self.read_message , args=[lock])

            send_thread.daemon =True 
            rcv_thread.daemon = True 
            input_thread.daemon =True

            send_thread.start()
            rcv_thread.start()
            input_thread.start()

            send_thread.join()
            rcv_thread.join()
            input_thread.join()
            
        except KeyboardInterrupt:
            self.client_socket.close()

    def send_message(self, lock):
        # Checa se há pacotes para ser enviados e os envia
        # Os pacotes a serem enviados podem ser reenvios, ACKS ou novas mensagens

        leave = False
        while not leave:
            lock.acquire()
            self.client_socket.check_pkt_buffer() # Reenvia pacotes que o timeout estourou
            _, _, msg = self.client_socket.check_ack('client') # Envia ACKs
            leave = msg == 'bye'
            self.client_socket.check_send_buffer() # Envia novas mensagens
            lock.release()
            
            
    def receive_message(self, lock):
        # Tenta receber um pacote
        # Cria o ACK referente a esse pacote e adiciona à lista de ACKs a serem enviados

        while(True):
            try:
                # OBS: recebe um pacote vazio quando a mensagem recebida for um ACK 
                # ou um pacote com numero de sequencia errado

                pkt, address , time =  self.client_socket.rdt_rcv()

                if pkt:
                    msg = eval(pkt.decode())
                    msg_rec = msg['data']

                    lock.acquire()
                    self.client_socket.add_ack(msg_rec, address, time)
                    lock.release()

                    print(msg_rec)
                    
            except KeyboardInterrupt:
                
                self.client_socket.close()
                
    def read_message(self, lock):
        # Verifica eventos de teclado (input) e adiciona no buffer de mensagens a serem enviadas
        while True:
            try: 
                msg = input()
                print("\033[A                             \033[A")
            except EOFError:
                break
            
            lock.acquire()
            self.client_socket.add_send_buffer(msg, self.client_socket.server_address)
            lock.release()
            
            if msg == 'bye':
                break

if __name__ == "__main__":
    Client()
