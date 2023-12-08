import socket

# create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# bind the socket to a specific IP address and port
server_address = ('192.168.1.1', 10000)
sock.bind(server_address)

# listen for incoming connections
sock.listen(1)

while True:
    # wait for a connection
    print('waiting for a connection...')
    connection, client_address = sock.accept()
    try:
        print('connection from', client_address)

        # receive data from the client
        data = connection.recv(1024)
        print('received "%s"' % data)

        # send a response to the client
        message = 'pong'
        connection.sendall(message.encode())

    finally:
        # close the connection
        connection.close()
