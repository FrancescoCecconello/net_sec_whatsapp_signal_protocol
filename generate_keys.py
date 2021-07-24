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

def long_term_keys(p_length, secret_key_length):

	# SCELGO UN NUMERO PRIMO DA CONDIVIDERE FRA ALICE E BOB 

	long_term_p = prime_generator(p_length) #genero un bit casuale di 10 bit

	#GENERO LE CHIAVI PRIVATE DI ALICE E BOB

	long_term_secret_key_A = prime_generator(secret_key_length) #genero un primo casuale di 20 bit

	long_term_secret_key_B = prime_generator(secret_key_length) #genero un primo casuale di 20 bit

	# CALCOLO IL GENERATORE DEL GRUPPO CICLICO Zp* 

	number_of_long_term_generators = 3 #fra quanti generatori voglio scegliere casualmente? (Non serve a molto in realtà, probabilmente si può rimuovere)

	lt_generators = find_group_generators(long_term_p, number_of_long_term_generators) #lista di generatori

	rl = random.randint(0,len(lt_generators)-1) #scelgo un indice casuale

	long_term_g = lt_generators[rl] #prendo il generatore corrispondente

	# CALCOLO LE CHIAVI PUBBLICHE DI ALICE E BOB

	long_term_public_key_A = (long_term_g**long_term_secret_key_A) % long_term_p

	long_term_public_key_B = (long_term_g**long_term_secret_key_B) % long_term_p

	# CALCOLO IL SEGRETO CONDIVISO

	shared_lt=hashlib.sha256(str((long_term_public_key_B**long_term_secret_key_A) % long_term_p).encode()).hexdigest()

	return(long_term_secret_key_A,long_term_secret_key_B,long_term_public_key_A,long_term_public_key_B,shared_lt)

#####################################################################################
############################                             ############################
############################          EPHIMERAL          ############################
############################                             ############################
#####################################################################################

def ephimeral_keys(p_length, secret_key_length):

	# SCELGO UN NUMERO PRIMO DA CONDIVIDERE FRA ALICE E BOB 

	ephimeral_p = prime_generator(p_length)

	#GENERO LE CHIAVI PRIVATE DI ALICE E BOB

	ephimeral_secret_key_A = prime_generator(secret_key_length)

	ephimeral_secret_key_B = prime_generator(secret_key_length)

	number_of_ephimeral_generators = 10

	# CALCOLO IL GENERATORE DEL GRUPPO CICLICO Zp* 

	e_generators = find_group_generators(ephimeral_p, number_of_ephimeral_generators)

	re= random.randint(0,len(e_generators)-1)

	ephimeral_g = e_generators[re]

	# CALCOLO LE CHIAVI PUBBLICHE DI ALICE E BOB

	ephimeral_public_key_A = (ephimeral_g**ephimeral_secret_key_A) % ephimeral_p

	ephimeral_public_key_B = (ephimeral_g**ephimeral_secret_key_B) % ephimeral_p

	# CALCOLO IL SEGRETO CONDIVISO

	shared_eph=hashlib.sha256(str((ephimeral_public_key_B**ephimeral_secret_key_A) % ephimeral_p).encode()).hexdigest()

	return(ephimeral_secret_key_A,ephimeral_secret_key_B,ephimeral_public_key_A,ephimeral_public_key_B,shared_eph)
