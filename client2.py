import socket

serverAddress   = ("localhost", 20001)
bufferSize      = 1024
fileRec         = "fileRecvFromServer."

# Create a UDP socket at client side
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
print("digite o nome: ")
fileNameIn = input()


#antes de mandar vou mandar o tipo 
Tipo = fileNameIn.split('.')[1]
bytesTipo = str.encode(Tipo)
UDPClientSocket.sendto(bytesTipo, serverAddress)
print("tipo enviado")


#enviando e recebendo:
fileRec += Tipo
file2 = open(fileRec,'wb')
file = open(fileNameIn, "rb")
bytesToSend = file.read(bufferSize)


print("Enviando...")
while(bytesToSend):
    UDPClientSocket.sendto(bytesToSend, serverAddress)
    bytesToSend = file.read(bufferSize)
    data, address = UDPClientSocket.recvfrom(bufferSize)
    file2.write(data)
    

UDPClientSocket.sendto('\x18'.encode(), serverAddress)
print("Envio realizado!")
file.close()
file2.close()
UDPClientSocket.close()
