import hashlib
import sys
import random
from generate_prime import prime_generator
from is_prime import is_prime
from generator_finder import find_group_generators

#####################################################################################
############################                             ############################
############################          LONG TERM          ############################
############################                             ############################
#####################################################################################

def long_term_keys(p, g, secret_key_length):

	#GENERO LE CHIAVI PRIVATE DI ALICE E BOB

	long_term_secret_key_A = prime_generator(secret_key_length) #genero un primo casuale di 20 bit

	long_term_secret_key_B = prime_generator(secret_key_length) #genero un primo casuale di 20 bit

	#CALCOLO LE CHIAVI PUBBLICHE DI ALICE E BOB

	long_term_public_key_A = (g**long_term_secret_key_A) % p

	long_term_public_key_B = (g**long_term_secret_key_B) % p

	return(long_term_secret_key_A,long_term_secret_key_B,long_term_public_key_A,long_term_public_key_B)

#####################################################################################
############################                             ############################
############################          EPHIMERAL          ############################
############################                             ############################
#####################################################################################

def ephimeral_keys(p, g, secret_key_length):

	#GENERO LE CHIAVI PRIVATE DI ALICE E BOB

	ephimeral_secret_key_A = prime_generator(secret_key_length)

	ephimeral_secret_key_B = prime_generator(secret_key_length)

	# CALCOLO LE CHIAVI PUBBLICHE DI ALICE E BOB

	ephimeral_public_key_A = (g**ephimeral_secret_key_A) % p

	ephimeral_public_key_B = (g**ephimeral_secret_key_B) % p

	return(ephimeral_secret_key_A,ephimeral_secret_key_B,ephimeral_public_key_A,ephimeral_public_key_B)
	
def shared_key(key1,key2,p):

	# CALCOLO IL SEGRETO CONDIVISO

	return hashlib.sha256(str((key1**key2) % p).encode()).hexdigest()
	
