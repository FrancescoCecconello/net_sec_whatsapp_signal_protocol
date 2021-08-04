import socket, threading
from generate_keys import *
from generate_prime import *

############################################################################
########################                            ########################
########################  GENERAZIONE DELLE CHIAVI  ########################
########################                            ########################
############################################################################

#SCELGO NUMERO PRIMO p DA CONDIVIDERE FRA ALICE E BOB

p_bit_length = 16

p = prime_generator(p_bit_length)

#SCELGO GENERATORE g DI Zp* (ricavato dal corso di crittografia)

number_of_generators = 10 #fra quanti generatori voglio scegliere casualmente? (Non serve a molto in realtà, probabilmente si può rimuovere)

generators = find_group_generators(p, number_of_generators) #lista di generatori

r = random.randint(0,len(generators)-1) #scelgo un indice casuale

g = generators[r] #prendo il generatore corrispondente

lt_public_key, lt_secret_key = pub_priv_keys(p,g,16) #calcolo le chiavi long-term

ep_public_keys = []

ep_secret_keys = {} 

nickname = input("Scegli il tuo nickname: ")

nickname_and_public_keys = [nickname,lt_public_key]
for i in range (16): #creo 16 chiavi
	ep_public_key, ep_secret_key = pub_priv_keys(p,g,16) #calcolo le chiavi ephimeral
	nickname_and_public_keys.append(ep_public_key) #aggiungo quelle pubbliche a quelle da mandare al server
	ep_secret_keys[ep_public_key] = ep_secret_key #creo un dizionario per ricordarmi la corrispondenza fra le chiavi pubbliche e private


############################################################################
########################                            ########################
########################        LATO CLIENT         ########################
########################                            ########################
############################################################################


nickname_and_public_keys = str(nickname_and_public_keys)
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)      
client.connect(('127.0.0.1', 9000))                            
def receive():
    while True:  
        message = client.recv(1024).decode('ascii')
        if message == 'NICKNAME':
           client.send(nickname_and_public_keys.encode('ascii'))
           del message
        elif str(message[0:6]) == 'PUBKEY': 
                print('Il server ha scelto per me la chiave effimera pubblica',message[6:])
                del message
        else:
           print(message)
           del message
   		
def write():
    while True:                                                 
        message = '{}: {}'.format(nickname, input(''))
        client.send(message.encode('ascii'))

receive_thread = threading.Thread(target=receive)               
receive_thread.start()
write_thread = threading.Thread(target=write)                   
write_thread.start()
