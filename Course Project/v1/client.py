import socket
import time

# create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# connect the socket to the server's IP address and port
server_address = ('192.168.1.1', 10000)
sock.connect(server_address)

try:
    # send a message to the server
    message = 'ping'
    sock.sendall(message.encode())

    # receive a response from the server
    data = sock.recv(1024)
    print('received "%s"' % data)

finally:
    # close the socket
    sock.close()
