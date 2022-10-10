from utils import *
import threading as th
class Server:
    #inicializacao do servidor
    def __init__(self):
        self.server_socket = UDP(True) # True => é servidor
        self.current_user = None
        self.last_data_received =None
        self.users = {}

        try:
            lock = th.Lock()
            send_thread = th.Thread(target= self.broadcast, args=[lock, ""] )
            rcv_thread = th.Thread(target= self.run, args=[lock])
            
            send_thread.daemon =True 
            rcv_thread.daemon= True 

            send_thread.start()
            rcv_thread.start()

            send_thread.join()
            rcv_thread.join()

        except KeyboardInterrupt:
            self.server_socket.close()
        

    def run(self, lock):
        #espera em loop infinito pelo contato de um cliente
        while (True):
            try:
                # recebe uma mensagem de um dos clientes
                lock.acquire()
                data, client_address = self.server_socket.rdt_rcv()
                lock.release()
                msg = eval(data.decode())
                msg = msg['data']
                print(msg[:15])
                if msg[:15] == "hi, meu nome eh":
                    print("entrei")
                    user_name = msg[16:]
                    self.users[user_name] = client_address # salva o usuário

                    message = user_name + " entrou na sala"
                    self.broadcast(lock, message)
            
                
            except KeyboardInterrupt:
                self.server_socket.close()
                break

    def broadcast(self, lock, msg):
        lock.acquire()
        for key in self.users:
            self.server_socket.rdt_send(msg, self.users[key])
        lock.release()

    
if __name__ == "__main__":  
    Server()

    
