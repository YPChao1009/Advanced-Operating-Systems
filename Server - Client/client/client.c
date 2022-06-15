#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

#define SUCCESS 0
#define PERMISSION_ERROR -1
#define INVALID_FILE -2
#define OCCUPIED -3
#define INVALID_ACCESS -4
#define FILE_EXIST -5

int main(int argc , char *argv[]){

    //create socket
    int sockfd = 0;
    sockfd = socket(AF_INET , SOCK_STREAM , 0);

    if (sockfd == -1){
        printf("Fail to create a socket.");
    }

    struct sockaddr_in info;
    bzero(&info, sizeof(info));
    info.sin_family = PF_INET;

    info.sin_addr.s_addr = inet_addr("127.0.0.1");
    info.sin_port = htons(8700);

    int err = connect(sockfd, (struct sockaddr *)&info, sizeof(info));
    if(err==-1){
        printf("Connection error");
    }

    // log in
    char name[10];
    char receiveMessage[256];
    recv(sockfd,receiveMessage,sizeof(receiveMessage),0);
    printf("%s", receiveMessage);
    scanf("%s", name);
    while(strcmp(name, "Mickey")!=0 && strcmp(name, "Minnie")!=0 && strcmp(name, "Daisy")!=0 && strcmp(name, "Goofy")!=0 && strcmp(name, "Pluto")!=0 && strcmp(name, "Donald")!=0){
        printf("Must be one of the following users.\n%s",receiveMessage);
        scanf("%s", name);
    }
    send(sockfd, name, sizeof(name), 0);
    recv(sockfd, receiveMessage, sizeof(receiveMessage), 0);
    printf("%s", receiveMessage);

    // \n buffer
    getchar();
    // input command
    while(1){
        char command[256];
        printf("\nCommands:\n(1) create file access right\n(2) read file\n(3) write file o/a\n(4) changemode file access right\n(5) exit\n\nInput command=>");
        //fgets(command, 64, stdin);
        gets(command);
        send(sockfd, command, sizeof(command), 0);
        // command analyzing
        char arg[10][256] = {"", "", "", ""};
        char *delim = " ";
        char *pch;
        pch = strtok(command, delim);
        int i = 0;
        while(pch != NULL){
            strcpy(arg[i], pch);		
            pch = strtok(NULL, delim);
            i++;
        }
        if(strcmp(arg[0], "exit") == 0){
            printf("exit\n");
            break;
        // create
        }else if(strcmp(arg[0], "create") == 0){
            int receive;
            recv(sockfd, &receive, sizeof(receive), 0);
            // check state
            switch (receive){
            case SUCCESS:
                printf("Creating complete\n");
                break;
            case FILE_EXIST:
                printf("%s already exist\n", arg[1]);
                break;
            case INVALID_ACCESS:
                printf("%s is invalid\n", arg[2]);
                break;
            default:
                printf("Unknown error\n");
                break;
            }
        // read
        }else if(strcmp(arg[0], "read") == 0){
            int receive;
            char buffer[1024];
            recv(sockfd, &receive, sizeof(receive), 0);
            // check state
            switch (receive){
            case SUCCESS:
                printf("Reading...\n");
                recv(sockfd, buffer, sizeof(buffer), 0);//receave file content
                FILE *f = fopen(arg[1], "w+");//write file content
                fprintf(f, "%s", buffer);
                printf("Reading complete\n");
                fclose(f);
                break;
            case PERMISSION_ERROR:
                printf("Permission error\n");
                break;
            case INVALID_FILE:
                printf("%s doesn't exist\n", arg[1]);
                break;
            case OCCUPIED:
                printf("Someone is writing\n");
                break;
            default:
                printf("Unknown error\n");
                break;
            }
        // write
        }else if(strcmp(arg[0], "write") == 0){
            int receive;
            recv(sockfd, &receive, sizeof(receive), 0);
            // check state
            switch (receive){
            case SUCCESS:
                printf("Writing...\n");
                char message[1024] = {""};
                char buffer[256];
                printf("Please enter the content:\n") ;
                gets(message) ;         //input string     
                sleep(10); // delay
                send(sockfd, message, sizeof(message), 0);//send string to server
                printf("Writing complete\n");
                break;
            case PERMISSION_ERROR:
                printf("Permission error\n");
                break;
            case INVALID_FILE:
                printf("%s doesn't exist\n", arg[1]);
                break;
            case OCCUPIED:
                printf("Someone is writing or reading\n");
                break;
            default:
                printf("Unknown error\n");
                break;
            }
        // changemode
        }else if(strcmp(arg[0], "changemode") == 0){
            int receive;
            recv(sockfd, &receive, sizeof(receive), 0);
            // check state
            switch (receive){
            case SUCCESS:
                printf("Changing mode complete\n");
                break;
            case INVALID_FILE:
                printf("%s doesn't exist\n", arg[1]);
                break;
            case INVALID_ACCESS:
                printf("%s is invalid\n", arg[2]);
                break;
            default:
                printf("Unknown error\n");
                break;
            }
        }else{
            printf("command error\n");
        }
        

    }
    

    close(sockfd);
    return 0;
}
