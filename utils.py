server_address = ("0.0.0.0", 20001)
buffer_size = 1024

import socket

class UDP:
    #inicializaçao
    def __init__(self, server):
        # server => true or false
        self.UDPsocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.sequence = 0
        if (server):
            self.UDPsocket.bind(server_address)
            print("Servidor ligado")
        
    def receive(self): #recebimento
        package, address = self.UDPsocket.recvfrom(buffer_size)
        return (package,address)
    
    def send(self, package, address): #envio
        self.UDPsocket.sendto(package, address) # pro cliente: address = serverAdress
    
    # fecha a conexão
    def close(self):
        self.UDPsocket.close()
    
    #envio de um pacote
    def rdt_send(self, msg, address):
        
        self.UDPsocket.settimeout(1) # seta o timeout

        pkt = self.make_pkt(msg,self.sequence) # cria o pacote
        print(self.sequence)
        ack = False
        while not ack :
            self.send(pkt,address) # envia o pacote (novamente, caso ja tenha enviado antes)
            
            try:
                msg, address = self.receive() # tenta receber um ACK
            except socket.timeout:
                print('Timeout')
                self.UDPsocket.settimeout(1) # reseta o temporizador
                self.send(pkt,address) # envia o pacote novamente
            else:
                ack = self.rcv_pkt(msg) # verifica se recebeu um ACK

        self.UDPsocket.settimeout(None) # desliga temporizador 

    #recebe um pacote e checa o conteudo 
    def rdt_rcv(self):
        msg, address = self.receive() #recebe um pacote
        check_seq = self.rcv_pkt(msg,'receiver') # checa o numero de sequencia (True => OK)
        #se estiver correto envia o ACK de volta
        if check_seq:
            pkt = self.make_pkt(str('ACK'), self.sequence)
            self.send(pkt,address)
            self.update_sequence()
        #se estiver errado devolve o ACK antigo
        else: 
            pkt = self.make_pkt(str('ACK'), 1-self.sequence)
            self.send(pkt,address)

        return msg,address        

    #cria o pacote com cabeçalho
    def make_pkt(self , msg, seq):
        return str({
            'data':msg,
            'seq':seq}).encode()
            
    #atualiza o numero de sequencia
    def update_sequence(self):
        self.sequence = 1 - self.sequence

    #verifica se o pacote recebido foi o esperado
    def rcv_pkt(self, msg, type='sender'):
        dicio = eval(msg.decode())
        
        # se é transmissor e o ACK recebido tem nº de sequência antigo
        if self.sequence != dicio['seq']:
            return False
        
        # se é transmissor e sobreviveu até aqui,é pq ele recebeu o ACK correto
        if type == 'sender':
            self.update_sequence()

        return True