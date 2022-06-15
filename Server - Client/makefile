all:server/server.out client/client.out

server/server.out:server/server.c
	gcc -o server/server.out server/server.c -pthread

client/client.out:client/client.c
	gcc -o client/client.out client/client.c

clean:
	rm -f */*.out
