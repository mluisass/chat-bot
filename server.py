from http import server
from utils import *
import threading as th
from datetime import datetime

class Server:
    # Inicialização do servidor
    def __init__(self):
        self.server_socket = UDP(True) # True => é servidor
        self.banned_users = []

        try:
            lock = th.Lock()
            send_thread = th.Thread(target = self.send_message, args=[lock])
            rcv_thread  = th.Thread(target = self.receive_message, args=[lock])
            
            send_thread.daemon  = True 
            rcv_thread.daemon   = True 

            send_thread.start()
            rcv_thread.start()

            send_thread.join()
            rcv_thread.join()

        except KeyboardInterrupt:
            self.server_socket.close()
    
    def send_message(self,lock):
        # Checa se há pacotes para ser enviados e os envia
        # Os pacotes a serem enviados podem ser reenvios, ACKS ou novas mensagens

        while True:
            lock.acquire()
            self.server_socket.check_pkt_buffer()
            [time, address, msg_received] = self.server_socket.check_ack('server')
            if msg_received:
                self.server_tasks(time, address, msg_received)
            self.server_socket.check_send_buffer('server')
            lock.release()
            
    def receive_message(self, lock):
        # Tenta receber um pacote
        # Cria o ACK referente a esse pacote e adiciona à lista de ACKs a serem enviados

        while(True):
            try:
                pkt, address , time =  self.server_socket.rdt_rcv()
                if pkt:
                    dic = eval(pkt.decode())
                    msg_rec = dic['data']
                    lock.acquire()
                    self.server_socket.add_ack(msg_rec, address, time)
                    lock.release()
                    print(msg_rec)

            except KeyboardInterrupt:
                self.server_socket.close()

    def broadcast(self, msg):
        # Adiciona ao buffer de mensagens a ser enviadas
        connected = self.server_socket.connected
        for address in connected.keys():
            self.server_socket.add_send_buffer(msg, address)
    
    def add_new_connection(self, user_name, address):
        # Inicia uma nova conexão
        # Verifica se esse usuário pode entrar no chat => se ele já tiver conectado ou já foi banido, ele não pode
        msg = ''
        already_connected = False
        connected = self.server_socket.connected
        for user_address in connected.keys():
                if connected[user_address]['user'] == user_name:
                    already_connected = True
                    break
                    
        if user_name not in self.banned_users and not already_connected:
            msg = '----------' + user_name + ' entrou no chat' + '----------'
            self.server_socket.connect(user_name, address)

        return msg

    def end_connection(self, address):
        user_name = self.server_socket.get_user_name(address)
        msg = ''
        if user_name:
            msg = '\n' + '----------' + user_name + ' saiu do chat' + '----------'
            self.server_socket.disconnect(address)

        return msg
        
    def server_tasks(self,time, address, msg_received):
        # Verifica que ação o servidor deve realizar:
            # 1. nova conexão
            # 2. bye
            # 3. list
            # 4. mensagem privada
            # 5. ban

            N = datetime.now()
            t = N.timetuple()

            _,_,_,h,min,sec,_,_,_ = t
                
            time = self.server_socket.get_str(h) + ':' + self.server_socket.get_str(min) + ':' + self.server_socket.get_str(sec)

            msg =  str(time) + ' ' + self.server_socket.get_user_name(address) + ': ' + str(msg_received)

            # 1. Nova conexão
            if len(msg_received) >= 17 and msg_received[:16] == 'hi, meu nome eh ':
                user_name = msg_received[16:]
                msg = self.add_new_connection(user_name, address)
                
            # 2. Desconectar usuário (bye)
            if msg_received == 'bye':
                msg = self.end_connection(address)

            # 3. Listar usuários conectados (list)
            if msg_received == 'list':
                msg = msg + '\n' + self.server_socket.get_connecteds()
                
            self.broadcast(msg)


    
if __name__ == "__main__":  
    Server()

    
