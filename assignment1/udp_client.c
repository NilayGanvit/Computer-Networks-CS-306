#include <stdio.h>
#include <string.h>
#include <sys/socket.h>
#include <arpa/inet.h>

int main(void){
    int socket_desc;
    struct sockaddr_in server_addr;
    int op1,op2;
    char op;
    int server_struct_length = sizeof(server_addr);
    //taking inputs

    scanf("%d",&op1);
    scanf("%c",&op);

    scanf("%d",&op2);


    
    // Create socket:
    socket_desc = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    
    if(socket_desc < 0){
        printf("Error while creating socket\n");
        return -1;
    }
    printf("Socket created successfully\n");
    
    // Set port and IP:
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(8080);
    server_addr.sin_addr.s_addr = inet_addr("127.0.0.1");;

    
    // Send the message to server:
    if(sendto(socket_desc, &op1, sizeof(op1), 0,
         (struct sockaddr*)&server_addr, server_struct_length) < 0){
        printf("Unable to send message\n");
        return -1;
    }
    // Send the message to server:
    if(sendto(socket_desc, &op, sizeof(op), 0,
         (struct sockaddr*)&server_addr, server_struct_length) < 0){
        printf("Unable to send message\n");
        return -1;
    }

    // Send the message to server:
    if(sendto(socket_desc, &op2, sizeof(op2), 0,
         (struct sockaddr*)&server_addr, server_struct_length) < 0){
        printf("Unable to send message\n");
        return -1;
    }
    
    
    printf("Server's response: %s\n", &op1);
    
    // Close the socket:
    close(socket_desc);
    
    return 0;
}

