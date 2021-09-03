import socket, threading, os
import sys
from colorama import init, Fore
from generate_keys import concat_KDF
from Crypto.Cipher import AES
from datetime import datetime
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.exceptions import InvalidSignature

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

	# Il metodo exchange crea la shared key
	# concat_KDF concatena le shared key per ottenere il segreto condiviso fra i due client
	def gen_message_key():
		global message_key
		if nickname == nicknames[0]:
			# Sono sul primo client
			shk1 = ep_secret_key.exchange(lt_pub_key_other_client)
			shk2 = ep_secret_key.exchange(ep_pub_key_other_client)
			shk3 = lt_x_secret_key.exchange(ep_pub_key_other_client)
		else:
			# Sono sul secondo client
			shk1 = lt_x_secret_key.exchange(ep_pub_key_other_client)
			shk2 = ep_secret_key.exchange(ep_pub_key_other_client)
			shk3 = ep_secret_key.exchange(lt_pub_key_other_client)
		message_key = concat_KDF(shk1, shk2, shk3)

	def receive():
		try:
			while True:
				from_server = client.recv(16777216).decode()
				try:
					from_server = eval(from_server) # trasformo la stringa in una lista
				except TypeError:
					print(Fore.RED + 'C\'è stato un problema durante la valutazione dei dati provenienti dal server. Per ulteriori informazioni consultare il file README. Termina la chat in entrambi i terminali client con KeyboardInterrupt (CTRL+C).')
					sys.exit(0)
				# Controllo il tipo di messaggio usando come flag il primo elemento della lista
				if from_server[0] == "REQKEYS":
					# Il server richiede la mia chiave pubblica long term e una chiave effimera da usare per fare l'handshake con l'altro client. 
					# Nella reale implementazione di X3DH devo generare molte chiavi effimere, poiché ognuna viene usata per fare l'handshake con ogni utente
					# che voglia iniziare una conversazione con me. In questo caso viene richiesto di dialogare con un solo utente, quindi basta generare una
					# sola chiave effimera.
					
					global lt_x_secret_key
					global ep_secret_key
					global ep_public_key
					
					# Creo una chiave long term segreta di tipo Ed25519 per consentire la firma digitale e l'autenticazione
					lt_ed_secret_key = Ed25519PrivateKey.generate()
					
					# Calcolo la corrispondente chiave pubblica (sempre di tipo Ed25519)
					lt_ed_public_key = lt_ed_secret_key.public_key()
					
					# Converto le chiavi in byte
					ed_secret_bytes =lt_ed_secret_key.private_bytes(encoding=serialization.Encoding.Raw,format=serialization.PrivateFormat.Raw,encryption_algorithm=serialization.NoEncryption())	
					ed_public_bytes = lt_ed_public_key.public_bytes(encoding=serialization.Encoding.Raw,format=serialization.PublicFormat.Raw)
					
					# Genero la stessa chiave segreta long term, ma stavolta di tipo X25519 per consentire il calcolo delle shared key
					lt_x_secret_key = x25519.X25519PrivateKey.from_private_bytes(ed_secret_bytes)
					
					# Calcolo la corrispondente chiave pubblica
					lt_x_public_key = lt_x_secret_key.public_key()
					
					# Converto le chiavi in byte (secret_bytes serve solo per la descrizione in public_chat.txt, nel protocollo non servirebbe calcolarlo)
					secret_bytes = lt_x_secret_key.private_bytes(encoding=serialization.Encoding.Raw,format=serialization.PrivateFormat.Raw,encryption_algorithm=serialization.NoEncryption())
					public_bytes = lt_x_public_key.public_bytes(encoding=serialization.Encoding.Raw,format=serialization.PublicFormat.Raw)
					
					# Dato che non posso inviare direttamente le chiavi tramite i socket, invio al server i byte dalle quali ricavarle
					public_keys.append(public_bytes)
					
					# Creo la chiave effimera segreta
					ep_secret_key = X25519PrivateKey.generate()
					
					# Calcolo la chiave effimera pubblica e invio al server i byte per ricavarla
					ep_secret_bytes = ep_secret_key.private_bytes(encoding=serialization.Encoding.Raw,format=serialization.PrivateFormat.Raw,encryption_algorithm=serialization.NoEncryption())
					ep_public_key = ep_secret_key.public_key()
					ep_public_bytes = ep_public_key.public_bytes(encoding=serialization.Encoding.Raw,format=serialization.PublicFormat.Raw)
					public_keys.append(ep_public_bytes)	# aggiungo quelle pubbliche a quelle da mandare al server
					
					# Genero la firma per la chiave segreta long term. b'auth' è il messaggio che deve controllare il verificatore per certificare la mia identità all'altro client
					signature = lt_ed_secret_key.sign(b'auth')
					
					# Invio i byte per calcolare la chiave pubblica di tipo Ed25519
					public_keys.append(ed_public_bytes)
					
					# Invio la firma
					public_keys.append(signature)
					
					p_chat = open('public_chat.txt','a')
					p_chat.write(nickname + ' ha inviato la sua chiave pubblica long term e la sua chiave effimera pubblica al server.\n\n')
					p_chat.write('Chiave pubblica long term di '+ nickname + ': ' + str(public_bytes) + '\n\n')
					p_chat.write('Chiave pubblica effimera di '+ nickname + ': ' + str(ed_public_bytes) + '\n\n')
					p_chat.close()
					s_chat = open(secret_chat,'a')
					s_chat.write(nickname + ' ha memorizzato in locale la sua chiave segreta long term e la sua chiave effimera segreta, oltre alle chiavi pubbliche già inviate al server.\n\n')
					s_chat.write('Chiave segreta long term di '+ nickname + ': ' + str(secret_bytes) + '\n\n')
					s_chat.write('Chiave segreta effimera di ' + nickname + ': ' + str(ep_secret_bytes) + '\n\n')
					s_chat.close()
					
					# Invio al server le chiavi pubbliche sotto forma di byte e la firma (pacchetto KEYS)
					client.sendall(str(public_keys).encode('utf-8')) 
				
				
				elif from_server[0] == "MSG":
					# Ricezione di un messaggio da parte dell'altro client
					
					global message_key
					
					# Genero il nonce
					nonce = from_server[2]
					
					# Creo un'istanza di AES
					cipher = AES.new(message_key, AES.MODE_EAX, nonce)
					
					# Decifro il contenuto del messaggio ottenendo i byte corrispondenti
					msg = cipher.decrypt(from_server[1])
					p_chat = open('public_chat.txt','a')
					p_chat.write(nickname + ' ha ricevuto il messaggio:\n ' + str(from_server) + '\n\n')
					p_chat.close()
					s_chat = open(secret_chat,'a')
					s_chat.write(nickname + ' ha ricevuto un messaggio, costituito dal nonce ' + str(nonce) + ' e dal cipher text: ' + str(cipher) + ' cifrato con AES.\n\n')
					s_chat.write(nickname + ' decifra con il segreto condiviso il cipher text, ottenendo il plain text: ' + msg.decode('utf-8') + '\n\n')
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
					# Ricezione dele prime chiavi: 
					# 	[1]: chiave pubblica long term in byte dell'altro client per X25519
					# 	[2]: chiave pubblica effimera in byte dell'altro client
					# 	[3]: chiave pubblica long term in byte dell'altro client per Ed25519 (firmata)
					# 	[4]: firma dell'altro client
					
					global lt_pub_key_other_client
					global ep_pub_key_other_client
					
					# Ricostruisco la chiave pubblica long term dell'altro client dai byte (X25519)
					lt_pub_key_other_client = x25519.X25519PublicKey.from_public_bytes(from_server[1])
					
					# Ricostruisco la chiave pubblica effimera dell'altro client dai byte (X25519)
					ep_pub_key_other_client = x25519.X25519PublicKey.from_public_bytes(from_server[2])
					
					# Ricostruisco la chiave pubblica firmata dell'altro client (Ed25519)
					signed_pub_key_other_client = ed25519.Ed25519PublicKey.from_public_bytes(from_server[3])
					
					# Prendo la firma
					signature = from_server[4]
					
					try:
						# Controllo la validità della firma
						signed_pub_key_other_client.verify(signature,b'auth')
						
						if nickname == nicknames[0]:
							secret_chat1 = 'secret_chat_' + nickname +'.txt'
							s_chat = open(secret_chat1,'a')
							s_chat.write(nickname + ' ha ricevuto una chiave autenticata.\n\n')
							s_chat.close()
						else:
							secret_chat2 = 'secret_chat_' + nickname +'.txt'
							s_chat = open(secret_chat2,'a')
							s_chat.write(nickname + ' ha ricevuto una chiave autenticata.\n\n')
							s_chat.close()
						
						# Se non è valida termino la conversazione
					except InvalidSignature:
						if nickname == nicknames[0]:
							secret_chat1 = 'secret_chat_' + nickname +'.txt'
							s_chat = open(secret_chat1,'a')
							s_chat.write(nickname + ' ha ricevuto una chiave non autenticata e non può certificare l\'identità di ' + nicknames[1] + '.\n\n')
							s_chat.close()
						else:
							secret_chat2 = 'secret_chat_' + nickname +'.txt'
							s_chat = open(secret_chat2,'a')
							s_chat.write(nickname + ' ha ricevuto una chiave non autenticata e non può certificare l\'identità di ' + nicknames[0] + '.\n\n')
							s_chat.close()
						print('Non è possibile certificare l\'identità di uno dei due client. La chat verrà terminata.')
						sys.exit(0)
					
					# Dopo aver verificato l'autenticità della chiave pubblica, genero il segreto condiviso
					gen_message_key() 
					
					if nickname == nicknames[0]:
						secret_chat1 = 'secret_chat_' + nickname +'.txt'
						s_chat = open(secret_chat1,'a')
						s_chat.write(nickname + ' ha ricevuto le chiavi pubbliche di ' + nicknames[1] + ' e può calcolare il segreto condiviso:\n' + str(message_key) + '\n\n')
						s_chat.close()
					else:
						secret_chat2 = 'secret_chat_' + nickname +'.txt'
						s_chat = open(secret_chat2,'a')
						s_chat.write(nickname + ' ha ricevuto le chiavi pubbliche di ' + nicknames[0] + ' e può calcolare il segreto condiviso:\n' + str(message_key) + '\n\n')
						s_chat.close()
					p_chat = open('public_chat.txt','a')
					p_chat.write(nickname + ' ha usato e dimenticato la chiave effimera segreta corrispondente a quella pubblica inviata al server.\n\n')
					p_chat.close()
					s_chat = open(secret_chat,'a')
					s_chat.write(nickname + ' ha usato e dimenticato la chiave effimera segreta corrispondente a quella pubblica inviata al server.\n\n')
					s_chat.close()
					
					# Elimino la chiave effimera segreta per evitare replay attack
					del ep_secret_key
				else:
					print(Fore.RED + "Errore sulle flag" + Fore.RESET)
		except KeyboardInterrupt:
			sys.exit(0)
				

	def write_message():
		try:
			while True:
				# Input del messaggio
				msg = input("")
				
				# Converto in stringa
				data = str(msg)
				
				# Genero un'istanza di AES
				cipher = AES.new(message_key, AES.MODE_EAX)
				
				# Genero un nonce
				nonce = cipher.nonce
				
				# Genero il ciphertext
				ciphertext = cipher.encrypt(str(data).encode('utf-8'))
				
				# Creo il pacchetto MSG: ["MSG", msg_cifrato, nonce]
				c_msg = ["MSG"]
				c_msg.append(ciphertext)
				c_msg.append(nonce)
				client.sendall(str(c_msg).encode('utf-8'))
		except KeyboardInterrupt:
			sys.exit(0)
	
	# Faccio partire i thread in parallelo per ricevere e mandare messaggi
	receive_thread = threading.Thread(target=receive)
	receive_thread.start()
	write_thread = threading.Thread(target=write_message)
	write_thread.start()
	receive_thread.join()
	write_thread.join()
	
		
except KeyboardInterrupt:
	sys.exit(0)



	

