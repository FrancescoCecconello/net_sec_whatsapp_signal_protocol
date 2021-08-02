import hashlib
import sys
import random
from generate_prime import prime_generator
from is_prime import is_prime
from generator_finder import find_group_generators

def pub_priv_keys(p, g, secret_key_length):

	#GENERO LE CHIAVI PRIVATE DELL'UTENTE

	secret_key = prime_generator(secret_key_length) #genero un primo casuale di 20 bit

	#CALCOLO LE CHIAVI PUBBLICHE DI ALICE E BOB

	public_key = (g**secret_key) % p	
	
	return(public_key,secret_key)
	
def shared_key(key1,key2,p):

	# CALCOLO IL SEGRETO CONDIVISO

	return hashlib.sha256(str((key1**key2) % p).encode()).hexdigest()
	
