#include <arpa/inet.h>
#include <netdb.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <unistd.h>

void error_fun(const char *msg)
{
    perror(msg);
    exit(1);
}

int main(int argc, char *argv[])
{

    if (argc < 2)
    {
        error_fun("Insufficient parameters");
    }

    int socket_desc, client_socket, c, client_port, *client_sock, portno, byte_size;
    struct sockaddr_in server, client;
    char *client_ip, buffer[255];

    socket_desc = socket(AF_INET, SOCK_STREAM, 0);
    if (socket_desc == -1)
    {
        error_fun("Could not create socket.");
    }

    bzero((char *)&server, sizeof(server));
    portno = atoi(argv[1]);

    server.sin_family = AF_INET;
    server.sin_addr.s_addr = INADDR_ANY;
    server.sin_port = htons(portno);

    if (bind(socket_desc, (struct sockaddr *)&server, sizeof(server)) < 0)
    {
        error_fun("Bind failed!");
    }
    printf("Binded");

    listen(socket_desc, 3);
    puts("Waiting for incoming connections");
    c = sizeof(struct sockaddr_in);
    client_socket = accept(socket_desc, (struct sockaddr *)&client, (socklen_t *)&c);
    if (client_socket < 0)
    {
        error_fun("Connection request failed.");
    }
    client_ip = inet_ntoa(client.sin_addr);
    client_port = ntohs(client.sin_port);
    printf("Client IP is %s and client port is %d\n", client_ip, client_port);

    while (1)
    {
        bzero(buffer, 255); // clear the buffer
        byte_size = read(client_socket, buffer, 255); // read from client
        if (byte_size == 0)
        {
            puts("Client Disconnected.");
            fflush(stdout);
        }
        else if (byte_size < 0)
        {
            error_fun("Error on Reading");
        }
        printf("Client: %s\n", buffer);
        bzero(buffer, 255);
        fgets(buffer, 255, stdin);

        byte_size = write(client_socket, buffer, strlen(buffer));
        if (byte_size < 0)
        {
            error_fun("Error on Writing");
        }
        int i = strncmp("close", buffer, 5);
        if (i == 0)
        {
            break;
        }
    }
    close(client_socket);
    close(socket_desc);
}