SERVER_ADDRESS = ("0.0.0.0", 20001)
BUFFER_SIZE = 1024

import socket

class UDP:
    #inicializaçao
    def __init__(self, server):
        # server => true or false
        self.UDPsocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.sequence = 0

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
    def rdt_send(self, msg, address):
        
        self.UDPsocket.settimeout(1) # seta o timeout

        pkt = self.__make_pkt(msg,self.sequence) # cria o pacote
        self.__send(pkt,address) # envia o pacote
        print(self.sequence)

        ack = False
        while not ack :
            try:
                msg, address = self.__receive() # tenta receber um ACK
            except socket.timeout:
                print('Timeout')
                self.UDPsocket.settimeout(1) # reinicia o temporizador
                self.__send(pkt,address) # envia o pacote novamente
            else:
                ack = (self.__check_seq(msg) & self.__is_ack(msg)) # verifica se recebeu um ACK com nº seq correto

        self.UDPsocket.settimeout(None) # desliga temporizador 

    #recebe um pacote e checa o conteudo 
    def rdt_rcv(self):
        msg, address = self.__receive() #recebe um pacote
        check_seq = self.__check_seq(msg,'receiver') # checa o numero de sequencia (True => OK)

        #se estiver correto envia o ACK de volta
        if check_seq:
            pkt = self.__make_pkt(str('ACK'), self.sequence)
            self.__send(pkt,address)
            self.__update_sequence()
        #se estiver errado devolve o ACK antigo
        else: 
            pkt = self.__make_pkt(str('ACK'), 1-self.sequence)
            self.__send(pkt,address)

        return msg,address        

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
        
        # se tem nº de sequência antigo
        if self.sequence != data['seq']:
            return False
        
        # caso seja transmissor, atualiza o numero de sequencia
        if type == 'sender' :
            self.__update_sequence()

        return True