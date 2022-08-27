from email import message
import socket
msgClient = open(input(),"rb")
retorno = "resposta.pdf"
#msgFromClient = "Hello UDP Server"
bufferSize = 1024
bytesToSend = msgClient.read(bufferSize)
serverAddressPort   = ("127.0.0.1", 20001)

# Create a UDP socket at client side
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Send to server using created UDP socket
while(bytesToSend):
    UDPClientSocket.sendto(bytesToSend, serverAddressPort)
    bytesToSend = msgClient.read(bufferSize)
    #msgServer = UDPClientSocket.recvfrom(bufferSize)
    #msg = "Message from Server {}".format(msgServer[0])
    print("Enviando...")
msgClient.close()
UDPClientSocket.sendto('\x18'.encode(),serverAddressPort)
print("Envio realizado!")
msg_retorno = open(retorno,'wb')
file, add = UDPClientSocket.recvfrom(bufferSize)
while(file != '\x18'.encode()):
    msg_retorno.write(file)
    file, add = UDPClientSocket.recvfrom(bufferSize)
msg_retorno.close()
UDPClientSocket.close()