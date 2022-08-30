import socket

localAddress    = ("localhost", 20001)
bufferSize      = 1024
fileRec         = "fileRecvFromClient."

# Create a datagram socket
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Bind to address and ip
print("Server is creating a UDP socket.")
UDPServerSocket.bind(localAddress)
print("UDP server up and listening!")

nFile = 1
# Listen for incoming datagrams
while(True):

    ##### RECEBENDO O TIPO
    data, addressClient = UDPServerSocket.recvfrom(bufferSize)
    tipoRecebido = str(data.decode())
    print("tipo recebido do cliente = ", tipoRecebido)
    #####
    
    fileName = str(nFile) + fileRec + tipoRecebido
    file = open(fileName, "wb")
    file2 = open(fileName, "rb")
    
    print("enviando a respsota...")
    

    while(data != '\x18'.encode()):
        data, addressClient = UDPServerSocket.recvfrom(bufferSize)
        file.write(data)
        UDPServerSocket.sendto(data, addressClient)

    
    print("##################################################")
    print("Arquivo recebido: " + fileName)
    print("Client IP Address:{}".format(addressClient))
    UDPServerSocket.sendto('\x18'.encode(), addressClient)
    file.close()
    file2.close()
    print("mandei a resposta!")
    nFile += 1
    
    
        

    
    
    

    