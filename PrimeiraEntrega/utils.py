server_address = ("0.0.0.0", 20001)
buffer_size = 1024

import socket

class UDP:
    def __init__(self, server):
        # server => true or false

        self.UDPsocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

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
    