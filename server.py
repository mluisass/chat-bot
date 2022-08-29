import socket

localAddress    = ("localhost", 20001)
bufferSize      = 1024
fileRec         = "fileRecvFromClient.pdf"

# Create a datagram socket
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Bind to address and ip
print("Server is creating a UDP socket.")
UDPServerSocket.bind(localAddress)
print("UDP server up and listening!")

nFile = 1
# Listen for incoming datagrams
while(True):

    data, addressClient = UDPServerSocket.recvfrom(bufferSize)

    fileName = str(nFile) + fileRec
    file = open(fileName, "wb")

    while(data != '\x18'.encode()):
        file.write(data)
        data, addressClient = UDPServerSocket.recvfrom(bufferSize)

    file.close()

    print("##################################################")
    print("Arquivo recebido: " + fileName)
    print("Client IP Address:{}".format(addressClient))

    # Sending a reply to client
    file = open(fileName, "rb")
    bytesToSend = file.read(bufferSize)
    
    while(bytesToSend):
        UDPServerSocket.sendto(bytesToSend, addressClient)
        bytesToSend = file.read(bufferSize)

    UDPServerSocket.sendto('\x18'.encode(), addressClient)
    file.close()

    nFile += 1