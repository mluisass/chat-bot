from http import server
from math import ceil
from utils import *
import threading as th
from datetime import datetime, timedelta

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
            self.server_socket.check_send_buffer()
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
        #print(connected)
        for address in connected.keys():
            self.server_socket.add_send_buffer(msg, address)
    
    def add_new_connection(self, user_name, address):
        # Inicia uma nova conexão
        # Verifica se esse usuário pode entrar no chat => se ele já tiver conectado ou já foi banido, ele não pode
        msg = ''
        
        if user_name not in self.banned_users and not self.server_socket.find_address(user_name):
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

    def ban_user(self, user, msg):
        # Procura usuário na lista de conectados e aumenta em 1 o seu ban_count
        # Verifica se já atingiu 2/3 de conectados
            # Caso tenha, bane => disconnect(address)
            # Mensagem => usuário foi banido do chat

        connected = self.server_socket.connected
        banned_address = self.server_socket.find_address(user)
        
        if banned_address:
            time = datetime.now()
            print(time - connected[banned_address]['ban']['time'])
            if time - connected[banned_address]['ban']['time'] <  timedelta(seconds=10):
                return msg  
            
            self.server_socket.connected[banned_address]['ban']['count'] += 1
            self.server_socket.connected[banned_address]['ban']['time'] = time

            if self.server_socket.connected[banned_address]['ban']['count'] >= ceil((2/3)*len(connected)):
                self.banned_users.append(user)
                
                msg += '\n' + '----------' + user + ' foi banido do chat ----------'
    
        return msg
    
    def __get_str(self, t):
        if t < 10:
            return '0' + str(t)
        
        return str(t)
    
    def server_tasks(self,time, address, msg_received):
        # Verifica que ação o servidor deve realizar:
            # 1. nova conexão
            # 2. bye
            # 3. list
            # 4. mensagem privada
            # 5. ban

            _,_,_,h,min,sec,_,_,_ = datetime.now().timetuple()
                
            time = self.__get_str(h) + ':' + self.__get_str(min) + ':' + self.__get_str(sec)

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

            if msg_received[:5] == 'ban @':
                user_name = msg_received[5:]
                msg = self.ban_user(user_name, msg)

            if msg_received[0] == '@':
                user_name, _ = msg_received[1:].split(' ', 1)
                priv_address = self.server_socket.find_address(user_name)

                if priv_address:
                    self.server_socket.add_send_buffer(msg, priv_address)
                    self.server_socket.add_send_buffer(msg, address)
                return
            
            self.broadcast(msg)

            if len(self.banned_users):
                banned_address = self.server_socket.find_address(self.banned_users[-1])
                self.server_socket.disconnect(banned_address)

        
    
if __name__ == "__main__":  
    Server()

    
