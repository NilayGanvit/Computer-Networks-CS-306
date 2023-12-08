// Assignment 1
// UDP Client
// including the header files:
#include <stdio.h> // for printf() and fprintf()
#include <string.h> // for memset()
#include <sys/socket.h> // for socket(), connect(), send(), and recv()
#include <arpa/inet.h> // for sockaddr_in and inet_addr()

int main(int argc, char *argv[]) // main function
{
    int socket_desc; // socket descriptor
    struct sockaddr_in server; // server address
    char server_reply[2000], equation[2000]; // server reply and equation
    int server_struct_length = sizeof(server); // server address length

    // Create UDP socket:
    socket_desc = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);

    // Check if socket is created:
    if (socket_desc < 0)
    {
        printf("Socket not created\n");
        return -1;
    }
    printf("creating socket\n");

    // Prepare the sockaddr_in structure:
    server.sin_family = AF_INET;
    server.sin_port = htons(atoi(argv[2]));
    server.sin_addr.s_addr = inet_addr(argv[1]);

    // Send and receive messages:
    int flag=1;
    while (flag)
    {   
        memset(equation, '\0', sizeof(equation));
        printf("Equation to be sent: ");
        gets(equation);
        // Check if the user wants to close:
        int close = strncmp("close", equation, 4);
        if (close == 0)
            break;

        // Send the equation to the server:
        if (sendto(socket_desc, equation, strlen(equation), 0, (struct sockaddr *)&server, server_struct_length) < 0)
        {
            printf("Equation not sent\n");
            return -1;
        }
        
        memset(server_reply, '\0', sizeof(server_reply));
        // Receive the server's reply:
        if (recvfrom(socket_desc, server_reply, sizeof(server_reply), 0, (struct sockaddr *)&server, &server_struct_length) < 0)
        {
            printf("Error recieving answer\n");
            return -1;
        }
        // Print the server's reply:
        printf("Ans: %s\n", server_reply);
    }
    // Close the socket:
    close(socket_desc);

    return 0;
}
