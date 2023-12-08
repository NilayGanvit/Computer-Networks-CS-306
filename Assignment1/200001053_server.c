// Assignment 1
// UDP Server
// including the header files:
#include <stdio.h>      // for printf() and fprintf()
#include <string.h>     // for memset()
#include <sys/socket.h> // for socket(), connect(), send(), and recv()
#include <arpa/inet.h>  // for sockaddr_in and inet_addr()
#include <stdbool.h>    // for bool data type
                        // function to check if the character is q space
bool space(char s)
{
    return s == ' ';
}
// function to check if the character is an operator
bool function(char s)
{
    return s == '+' || s == '-' || s == '*' || s == '/';
}
// function to solve the equation
int solve(char buffer[255])
{ // initialize the answer and the operands
    int ans = 0;
    char op1[255];
    char op2[255];
    // loop through the equation
    for (int i = 0; i < 255; i++)
    {
        if (isalpha(buffer[i]))
        {
            ans = -999;
            return ans;
        }
    }
    for (int i = 0; i < 255; i++)
    { // check if the equation is valid
        if (!isdigit(buffer[i]) && !function(buffer[i]) && !space(buffer[i]))
        {
            ans = -999;
            return ans;
        }
        // calculation
        if (function(buffer[i]))
        {

            strncpy(op1, buffer, i);
            int j = i + 1;
            while (isdigit(buffer[j]))
                j++;

            strncpy(op2, buffer + i + 1, j - i - 1);

            int q = atoi(op1), w = atoi(op2);
            switch (buffer[i])
            {
            case '+':
                ans = q + w;
                break;
            case '-':
                ans = q - w;
                break;
            case '*':
                ans = q * w;
                break;
            case '/':
                if (w == 0)
                {
                    ans = -1000;
                    break;
                }
                ans = q / w;
                break;
            }
            return ans;
        }
    }
}
// main function
int main(int argc, char *argv[])
{ // initialize the socket descriptor, server and client addresses, server reply and equation
    int socket_desc;
    struct sockaddr_in server, client;
    char server_reply[2000], equation[2000];
    int client_struct_length = sizeof(client);

    // Create UDP socket:
    socket_desc = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    // Check if socket is created:
    if (socket_desc < 0)
    {
        printf("Socket not created\n");
        return -1;
    }
    printf("Created the socket\n");

    // Prepare the sockaddr_in structure:
    server.sin_family = AF_INET;
    server.sin_port = htons(atoi(argv[2]));
    server.sin_addr.s_addr = inet_addr(argv[1]);

    // Bind the socket:
    if (bind(socket_desc, (struct sockaddr *)&server, sizeof(server)) < 0)
    {
        printf("Binding not done\n");
        return -1;
    }
    printf("Binding done\n");
    // Listen to client:
    printf("Write equation in client\n\n");
    // infinite loop to keep the server running
    int flag = 1;
    while (flag)
    { // initialize the answer
        int ans;
        // Receive from client:
        memset(equation, '\0', sizeof(equation));
        if (recvfrom(socket_desc, equation, sizeof(equation), 0, (struct sockaddr *)&client, &client_struct_length) < 0)
        {
            printf("Message not recieved\n");
            return -1;
        }
        // print the client's IP and port
        printf("clients' IP= %s & port = %i\n", inet_ntoa(client.sin_addr), ntohs(client.sin_port));
        // print the equation
        printf("Reseived %s\n", equation);
        ans = solve(equation);
        // check if the equation is valid
        memset(server_reply, '\0', sizeof(server_reply));
        if (ans == -999)
        {
            char e[255] = "Wrong input";
            strcpy(equation, e);
        }
        else if (ans == -1000)
        {
            char e[255] = "Division by zero";
            strcpy(equation, e);
        }
        else
        {
            sprintf(equation, "%d", ans);
        }

        // Respond to client:
        strcpy(server_reply, equation);
        if (sendto(socket_desc, server_reply, strlen(server_reply), 0, (struct sockaddr *)&client, client_struct_length) < 0)
        {
            printf("Can't send message\n");
            return -1;
        }
    }
    // clossing the socket
    close(socket_desc);

    return 0;
}
