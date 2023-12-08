// #include <iostream>
// #include <cstring>
// #include <vector>
// #include <string>
// #include <algorithm>
// #include <stdio.h>
// #include <stdlib.h>
#include<bits/stdc++.h>
#include <pthread.h>
#include <unistd.h>
#include <sys/socket.h>
#include <arpa/inet.h>

using namespace std;

const int PORT = 8080;
const int conn_limit = 10;

pthread_t thread_id[20];

void *handle_client(void *param)
{
    int sock = *(int *)param;
    while (true)
    {
        char buffer[1024];
        int bytes_received = recv(sock, buffer, 1024, 0);
        if (bytes_received == 0)
        {
            break;
        }
        buffer[bytes_received] = '\0';
        cout <<"client: "<< buffer << endl;
        if (strcmp(buffer, "close") == 0)
        {
            send(sock, buffer, strlen(buffer), 0);
            break;
        }
        // bytes_received = recv(sock, buffer, 1024, 0);
        string send_line;
        getline(cin, send_line);
        const char *send_message = send_line.c_str();
        send(sock, send_message, strlen(send_message), 0);
    }
    close(sock);
    pthread_exit(NULL);
}

int main()
{
    int server_sock = socket(AF_INET, SOCK_STREAM, 0);
    if (server_sock < 0)
    {
        cout << "Failed to create socket" << endl;
        return 1;
    }

    struct sockaddr_in server_addr;
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = INADDR_ANY;
    server_addr.sin_port = htons(PORT);

    if (bind(server_sock, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0)
    {
        cout << "Failed to bind socket" << endl;
        return 1;
    }

    if (listen(server_sock, conn_limit) < 0)
    {
        cout << "Failed to listen on socket" << endl;
        return 1;
    }

    // cout << "Server running on port " << PORT << endl;

    vector<thread> threads;

    int i = 0;

    while (true)
    {
        struct sockaddr_in client_addr;
        socklen_t client_addr_len = sizeof(client_addr);
        int client_sock = accept(server_sock, (struct sockaddr *)&client_addr, &client_addr_len);
        if (client_sock < 0)
        {
            cout << "Failed to accept client connection" << endl;
            continue;
        }
        if (pthread_create(&thread_id[i], NULL, handle_client, (void *)&client_sock) < 0)
        {
            perror("could not create thread");
            return 1;
        }
        if (i >= 10)
        {
            i = 0;
            while (i < 10)
            {
                pthread_join(thread_id[i++], NULL);
            }
            i = 0;
        }

    }

    close(server_sock);
    return 0;
}