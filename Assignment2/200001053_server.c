#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <pthread.h>

#define MAX_MSG_LEN 255
#define PORT 8000

void* receive_message(void* conn) {
    char buffer[MAX_MSG_LEN];
    int connection = *((int*) conn);
    for (;;) {
        bzero(buffer, MAX_MSG_LEN);
        read(connection, buffer, sizeof(buffer));
        if (strncmp("close", buffer, 5) == 0) {
            break;
        }
        printf("Client: %s", buffer);
    }
}

void* send_message(void* conn) {
    char buffer[MAX_MSG_LEN];
    int connection = *((int*) conn);
    for (;;) {
        bzero(buffer, MAX_MSG_LEN);
        fgets(buffer, MAX_MSG_LEN, stdin);
        write(connection, buffer, sizeof(buffer));
        if (strncmp("close", buffer, 5) == 0) {
            printf("Server closed.\n");
            break;
        }
    }
}

int main() {
    int sockfd, connection, len;
    struct sockaddr_in server, client;

    sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd == -1) {
        perror("Error creating socket");
        exit(EXIT_FAILURE);
    }
    printf("Socket created successfully.\n");

    bzero(&server, sizeof(server));
    server.sin_family = AF_INET;
    server.sin_addr.s_addr = htonl(INADDR_ANY);
    server.sin_port = htons(PORT);

    if (bind(sockfd, (struct sockaddr*) &server, sizeof(server)) != 0) {
        perror("Error binding socket");
        exit(EXIT_FAILURE);
    }
    printf("Socket bound successfully.\n");

    if (listen(sockfd, 5) != 0) {
        perror("Error listening to socket");
        exit(EXIT_FAILURE);
    }
    printf("Server listening...\n");

    len = sizeof(client);
    connection = accept(sockfd, (struct sockaddr*) &client, &len);
    if (connection < 0) {
        perror("Error accepting connection");
        exit(EXIT_FAILURE);
    }
    printf("Server accepted client request.\n");

    pthread_t receive_thread, send_thread;
    pthread_create(&receive_thread, NULL, receive_message, &connection);
    pthread_create(&send_thread, NULL, send_message, &connection);

    pthread_join(receive_thread, NULL);
    pthread_join(send_thread, NULL);

    close(sockfd);
    return 0;
}
