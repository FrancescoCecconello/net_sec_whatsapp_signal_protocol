from generate_keys import *

print('#####################################')
print('####### DIFFIE - HELLMAN PER ########')
print('#######   WHATSAPP E SIGNAL  ########')
print('#####################################\n\n')
lt_secret_key_A, lt_secret_key_B, lt_public_key_A, lt_public_key_B, lt_shared_secret = long_term_keys(8,16)

print('Questa conversazione verrà crittografata con le seguenti chiavi a lungo termine:\nChiave segreta di Alice:', lt_secret_key_A,'\nChiave segreta di Bob:',lt_secret_key_B,
'\nChiave pubblica di Alice:',lt_public_key_A,'\nChiave pubblica di Bob:',lt_public_key_B,'\nChiave condivisa:',lt_shared_secret,'\n\n')

ep_secret_key_A, ep_secret_key_B, ep_public_key_A, ep_public_key_B, ep_shared_secret = ephimeral_keys(8,16)

print('Durante questa sessione verranno utilzzate le seguenti chiavi effimere:\nChiave segreta di Alice:', ep_secret_key_A,'\nChiave segreta di Bob:',ep_secret_key_B,
'\nChiave pubblica di Alice:',ep_public_key_A,'\nChiave pubblica di Bob:',ep_public_key_B,'\nChiave condivisa:',ep_shared_secret)
		
	
