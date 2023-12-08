#include <pthread.h>
#include <iostream>
#include <unistd.h>
#include <sys/socket.h>
#include <arpa/inet.h>

using namespace std;

const char* SERVER_ADDR = "127.0.0.1";
const int PORT = 8080;

void* client_pid(void* args) {
    int sockfd;
    struct sockaddr_in server_addr;

    sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0) {
        perror("socket error");
        exit(1);
    }

    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(PORT);
    server_addr.sin_addr.s_addr = inet_addr(SERVER_ADDR);

    if (connect(sockfd, (struct sockaddr*)&server_addr, sizeof(server_addr)) < 0) {
        perror("connect error");
        exit(1);
    }

    int count;
    while (true) {
        char buffer[1024];
        string mssg_sent;
        getline(cin, mssg_sent);
        const char* mssg_out = mssg_sent.c_str();

        if ((count = send(sockfd, mssg_out, strlen(mssg_out), 0)) < 0) {
            perror("send error");
            exit(1);
        }

        if (mssg_sent == "close") {
            break;
        }

        count = recv(sockfd, buffer, 1024, 0);
        buffer[count] = '\0';
        cout << "server: " << buffer << endl;
    }

    close(sockfd);
    pthread_exit(NULL);

    return NULL;
}

int main() {
    pthread_t thread_id;
    pthread_create(&thread_id, NULL, client_pid, NULL);
    pthread_join(thread_id, NULL);

    return 0;
}
