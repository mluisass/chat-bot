server_address = ("0.0.0.0", 20001)
buffer_size = 1024

import socket

class UDP:
    def __init__(self, server):
        # server => true or false

        self.UDPsocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.sequence = 0
        if (server):
            self.UDPsocket.bind(server_address)
            print("Servidor ligado")
        
    def receive(self):
        package, address = self.UDPsocket.recvfrom(buffer_size)
        return (package,address)
    
    def send(self, package, address):
        self.UDPsocket.sendto(package, address) # pro cliente: address = serverAdress
    
    def close(self):
        self.UDPsocket.close()
    
    def rdt_send(self, msg, address):
        
        self.UDPsocket.settimeout(1) # seta o timeout

        pkt = self.make_pkt(msg,self.sequence) # cria o pacote
        print(self.sequence)
        ack = False
        while not ack :
            self.send(pkt,address) # envia o pacote novamente
            
            try:
                msg, address = self.receive() # tenta receber um ACK
            except socket.timeout:
                print('Timeout')
                self.UDPsocket.settimeout(1) # reseta o temporizador
                self.send(pkt,address) # envia o pacote novamente
            else:
                ack = self.rcv_pkt(msg) # verifica se recebeu um ACK

        self.UDPsocket.settimeout(None) # desliga temporizador 

    def rdt_rcv(self):

        msg, address = self.receive()
        check_seq = self.rcv_pkt(msg,'receiver') # T => OK
        
        if check_seq:
            pkt = self.make_pkt(str('ACK'), self.sequence)
            self.send(pkt,address)
            self.update_sequence()
        else: 
            pkt = self.make_pkt(str('ACK'), 1-self.sequence)
            self.send(pkt,address)

        return msg,address        

    def make_pkt(self , msg, seq):
        return str({
            'data':msg,
            'seq':seq}).encode()
            
    def update_sequence(self):
        self.sequence = 1 - self.sequence

    def rcv_pkt(self, msg, type='sender'):
        dicio = eval(msg.decode())
        
        # se é transmissor e o ACK recebido tem nº de sequência antigo
        if self.sequence != dicio['seq']:
            return False
        
        # se é transmissor e sobreviveu até aqui,é pq ele recebeu o ACK certinho
        if type == 'sender':
            self.update_sequence()

        return True