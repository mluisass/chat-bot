server_address = ("0.0.0.0", 20001)
buffer_size = 1024

from pickle import FALSE
import socket
from struct import unpack

class UDP:
    def __init__(self, server):
        # server => true or false

        self.UDPsocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.sequence = 0
        if (server):
            self.UDPsocket.bind(server_address)
            print("servidor ligou hein")
        
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
        
        ack = False
        while not ack :
            self.send(pkt,address) # envia o pacote novamente
            
            try:
                msg, address = self.receive() # tenta receber um ACK
            except socket.timeout:
                print('Timeout')
                self.UDPsocket.settimeout(1) # reseta o temporizador
            else:
                ack = self.rcv_pkt(msg) # verifica se recebeu um ACK
                # aqui tem q ter um update dps

        self.UDPsocket.settimeout(None) # desliga temporizador 

    def rdt_rcv(self):

        msg, address = self.receive()
        not_corrupt = self.rcv_pkt(msg,'receiver')
        
        if not_corrupt:
            pkt = self.make_pkt(str('').encode(), self.sequence)
            self.send(pkt,address)
            self.update_sequence()
        else: 
            pkt = self.make_pkt(str('').encode(), 1-self.sequence)
            self.send(pkt,address)

        return msg,address        

    def make_pkt(self , msg, seq):
        cksum = self.checksum(msg)
        
        return str({
            'cksum':cksum,
            'data':msg,
            'seq':seq}).encode()
            
    def update_sequence(self):
        self.sequence = 1 - self.sequence

    def rcv_pkt(self, msg, type='sender'):
        dicio = eval(msg.decode())
        cksum = self.checksum(dicio['data'])
        
        # verifica se o pacote está corrompido
        if cksum != dicio["cksum"]:
            return False
        
        # se é transmissor e o ACK recebido tem nº de sequência antigo
        if type == 'sender' and self.sequence != dicio['seq']:
            return False
        
        # se é transmissor e sobreviveu até aqui,é pq ele recebeu o ACK certinho
        if type == 'sender':
            self.update_sequence()

        return True

    ## ----- todo: entender isso aqui -----
    def checksum(self, msg):
        cksum = 0

        array = bytearray(msg)[::-1]
        lenght = len(array)

        for i in range(lenght):
            if i % 2:
                continue 
            
            cksum += (array[i] << 8)
            if i + 1 < lenght:
                cksum += array[i+1]

        while cksum >> 16:
            cksum = (cksum >> 16) + (cksum & 0xffff)
        
        cksum = cksum ^ 0xffff # inverte bits

        return cksum