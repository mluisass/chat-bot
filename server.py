import socket

localIP     = "127.0.0.1"
localPort   = 20001
bufferSize  = 1024
fileName = "imagem_rec.pdf"

# Create a datagram socket
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Bind to address and ip
UDPServerSocket.bind((localIP, localPort))
print("UDP server up and listening")

# Listen for incoming datagrams
while(True):
    file = open(fileName, "wb")
    data, add = UDPServerSocket.recvfrom(bufferSize)
    while(data != '\x18'.encode()):
        file.write(data)
        data, add = UDPServerSocket.recvfrom(bufferSize)

    file.close()
    clientMsg = "data from Client:{}".format(data)
    clientIP  = "Client IP Address:{}".format(add)
    print(clientMsg)
    print(clientIP)
    # Sending a reply to client
    file2 = open(fileName,"rb")
    bytesToSend = file2.read(bufferSize)
    while(bytesToSend):
        UDPServerSocket.sendto(bytesToSend,add)
        bytesToSend = file2.read(bufferSize)

    file2.close()
    UDPServerSocket.sendto('\x18'.encode(),add)

