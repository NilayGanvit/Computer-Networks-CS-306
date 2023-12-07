#include <unistd.h>
#include <arpa/inet.h>
#include <netdb.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/types.h>

/*
filename server_ipaddress portno
argv[0] - filename
argv[1] - server_ipaddress
argv[2] - portno
*/

void error_fun(const char *msg) {
    perror(msg);
    exit(1);
}

int main(int argc, char *argv[]) {
    int sockfd, portno;
    struct sockaddr_in server;
    char *message, server_reply[2060];
    struct hostent *server_host;

    // if (argc < 3) {
    //     printf("Please provide filename, hostname and port.\n");
    //     exit(1);
    // }
    portno = atoi(argv[0]);

    // Create socket
    sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd == -1) {
        error_fun("Socket can not be created");
    }

    server_host = gethostbyname(argv[1]);

    if (server_host == NULL) {
        error_fun("Error, No such host");
    }

    // copying h_addr into s addr
    bcopy((char *)server_host->h_addr, (char *)&server.sin_addr.s_addr,
          server_host->h_length);
    // server.sin_addr.s_addr = inet addr("142.251.42.100");

    server.sin_family = AF_INET;

    server.sin_port = htons(portno);  // portno taken from command line argument

    // Connect to remote server
    if (connect(sockfd, (struct sockaddr *)&server, sizeof(server)) < 0) {
        error_fun("connection error");
    }

    printf("Connected\n");

    // Send some data
    message = "GET / HTTP/1.1\r\n\r\n";

    if (send(sockfd, message, strlen(message), 0) < 0) {
        error_fun("Send failed");
    }
    printf("Data Send\n");

    // Receive a reply from the server
    if (recv(sockfd, server_reply, 2000, 0) < 0) {
        error_fun("recv failed ");
    }

    puts("Reply received\n");
    puts(server_reply);
    close(sockfd);

    return 0;
}