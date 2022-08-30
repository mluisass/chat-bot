import socket

serverAddress   = ("localhost", 20001)
bufferSize      = 2048
fileRec         = "fileRecvFromServer.pdf"

# Create a UDP socket at client side
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

file = open(input("Digite o nome do arquivo que deseja enviar: "), "rb")
bytesToSend = file.read(bufferSize)

# Send to server using created UDP socket
print("Enviando...")
while(bytesToSend):
    UDPClientSocket.sendto(bytesToSend, serverAddress)
    bytesToSend = file.read(bufferSize)
    
file.close()
UDPClientSocket.sendto('\x18'.encode(), serverAddress)
print("Envio realizado!")

file = open(fileRec,'wb')
data, address = UDPClientSocket.recvfrom(bufferSize)

while(data != '\x18'.encode()):
    file.write(data)
    data, address = UDPClientSocket.recvfrom(bufferSize)

file.close()
UDPClientSocket.close()