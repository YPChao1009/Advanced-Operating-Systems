#include<stdio.h>
#include<stdlib.h>
#include<string.h>
#include<unistd.h>
#include<pthread.h>
#include<sys/types.h>
#include<sys/socket.h>
#include<netinet/in.h>  // INADDR_ANY sockaddr_in 
#include <arpa/inet.h>  //inet_addr

#define SUCCESS 0
#define PERMISSION_ERROR -1
#define INVALID_FILE -2
#define OCCUPIED -3
#define INVALID_ACCESS -4
#define FILE_EXIST -5


void *connection_handler(void *);//thread function 會開thread 
void show_capability_list();
int check_access_string();

struct capability{
    char accessright[16];
    char owner[10];
    char group[16];
    char file_name[256];
    int status;  //0:do nothing, 1:read, 2:write
};
struct capability capability_list[256];
int num = 0;

int main(int argc , char *argv[]){
    //create socket
    int sockfd ,forClientSockfd;
    pthread_t thread_id;
    sockfd = socket(AF_INET, SOCK_STREAM, 0); //socket File Description

    if (sockfd == -1){
        printf("Fail to create a socket.\n");
    }

    struct sockaddr_in serverInfo,clientInfo;
    int addrlen = sizeof(clientInfo);
    bzero(&serverInfo, sizeof(serverInfo));

    //prepare socketaddr_in structure
    serverInfo.sin_family = PF_INET; //IPv4
    serverInfo.sin_addr.s_addr = INADDR_ANY;//any address
    serverInfo.sin_port = htons(8700);
    bind(sockfd, (struct sockaddr *)&serverInfo, sizeof(serverInfo));//Bind
    listen(sockfd,3);//backlog = 3, connect to server max num
    printf("Waiting for connection...\n");

    while(1){
        forClientSockfd = accept(sockfd, (struct sockaddr*) &clientInfo, &addrlen);
        printf("Connection accepted.\n");
        if( pthread_create( &thread_id, NULL, connection_handler, (void*) &forClientSockfd) < 0){
            perror("could not create thread");
            return 1;
        }
        
        printf("Handler assigned\n");
        
    }
    return 0;
}

void *connection_handler(void *socketfd){
    int clientfd = *(int*)socketfd; //不同client的file description
    char user[10];
    char group[16];

    //log in
    char name[10];
    send(clientfd, "Log in as( Mickey , Minnie , Daisy , Goofy , Pluto, Donald ):\n", 256, 0);
    recv(clientfd, name, sizeof(name), 0);

    //define group
    if(strcmp(name, "Mickey") == 0){strcpy(group, "AOS-students");}
    else if(strcmp(name, "Minnie") == 0){strcpy(group, "AOS-students");}
    else if(strcmp(name, "Daisy") == 0){strcpy(group, "AOS-students");}
    else if(strcmp(name, "Goofy") == 0){strcpy(group, "CSE-students");}
    else if(strcmp(name, "Pluto") == 0){strcpy(group, "CSE-students");}
    else if(strcmp(name, "Donald") == 0){strcpy(group, "CSE-students");}
    strcpy(user, name);
    char message[256] = {"You're in group: "};
    strcat(message, group);
    strcat(message, "\n");
    send(clientfd, message, sizeof(message), 0);
    printf("user: %s group: %s\n", user, group);
    
    while(1){
        //command analyzing
        char command[256];
        recv(clientfd, command, sizeof(command), 0);
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
            printf("%s log out.\n", user);
            break;
        
        //create
        }else if(strcmp(arg[0], "create") == 0){
            // check file exist
            int state;
            int file_exist = 0;
            for(int i=0;i<num;i++){
                if(strcmp(capability_list[i].file_name, arg[1]) == 0){
                    file_exist = 1;
                    break;
                }
            }
            if(file_exist){state = FILE_EXIST;}
            else{state = check_access_string(arg[2]);}
            
            // creating
            if(state == SUCCESS){
                send(clientfd, &state, sizeof(state), 0);
                printf("%s create %s\n", user, arg[1]);
                FILE *f = fopen(arg[1],"w");
                fclose(f);
                // append capability list
                strcpy(capability_list[num].owner, user);
                strcpy(capability_list[num].group, group);
                strcpy(capability_list[num].accessright, arg[2]);
                strcpy(capability_list[num].file_name, arg[1]);
                capability_list[num].status = 0;
                num += 1;
            }else{
                send(clientfd, &state, sizeof(state), 0);          
            }
        
        // read
        }else if(strcmp(arg[0], "read") == 0){
            // check file exist
            int state, index;
            int file_exist = 0;
            for(int i=0;i<num;i++){
                if(strcmp(capability_list[i].file_name, arg[1]) == 0){
                    file_exist = 1;
                    index = i;
                    // check whether someone is writing
                    if(capability_list[i].status == 2){
                        state = OCCUPIED;
                        break;
                    }
                    // check access right
                    if(strcmp(capability_list[i].owner, user) == 0){
                        if(capability_list[i].accessright[0] == 'r'){state = SUCCESS;}
                        else{state = PERMISSION_ERROR;}
                    }else if(strcmp(capability_list[i].group, group) == 0){
                        if(capability_list[i].accessright[2] == 'r'){state = SUCCESS;}
                        else{state = PERMISSION_ERROR;}
                    }else{
                        if(capability_list[i].accessright[4] == 'r'){state = SUCCESS;}
                        else{state = PERMISSION_ERROR;}
                    }
                    break;
                }
            }
            if(file_exist == 0){state = INVALID_FILE;}
            // reading start
            if(state == SUCCESS){
                capability_list[index].status = 1;
                send(clientfd, &state, sizeof(state), 0);
                char message[1024] = {""};
                char buffer[256];
                FILE *f = fopen(arg[1],"r");
                while(fgets(buffer, sizeof(buffer), f)){strcat(message, buffer);}
                sleep(10); // delay
                send(clientfd, message, sizeof(message), 0);
                printf("%s read %s\n", user, arg[1]);
                fclose(f);
                capability_list[index].status = 0;
            // error occur
            }else{
                send(clientfd, &state, sizeof(state), 0);
            }
        
        //write
        }else if(strcmp(arg[0], "write") == 0){
            // check file exist
            int state, index;
            int file_exist = 0;
            for(int i=0;i<num;i++){
                if(strcmp(capability_list[i].file_name, arg[1]) == 0){
                    file_exist = 1;
                    index = i;
                    // check whether someone is reading or writing
                    if(capability_list[i].status == 1 || capability_list[i].status == 2){
                        state = OCCUPIED;
                        break;
                    }
                    // check access right
                    if(strcmp(capability_list[i].owner, user) == 0){
                        if(capability_list[i].accessright[1] == 'w'){state = SUCCESS;}
                        else{state = PERMISSION_ERROR;}
                    }else if(strcmp(capability_list[i].group, group) == 0){
                        if(capability_list[i].accessright[3] == 'w'){state = SUCCESS;}
                        else{state = PERMISSION_ERROR;}
                    }else{
                        if(capability_list[i].accessright[5] == 'w'){state = SUCCESS;}
                        else{state = PERMISSION_ERROR;}
                    }
                    break;
                }
            }
            if(file_exist == 0){state = INVALID_FILE;}
            // writing start
            if(state == SUCCESS){
                capability_list[index].status = 2;
                send(clientfd, &state, sizeof(state), 0);
                char buffer[1024];
                recv(clientfd, buffer, sizeof(buffer), 0);
                FILE *f;
                printf("%s\n",buffer);
                // o/a
                if(strcmp(arg[2], "o") == 0){f = fopen(arg[1], "w");           
                }
                else{f = fopen(arg[1], "a+");}
                fprintf(f, "%s", buffer);
                printf("%s write %s\n", user, arg[1]);
                fclose(f);
                capability_list[index].status = 0;
            // error occur
            }else{
                send(clientfd, &state, sizeof(state), 0);
            }
        //changemode
        }else if(strcmp(arg[0], "changemode") == 0){
            // check file exist
            int state, index;
            int file_exist = 0;
            for(int i=0;i<num;i++){
                if(strcmp(capability_list[i].file_name, arg[1]) == 0){
                    file_exist = 1;
                    index = i;
                    break;
                }
            }

            if(file_exist == 0){state = INVALID_FILE;}
            else{state = check_access_string(arg[2]);}
            
            // change mode start
            if(state == SUCCESS){
                strcpy(capability_list[index].accessright, arg[2]);
                send(clientfd, &state, sizeof(state), 0);
                printf("%s changemode %s\n", user, arg[1]);
            // error occur
            }else{
                send(clientfd, &state, sizeof(state), 0);
            }

        }else{
            printf("command error\n");
        }
        show_capability_list();
    }
    
}

void show_capability_list(){
    printf("*******************************************\n");
    for(int i=0;i<num;i++){
        printf("%s %s %s %s\n", capability_list[i].accessright, capability_list[i].owner, capability_list[i].group, capability_list[i].file_name);
    }
    printf("*******************************************\n");
}

int check_access_string(char access[]){  //check rwr---
    for(int i=0;i<6;i++){
        if(i%2){
            if(access[i] != 'w' && access[i] != '-'){return INVALID_ACCESS;}
        }else{
            if(access[i] != 'r' && access[i] != '-'){return INVALID_ACCESS;}
        }
        
    }
    return SUCCESS;
}
