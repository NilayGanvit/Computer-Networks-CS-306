#include <arpa/inet.h>
#include <netdb.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>
#include <pthread.h>

#define MAX_BUFFER_SIZE 255
#define PORT 8000

void *incoming(void *sockfd) {
    char buffer[MAX_BUFFER_SIZE];
    int sock = *((int *)sockfd);

    while (1) {
        // Empty buffer
        bzero(buffer, sizeof(buffer));

        // Read from server to buffer
        read(sock, buffer, sizeof(buffer));

        if (strncmp("close", buffer, 5) == 0) {
            break;
        }

        printf("Server: %s", buffer);
    }
}

void *outgoing(void *sockfd) {
    char buffer[MAX_BUFFER_SIZE];
    int sock = *((int *)sockfd);

    for (;;) {
        // Empty buffer
        bzero(buffer, sizeof(buffer));

        // Copy input to buffer
        fgets(buffer, MAX_BUFFER_SIZE, stdin);

        // Write to server from buffer
        write(sock, buffer, sizeof(buffer));

        // if message is "close" then client exits.
        if ((strncmp(buffer, "close", 5)) == 0) {
            printf("Client Exit.\n");
            break;
        }
    }
}

void error(const char *msg) {
    perror(msg);
    exit(0);
}

int main() {
    int sockfd, connection;
    struct sockaddr_in server, client;

    // Creating Socket
    sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd == -1) {
        error("Socket could not be created.\n");
    } else {
        printf("Socket created successfully.\n");
    }

    bzero(&server, sizeof(server));

    // assign IP and PORT
    server.sin_family = AF_INET;
    server.sin_addr.s_addr = inet_addr("127.0.0.1");
    server.sin_port = htons(PORT);

    // connect the client socket to server socket
    if (connect(sockfd, (struct sockaddr *)&server, sizeof(server)) != 0) {
        error("Connection failed.\n");
    } else {
        printf("Connected to the server.\n");
    }

    // function for chat
    pthread_t incoming_msgs, outgoing_msgs;
    pthread_create(&incoming_msgs, NULL, incoming, &sockfd);
    pthread_create(&outgoing_msgs, NULL, outgoing, &sockfd);

    pthread_join(incoming_msgs, NULL);
    pthread_join(outgoing_msgs, NULL);

    // close the socket
    close(sockfd);
}
