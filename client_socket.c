#include<stdio.h>
#include<string.h>
#include<sys/socket.h>
#include<netdb.h>
#include<stdlib.h>

void error_fun(const char *msg)
{
    perror(msg);
    exit(1);
}
int main(int argc, char *argv[])
{
    int sockfd, portno;
    struct sockaddr_in server;
    char *message , server_reply[2000];
    struct hostent *server_host;

    if(argc<3)
    {
        printf('Please provide filename, hostname and port.\n');
        exit(1);
    }
    portno = atoi(argv[2]);

    sockfd = socket(AF_INET, SOCK_STREAM,0);
    if(sockfd == -1)
    {
        error_fun("Socket can not be created");
    }

    server_host = gethostbyname(argv[1]);

    if(server_host == NULL)
    {
        error_fun("Error, No such host");
    }

    bcopy((char *)server_host->h_addr, (char *) & server.sin_addr.s_addr, server_host->h_length);

    server.sin_family = AF_INET;
    server.sin_port=htons( portno );

    if ()
    
}