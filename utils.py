SERVER_ADDRESS = ("0.0.0.0", 20001)
BUFFER_SIZE = 1024
from datetime import datetime
import socket

class UDP:
    #inicializaçao
    def __init__(self, server):
        # server => true or false
        self.UDPsocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.sequence = 0
        
        self.send_buffer = [] # Mensagens a serem enviadas
        self.pkt_buffer = {} # Pacotes enviados sem confirmação (ACK)
        self.delete_buffer = []
        self.connecteds = {}
        self.acks = [] # ACKs a serem enviados
        self.bye = False
        if (server):
            self.UDPsocket.bind(SERVER_ADDRESS)
            print("Servidor ligado")
        
    #recebimento de pacote
    def __receive(self):
        package, address = self.UDPsocket.recvfrom(BUFFER_SIZE)
        return (package,address)
    
    # envio de pacote 
    def __send(self, package, address):
        self.UDPsocket.sendto(package, address) # para o cliente: address = SERVER_ADDRESS
    
    # encerra a conexão
    def close(self):
        print("\nConexão encerrada")
        self.UDPsocket.close()
    
    # envio de um pacote
    def rdt_send(self, msg,time, address):
        # Fazer o pacote
        # Se a msg é ACK
        # Colocar o numero de seq
        # Colocar o pacote enviado no buffer
        
        now = str(datetime.now())

        if msg.decode() == "ACK":
            # Se a mensagem é um ACK, eu sou um receptor
            # Então, envio o ACK para o endereço e atualizo o número de sequência

            pkt = self.__make_pkt(msg, self.get_sequence('receiver'),time)
            self.__send(pkt,address)
            self.__update_sequence('receiver',address)
        else:
            # Se não for um ACK, eu um sender querendo enviar uma mensagem
            # Então, crio o pacote, envio e salvo o pacote enviado em um buffer pra 
            # posterior reenvio (estouro do temporizador)

            pkt = self.__make_pkt(msg, self.get_sequence('sender'),now)
            self.pkt_buffer[now] = {
                'pkt': pkt,
                'address': address
            }
            self.__send(pkt,address)

            # Checa se a mensagem a ser enviada é um 'bye', indicando que o cliente será desconectado
            if msg.decode() == "bye":
                self.bye = True
            

    #recebe um pacote e checa o conteudo 
    def rdt_rcv(self):
        msg, address = self.__receive() #recebe um pacote
        #check_seq = self.__check_seq(msg,'receiver') # checa o numero de sequencia (True => OK)
        dic = eval(msg.decode())
        time = dic['time']
        
        # Se a mensagem recebida foi um ACK, eu sou um sender
        # Então, checo se o número de sequência era o que eu tava esperando
        # Se a mensagem não for um ACK 
        if self.__is_ack(dic) and self.__check_seq(msg,address, 'sender'):
            self.delete_buffer.append(time) # A mensagem foi recebida corretamente e pode ser deletada do pkt_buffer
            self.__update_sequence('sender',address)
            return msg, address, time
        
        elif not self.__is_ack(dic) and self.__check_seq(msg,address, 'receiver'):
            
            return msg, address, time

        return '',address,time        

    # verifica se a mensagem é um ACK
    def __is_ack(self, msg):
        data = eval(msg.decode())
        return (data['data'] == 'ACK')
    
    #cria o pacote com cabeçalho
    def __make_pkt(self , msg, seq):
        return str({
            'data':msg,
            'seq':seq}).encode()
            
    #atualiza o numero de sequencia
    def __update_sequence(self):
        self.sequence = 1 - self.sequence

    #verifica se o pacote recebido foi o esperado
    def __check_seq(self, msg, type='sender'):
        data = eval(msg.decode())
        seq = self.get_sequence(type, address)
        # se tem nº de sequência antigo
        if seq != data['seq']:
            return False
        
        # caso seja transmissor, atualiza o numero de sequencia

        return True

    def add_send_buffer(self, msg, address = SERVER_ADDRESS):
        # Adiciona mensagem ao buffer de mensagens a serem enviadas
    
        self.send_buffer.append((msg,address))
        # TODO :  ver se eh mais fácil já colocar todos os destinatarios aqui

    def check_pkt_buffer(self):
        for time in self.delete_buffer:
            if time in self.buffer:
                del self.buffer[time]

        self.delete_buffer = []
        todelete = []
    
        for time in self.buffer:
            now = datetime.now()
            t = datetime.strptime(time, '%Y-%m-%d %H:%M:%S.%f')
            t = now - t 
            if t.seconds > 0:
                todelete.append(time)
        
        for time in todelete:
            pkt = self.buffer[time]['pkt']
            address = self.buffer[time]['address']

            del self.buffer[time]

            dic = eval(pkt.decode())
            msg = dic['data']
            self.rdt_send(msg, 0, address)
        # Remove do buffer mensagens já enviadas


    def get_sequence(self):
        # TODO: isso daqui tem que trocar, tem que ter um numero de sequencia de receiver
        # e de sender para cada um dos conectados
        return self.sequence
    
    def check_ack(self, type):
        # Checa se existem ACKs a serem enviados e envia
        # Caso o ACK seja para um 'bye', retorna True, indicando que o usuário será desconectado
        
        if len(self.acks):
            a = self.acks[0]

            msg= a[0]
            time= a[1]
            address = a[2]
            msg_received = a[3]
            
            self.rdt_send(msg,time,address)
            self.acks.pop(0)
            
            if type == "client" and self.bye == True:
                return True
                
            if type == "server" and msg_received:
                # Faz todas as verificações que o servidor deve fazer:
                # 1. bye
                # 2. list
                # 3. ban
                # 4. mensagem privada

                N = datetime.now()
                t = N.timetuple()
                _,_,_,h,min,sec,_,_,_ = t
                
                time = self.get_str(h) + ':' + self.get_str(min) + ':' + self.get_str(sec)

                msg =  str(time) + ' ' + self.get_user(address) + ': ' + msg_received
                
                if len(msg_received) >= 17 and msg_received[:16] == 'hi, meu nome eh ':
                    msg = '----------' + self.get_user(address) + ' got in the chat' + '----------'

                if msg_received == 'bye':
                    msg_bye = msg + '\n' + '----------' + self.get_user(address) + ' left the chat' + '----------'
                    self.add_send_buffer(msg_bye.encode(), address, 1)

                    self.send_buffer.append((msg.encode(), address, address))
                elif msg_received == 'list':
                    msg_list = msg + '\n' + self.get_connecteds()
                    self.add_send_buffer(msg_list.encode(), address)
                else:
                    self.add_send_buffer(msg.encode(), address)
                
    def get_connecteds(self):
        msg_list = '---- users list ----'
        for address in self.connecteds:
            msg_list += '\n' + str(self.connecteds[address]['user'])
        msg_list += '\n--------------------'
        return msg_list
        
    def get_str(self, t):
        if t < 10:
            return '0' + str(t)
        
        return str(t)

    def check_send_buffer(self,type):
        # Checa se existe alguma mensagem para enviar e envia
        # Caso seja o servidor e a mensagem enviada for um 'bye', desconecta o usuário que enviou o 'bye'

        if len(self.send_buffer):
            a = self.send_buffer[0]
            pkt = a[0]
            address_to = a[1]
            self.rdt_send(pkt,0,address_to)
            self.send_buffer.pop(0)
            
            if type =='server':
                msg= pkt.decode().split(' ')
                if len(msg) == 3 and msg[2] =='bye':
                    self.disconnect(address_to)