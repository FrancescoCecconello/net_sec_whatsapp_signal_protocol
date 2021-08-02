from generate_keys import *
from generate_prime import *

print('#####################################')
print('####### DIFFIE - HELLMAN PER ########')
print('#######   WHATSAPP E SIGNAL  ########')
print('#####################################\n\n')

#SCELGO NUMERO PRIMO p DA CONDIVIDERE FRA ALICE E BOB

p_bit_length = 16

p = prime_generator(p_bit_length)

#SCELGO GENERATORE g DI Zp* (ricavato dal corso di crittografia)

number_of_generators = 10 #fra quanti generatori voglio scegliere casualmente? (Non serve a molto in realtà, probabilmente si può rimuovere)

generators = find_group_generators(p, number_of_generators) #lista di generatori

r = random.randint(0,len(generators)-1) #scelgo un indice casuale

g = generators[r] #prendo il generatore corrispondente

print('Alice e Bob hanno deciso di condividere il numero primo a',p_bit_length,'bit p =',p,'e il generatore g =',g,'\n\n')
# CALCOLO CHIAVI PUBBLICHE E PRIVATE LONG TERM

lt_secret_key_A, lt_secret_key_B, lt_public_key_A, lt_public_key_B = long_term_keys(p,g,16)

print('Questa conversazione verrà crittografata con le seguenti chiavi a lungo termine:\n\nChiave segreta di Alice:', lt_secret_key_A,'\nChiave segreta di Bob:',lt_secret_key_B,
'\nChiave pubblica di Alice:',lt_public_key_A,'\nChiave pubblica di Bob:',lt_public_key_B,'\n\n')

#CALCOLO CHIAVI PUBBLICHE E PRIVATE EPHIMERAL

ep_secret_key_A, ep_secret_key_B, ep_public_key_A, ep_public_key_B = ephimeral_keys(p,g,16)

print('Durante questa sessione verranno utilzzate le seguenti chiavi effimere:\n\nChiave segreta di Alice:', ep_secret_key_A,'\nChiave segreta di Bob:',ep_secret_key_B,
'\nChiave pubblica di Alice:',ep_public_key_A,'\nChiave pubblica di Bob:',ep_public_key_B,'\n\n')

#COMUNICAZIONE DA ALICE A BOB

shk1_A_to_B = shared_key(ep_secret_key_A,lt_public_key_B,p)

shk2_A_to_B = shared_key(ep_secret_key_A,ep_public_key_B,p)

shk3_A_to_B = shared_key(lt_secret_key_A,ep_public_key_B,p)

ep_secret_key_A = 0 #dimentico la chiave dopo averla usata (qui c'è da sistemare, perché devo ricalcolare le effimere una volta buttata via questa chiave)

print('Se è Alice a comunicare con Bob uso le seguenti chiavi condivise:\n\nSH-K1:',shk1_A_to_B,'\nSH-K2:',shk2_A_to_B,'\nSH-K3:',shk3_A_to_B,'\n\n')

#COMUNICAZIONE DA BOB AD ALICE

shk1_B_to_A = shared_key(ep_public_key_A,lt_secret_key_B,p)

shk2_B_to_A = shared_key(ep_public_key_A,ep_secret_key_B,p)

shk3_B_to_A = shared_key(lt_public_key_A,ep_secret_key_B,p)

ep_secret_key_B = 0 #dimentico la chiave dopo averla usata (qui c'è da sistemare, perché devo ricalcolare le effimere una volta buttata via questa chiave)

print('Se è Bob a comunicare con Alice uso le seguenti chiavi condivise:\n\nSH-K1:',shk1_B_to_A,'\nSH-K2:',shk2_B_to_A,'\nSH-K3:',shk3_B_to_A,'\n\n')	
