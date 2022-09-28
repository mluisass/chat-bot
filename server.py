from utils import *

class Server:
    #inicializacao do servidor
    def __init__(self):
        self.server_socket = UDP(True) # True => é servidor
        self.current_user = None
        self.last_data_received =None
    
        self.run()

    def run(self):

        #espera em loop infinito pelo contato de um cliente
        while (True):
            try:
                # recebe uma mensagem de um dos clientes
                data, client_address = self.server_socket.rdt_rcv()
                print(data.decode())

                self.last_data_received = data
                self.current_user = client_address

                msg = eval(self.last_data_received.decode())
                msg = msg['data']

                # devolve ao cliente a mensagem enviada por ele
                self.server_socket.rdt_send(msg, self.current_user)
            except KeyboardInterrupt:
                self.server_socket.close()
                break

    
if __name__ == "__main__":
    Server()

    
