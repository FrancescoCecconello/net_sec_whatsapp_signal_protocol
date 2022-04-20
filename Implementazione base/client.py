import socket, threading, os
from colorama import init, Fore
from generate_keys import *
from generate_prime import *
from Crypto.Cipher import AES
import sys
from datetime import datetime

try:
	init()
	print(Fore.RESET)

	global message_key #chiave di cifratura/decifratura dei messaggi
	client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	client.connect(('127.0.0.1', 8080))

	nickname = input("Scegli il tuo nickname: ")
	client.sendall(str(nickname).encode('utf-8'))
	nicknames = [nickname]
	secret_chat = 'secret_chat_' + nickname + '.txt'

	public_keys = ["KEYS"]


	def gen_message_key():
		global message_key
		global ep_secret_key
		if nickname == nicknames[0]:
		    # Sono sul primo client
		    shk1 = shared_key(lt_pub_key_other_client, ep_secret_key, p)
		    shk2 = shared_key(ep_pub_key_other_client, ep_secret_key, p)
		    shk3 = shared_key(ep_pub_key_other_client, lt_secret_key, p)
		else:
		    # Sono sul secondo client
		    shk1 = shared_key(ep_pub_key_other_client, lt_secret_key, p)
		    shk2 = shared_key(ep_pub_key_other_client, ep_secret_key, p)
		    shk3 = shared_key(lt_pub_key_other_client, ep_secret_key, p)

		message_key = KDF(shk1, shk2, shk3)

	def receive():
		try:
		    while True:
		        from_server = client.recv(16777216).decode()
		        try:
		            from_server = eval(from_server) # trasformazione della stringa in una lista
		        except TypeError:
		            print('C\'è stato un problema durante la valutazione dei dati provenienti dal server. Per ulteriori informazioni consultare il file README. Termina la chat in entrambi i terminali client con KeyboardInterrupt (CTRL+C).')
		            sys.exit(0)
		        # Controllo del tipo di messaggio usando come flag il primo elemento della lista
		        if from_server[0] == "P-G":
		            # Ricezione dei numeri p e g dal server
		            global p
		            global g
		            p = int(from_server[1])
		            g = int(from_server[2])
		            p_chat = open('public_chat.txt','a')
		            p_chat.write(nickname + ' ha ricevuto il generatore ' + str(g) + ' e il numero primo ' + str(p) + ' da condividere con l\'altro client.\n\n')
		            p_chat.close()
		            global lt_public_key
		            global lt_secret_key
		            # generazione delle chiavi long term ed effimere
		            lt_public_key, lt_secret_key = pub_priv_keys(p, g, 16)
		            public_keys.append(lt_public_key)
		            global ep_public_key
		            global ep_secret_key
		            ep_public_key, ep_secret_key = pub_priv_keys(p, g, 16)
		            public_keys.append(ep_public_key)
		            p_chat = open('public_chat.txt','a')
		            p_chat.write(nickname + ' ha inviato la sua chiave pubblica long term e le sue chiavi effimere pubbliche al server.\n\n')
		            p_chat.write('Chiave pubblica long term di '+ nickname + ': ' + str(lt_public_key) + '\n\n')
		            p_chat.write('Chiave pubblica effimera di '+ nickname + ': ' + str(ep_public_key) + '\n\n')
		            p_chat.close()
		            s_chat = open(secret_chat,'a')
		            s_chat.write(nickname + ' ha memorizzato in locale la sua chiave segreta long term e le sue chiavi effimere segrete, oltre alle chiavi pubbliche già inviate al server.\n\n')
		            s_chat.write('Chiave segreta long term di '+ nickname + ': ' + str(lt_secret_key) + '\n\n')
		            s_chat.write('Chiave segreta effimera di ' + nickname + ': ' + str(ep_secret_key) + '\n\n')
		            s_chat.close()
		            client.sendall(str(public_keys).encode('utf-8')) # invio delle chiavi pubbliche al server (pacchetto KEYS)
		        elif from_server[0] == "MSG":
		            # Ricezione del mesaggio cifrato dall'altro client con relativa decifratura e stampa
		            global message_key
		            nonce = from_server[2]
		            cipher = AES.new(message_key, AES.MODE_EAX, nonce)
		            msg = cipher.decrypt(from_server[1])
		            if msg == 'end_chat':
		                system.exit(0)
		            p_chat = open('public_chat.txt','a')
		            p_chat.write(nickname + ' ha ricevuto il messaggio:\n ' + str(from_server) + '\n\n')
		            p_chat.close()
		            s_chat = open(secret_chat,'a')
		            s_chat.write(nickname + ' ha ricevuto un messaggio, costituito dal nonce ' + str(nonce) + ' e dal cipher text: ' + str(cipher) + ' cifrato con AES.\n\n')
		            s_chat.write(nickname + ' decifra con il segreto condiviso il cipher text, ottenendo il public text: ' + msg.decode('utf-8') + '\n\n')
		            s_chat.close()
		            now = datetime.now()
		            current_time = now.strftime("%H:%M:%S")
		            chat = open('chat.txt','a')
		            if nickname == nicknames[0]:
		                chat.write('[' + current_time + '] ' + nicknames[1] + ': ' + msg.decode('utf-8') + '\n\n')
		            else:
		                chat.write('[' + current_time + '] ' + nicknames[0] + ': ' + msg.decode('utf-8') + '\n\n')
		            chat.close()
		            print(Fore.CYAN + msg.decode() + Fore.RESET)
		        elif from_server[0] == "ENTRY":
		            # Collegamento tra i due client: vengono mandati i rispettivi nickname
		            print(Fore.YELLOW + from_server[1] + Fore.RESET)
		            nicknames.append(from_server[2])
		            nicknames.sort() # ordinamento così da differenziare i due client per il riutilizzo del codice
		        elif from_server[0] == "KEYS":
		            #Ricezione dele prime chiavi: in pos 1 si trova la chiave pubblica long term dell'altro client, pos 2 la chave effimera
		            global lt_pub_key_other_client
		            global ep_pub_key_other_client
		            lt_pub_key_other_client = int(from_server[1])
		            ep_pub_key_other_client = int(from_server[2])
		            gen_message_key() # Ricevute le chiavi, genero la message key
		            if nickname == nicknames[0]:
		                secret_chat1 = 'secret_chat_' + nickname +'.txt'
		                s_chat = open(secret_chat1,'a')
		                s_chat.write(nickname + ' ha ricevuto le chiavi pubbliche di ' + nicknames[1] + ' e può calcolare il segreto condiviso:\n' + str(message_key) + '\n\n')
		                s_chat.write(nickname + ' ha cancellato la chiave segreta effimera ' + str(ep_secret_key) + '.\n\n')
		                del ep_secret_key
		                print(ep_secret_key)
		                s_chat.close()
		            else:
		                secret_chat2 = 'secret_chat_' + nickname +'.txt'
		                s_chat = open(secret_chat2,'a')
		                s_chat.write(nickname + ' ha ricevuto le chiavi pubbliche di ' + nicknames[0] + ' e può calcolare il segreto condiviso:\n' + str(message_key) + '\n\n')
		                s_chat.write(nickname + ' ha cancellato la chiave segreta effimera ' + str(ep_secret_key) + '.\n\n')
		                del ep_secret_key
		                s_chat.close()
		        else:
		            print(Fore.RED + "Errore sulle flag" + Fore.RESET)
		except KeyboardInterrupt:
		    sys.exit(0)
		        

	def write_message():
		try:
		    while True:
		        msg = input("")
		        data = str(msg)
		        global message_key
		        cipher = AES.new(message_key, AES.MODE_EAX)
		        nonce = cipher.nonce
		        ciphertext = cipher.encrypt(str(data).encode('utf-8'))
		        # creazione del pacchetto msg: ["MSG", msg_cifrato, nonce]
		        c_msg = ["MSG"]
		        c_msg.append(ciphertext)
		        c_msg.append(nonce)
		        client.sendall(str(c_msg).encode('utf-8'))
		except KeyboardInterrupt:
		    sys.exit(0)
		    
	receive_thread = threading.Thread(target=receive)
	receive_thread.start()
	write_thread = threading.Thread(target=write_message)
	write_thread.start()
	receive_thread.join()
	write_thread.join()
	
		
except KeyboardInterrupt:
    sys.exit(0)


	

