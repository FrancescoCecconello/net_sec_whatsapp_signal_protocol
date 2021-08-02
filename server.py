import socket, threading                                             
import pickle

host = '127.0.0.1'                                                     
port = 9000     
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)     
server.bind((host, port))                                           
server.listen()
clients = []
nicknames = []
long_term_public_keys = {}
ephimeral_public_keys = {}
def broadcast(message):                                      
    for client in clients:
        client.send(message)
        
def handle(client):                                         
    while True:
        try:                                        
            message = client.recv(1024)
            broadcast(message)
        except:                                          
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            broadcast('{} left!'.format(nickname).encode('ascii'))
            nicknames.remove(nickname)
            break

def receive():      
    while True:
        client, address = server.accept()
        print("Connesso a {}".format(str(address)))       
        client.send('NICKNAME'.encode('ascii'))
        name_and_pubkeys = client.recv(1024).decode('ascii')
        name_and_pubkeys = eval(name_and_pubkeys) # eval() trasforma le stringhe in liste
        print('Chiave pubblica long term di', name_and_pubkeys[0],':',name_and_pubkeys[1])
        print('Chiavi pubbliche ephimeral di', name_and_pubkeys[0],':',name_and_pubkeys[2:])
        nickname = name_and_pubkeys[0]
        nicknames.append(nickname)
        clients.append(client)
        print('\n\n')
        client.send('Connesso al server.'.encode('ascii'))
        long_term_public_keys[client] = name_and_pubkeys[1]
        ephimeral_public_keys[client] = name_and_pubkeys[2:]
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

receive()
