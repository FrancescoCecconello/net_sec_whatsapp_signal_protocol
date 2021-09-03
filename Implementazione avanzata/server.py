import socket, threading
import time
import sys
from socket import error as SocketError
import errno
from nice_text import center

try:
	p_chat = open('public_chat.txt','w')
	p_chat.write(center('Questo file contiene la trascrizione della chat tra Alice e Bob dal punto di vista di un agente esterno.',20))
	p_chat.close()
	chat = open('chat.txt','w')
	chat.write(center('Questo file contiene la trascrizione della chat in chiaro e rappresenta il front-end.',20))
	chat.close()
	
	# Creo un server all'indirizzo 127.0.0.1, porta 8080
	
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server.bind(('127.0.0.1', 8080))
	server.listen(5)

	nicknames = []
	clients = []


	# Connessione con i due client
	for _ in range(0, 2):
		client, addr = server.accept()
		nick = client.recv(16777216).decode('utf-8')
		secret_chat = 'secret_chat_' + nick + '.txt'
		nicknames.append(nick)
		clients.append(client)
		s_chat = open(secret_chat,'w')
		text = 'Chat dal punto di vista di ' + nick
		s_chat.write(center(text,20))
		s_chat.close()
	

	# Richiedo le chiavi pubbliche ai client
	clients[0].sendall(str(["REQKEYS"]).encode('utf-8'))
	clients[1].sendall(str(["REQKEYS"]).encode('utf-8'))


	# Sincronizzazione dei due client
	for i in range(0, 2):
		data = ["ENTRY"]
		msg = "Sei connesso con "
		if i == 0:
		    nick = nicknames[1]
		else:
		    nick = nicknames[0]
		client = clients[i]
		msg += str(nick)
		data.append(msg)
		data.append(nick)
		client.sendall(str(data).encode('utf-8'))
		time.sleep(0.5) # do il tempo per sincronizzarsi


	# Classi con thread per l'inoltro dei messaggi tra i due client
	class inoltroToSecond(threading.Thread):
		def __init__(self):
		    threading.Thread.__init__(self)

		def run(self):
		    secret_chat_A = 'secret_chat_' + nicknames[0] +'.txt'
		    secret_chat_B = 'secret_chat_' + nicknames[1] +'.txt'
		    while True:
		        client = clients[1]
		        try:
		        	# Ricevo i dati da inoltrare ai client
		            data = client.recv(16777216).decode('utf-8')
		        except SocketError as e:
		            if e.errno != errno.ECONNRESET:
		                raise 
		            server.close()
		            p_chat = open('public_chat.txt','a')
		            p_chat.write('La chat è stata chiusa dai client.')
		            p_chat.close()
		            s_chat_A = open(secret_chat_A,'a')                                                                                                          
		            s_chat_A.write('La chat è stata chiusa dai client.')
		            s_chat_A.close()
		            s_chat_B = open(secret_chat_B,'a')                                                                                                          
		            s_chat_B.write('La chat è stata chiusa dai client.')
		            s_chat_B.close()
		            sys.exit(0)
		        
		        client = clients[0]
		        if not data:
		            p_chat = open('public_chat.txt','a')
		            p_chat.write('La chat è stata chiusa dai client.')
		            p_chat.close()
		            s_chat_A = open(secret_chat_A,'a')                                                                                                          
		            s_chat_A.write('La chat è stata chiusa dai client.')
		            s_chat_A.close()
		            s_chat_B = open(secret_chat_B,'a')                                                                                                          
		            s_chat_B.write('La chat è stata chiusa dai client.')
		            s_chat_B.close()
		            sys.exit(0)		            
		        else:
		            data = eval(data)
		            client.sendall(str(data).encode('utf-8'))
				
	class inoltroToFirst(threading.Thread):
		def __init__(self):
		    threading.Thread.__init__(self)

		def run(self):
		    while True:
		        client = clients[0]
		        try:
		            data = client.recv(16777216).decode('utf-8')
		        except SocketError as e:
		            if e.errno != errno.ECONNRESET:
		                raise 
		            server.close()
		            sys.exit(0)
		        #print(nicknames[0] + " ha mandato: " + data)
		        client = clients[1]
		        if not data:
		            sys.exit(0)		            
		        else:    
		            data = eval(data)
		            client.sendall(str(data).encode('utf-8'))
		            
	# Thread per ricevere e inoltrare i messaggi	                              
	a=inoltroToFirst()
	b=inoltroToSecond()
	a.start()
	b.start()
	
except KeyboardInterrupt:
	sys.exit(0)
