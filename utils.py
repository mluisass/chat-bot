SERVER_ADDRESS = ("0.0.0.0", 20001)
BUFFER_SIZE = 1024
from datetime import datetime
import socket

class UDP:
    def __init__(self, server):
        # server => true or false
        self.UDPsocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.sequence = 0
        
        self.send_buffer = [] # Mensagens a serem enviadas
        self.pkt_buffer = {} # Pacotes enviados sem confirmação (ACK)
        self.delete_buffer = []
        self.connected = {}
        self.ack_buffer = [] # ACKs a serem enviados
        self.bye = False

        self.server = server 

        self.server_address = SERVER_ADDRESS

        if server:
            self.UDPsocket.bind(SERVER_ADDRESS)
            print("Servidor ligado")
    
    def __receive(self):
        #Recebimento de pacote

        package, address = self.UDPsocket.recvfrom(BUFFER_SIZE)

        # Caso seja o cliente, precisa conhecer o endereço do servidor
        if not self.server and address not in self.connected:
            self.server_address = address
            self.connect("server", address)

        return (package,address)
    
    # ------------------------ Número de Sequência ---------------------------------

    def __get_sequence(self, type, address):
        # Retorna o número de sequência referente a um endereço em específico 
        # Cada endereço (usuário) possui um número de sequência para seu modo receptor e transmissor

        if address in self.connected:
            return self.connected[address]['seqNumber'][type]
        return 0

    def __check_seq(self, pkt, address, type = 'sender'):
        # Verifica se o pacote recebido foi o esperado
        # Ou seja, se o número de sequência do pacote é o mesmo armazenado

        msg = eval(pkt.decode())
        seq = self.__get_sequence(type, address)

        return seq == msg['seq']

    def __update_sequence(self, type, address):
        # Atualiza o numero de sequência
        if address in self.connected:
            self.connected[address]['seqNumber'][type] = 1 - self.__get_sequence(type, address)
            self.sequence = self.__get_sequence(type, address)
    
    # ------------------------ Preparar/transmitir mensagem (send) ---------------------------------

    def __send(self, package, address):
        # Envio de pacote 
        self.UDPsocket.sendto(package, address)

    def __make_pkt(self , msg, seq, time):
        # Cria o pacote com cabeçalho
        return str({
            'data':msg,
            'seq':seq,
            'time': time}).encode()

    def __rdt_send(self, msg, time, address):
        # Prepara um pacote e envia
        if msg == "ACK":
            # Se a mensagem é um ACK, eu sou um receptor
            # Então, envio o ACK para o endereço e atualizo o número de sequência
            pkt = self.__make_pkt(msg, self.__get_sequence('receiver', address), time)
            self.__send(pkt, address)
            self.__update_sequence('receiver',address)

        else:
            # Se não for um ACK, e um sender querendo enviar uma mensagem
            # Então, crio o pacote, envio e salvo o pacote enviado em um buffer pra 
            # um (possível) posterior reenvio (estouro do temporizador)

            now = str(datetime.now()) # O pacote deve ser enviado com o tempo atual

            self.__update_sequence('sender', address)
            pkt = self.__make_pkt(msg, self.__get_sequence('sender', address), now)
            
            self.pkt_buffer[now] = {
                'pkt': pkt,
                'address': address
            }
            
            self.__send(pkt, address)

            # Checa se a mensagem a ser enviada é um 'bye', indicando que o cliente será desconectado
            if msg == "bye":
                self.bye = True      

    def check_ack(self, type):
        # Checa se existem ACKs a serem enviados e envia
        # Caso o ACK seja para um 'bye', retorna True, indicando que o usuário será desconectado

        if len(self.ack_buffer):
            [msg, time, address, msg_received] = self.ack_buffer[0]
            self.ack_buffer.pop(0)

            if address:
                self.__rdt_send(msg, time, address)
            
            if type == "client" and self.bye == True:
                return time, address, 'bye'
                
            if type == "server" and msg_received:
                return time, address, msg_received
        return '', ('',0), ''

    def check_send_buffer(self):
        # Checa se existe alguma mensagem nova para enviar e envia
        # Caso seja o servidor e a mensagem enviada for um 'bye', desconecta o usuário que enviou o 'bye'

        if len(self.send_buffer):
            # Envia primeira mensagem do buffer
            msg, address_to = self.send_buffer[0]
            self.send_buffer.pop(0)
            self.__rdt_send(msg, 0, address_to)
             
        

    def check_pkt_buffer(self):
        # Deleta do buffer de pacotes enviados aqueles que receberam ACK
        # OBS: os pacotes são referenciados pelo tempo em que foram enviados

        for time in self.delete_buffer:
            if time in self.pkt_buffer:
                del self.pkt_buffer[time]

        self.delete_buffer = [] # Reseta pq todos já foram apagados do buffer
        
        # Os que sobraram no buffer devem ser reenviados
        to_resend = []
        for time in self.pkt_buffer:
            now = datetime.now() # Atualiza o tempo, porque o pacote deve será reenviado

            t = datetime.strptime(time, '%Y-%m-%d %H:%M:%S.%f') # Converte a string em tempo
            t = now - t # Verifica a diferença de tempo entre o tempo original e o tempo atual

            # Se o pacote não foi o que eu LITERALMENTE acabei de mandar (ou seja, se ele é antigo)
            if t.seconds > 0:
                to_resend.append(time)

        for time in to_resend:
            # Pega o pacote que foi enviado no tempo
            pkt = self.pkt_buffer[time]['pkt']
            address = self.pkt_buffer[time]['address']
            
            del self.pkt_buffer[time] # Deleta do buffer, pq no rdt_send vou colocar de novo

            dic = eval(pkt.decode())
            msg = dic['data']
            self.__rdt_send(msg, 0, address) # Reenvia mensagem

    # ------------------------ Receber mensagem ---------------------------------

    def __is_ack(self, msg):
        # Verifica se a mensagem é um ACK
        return (msg['data'] == 'ACK')

    def rdt_rcv(self):
        # Recebe um pacote e checa o conteúdo

        pkt, address = self.__receive() # Recebe um pacote
        msg = eval(pkt.decode())
        time = msg['time']

        if not self.__is_ack(msg) and self.__check_seq(pkt, address, 'receiver'):
            # Se a mensagem não for um ACK eu retorno o pacote recebido
            return pkt, address, time
        
        # Se a mensagem recebida foi um ACK, eu sou um transmissor que recebeu confirmação do pacote transmitido
        # Então, checo se o número de sequência era o que eu tava esperando
        if self.__is_ack(msg) and self.__check_seq(pkt, address, 'sender'):
            self.delete_buffer.append(time) # A mensagem foi recebida corretamente e pode ser deletada do pkt_buffer
            self.__update_sequence('sender', address)

        
        # Retorno um pacote vazio para que não seja adicionado um ACK à lista de ACKs
        return '', address, time  

    def add_send_buffer(self, msg, address):
        # Adiciona mensagem ao buffer de mensagens a serem enviadas
        self.send_buffer.append((msg,address)) # Mensagem e pra quem eu quero enviar
        
    def add_ack(self,msg_received, address, time):
        # Adiciona a mensagem recebida ao vetor de ACKs para posterior envio de ACK
        msg = "ACK"
        self.ack_buffer.append((msg, time, address, msg_received))

    # ------------------------ Conexão ---------------------------------

    def close(self):
        # Encerra a conexão
        print("\nConexão encerrada")
        self.UDPsocket.close() 

    def get_connecteds(self):
        msg_list = '---- lista de usuários ----'
        for address in self.connected.keys():
            msg_list += '\n' + str(self.connected[address]['user'])
        msg_list += '\n---------------------------'
        return msg_list
  
    def connect(self, user_name, address):
        self.connected[address] = {
            'user': user_name,
            'seqNumber': {
                'sender': 0 ,
                'receiver': 0
            },
            'ban': {
                'count': 0,
                'time' : datetime.now()
            }
        }

    def get_user_name(self, address):
        if address in self.connected.keys():
            return str(self.connected[address]['user'])
        return ''

    def disconnect(self, address):
        if address in self.connected.keys():
           del self.connected[address]
    
    def find_address(self, user_name):
        for user_address in self.connected.keys():
                if self.connected[user_address]['user'] == user_name:
                    return user_address
        return ''
