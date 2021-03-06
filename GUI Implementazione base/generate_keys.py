import hashlib
import sys
import random
from generate_prime import prime_generator
from generator_finder import find_group_generators
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.concatkdf import ConcatKDFHMAC
from cryptography.hazmat.backends import default_backend

def pub_priv_keys(p, g, secret_key_length):

	#GENERO LA CHIAVEI PRIVATA DELL'UTENTE IN MODO CHE SIA PRIMA RISPETTO A p
	secret_key = prime_generator(secret_key_length)

	#CALCOLO LA CHIAVE PUBBLICHA 

	public_key = (g**secret_key) % p	
	
	return(public_key,secret_key)
	
def shared_key(key1,key2,p):

	# CALCOLO SHARED KEY

	return hashlib.sha256(str((key1**key2) % p).encode()).hexdigest()

def KDF(key1, key2, key3):
    # GENERO IL SEGRETO CONDIVISO

    # prima iterazione di KDF
    backend = default_backend()
    salt = b'saltsaltsalt'
    kdf = ConcatKDFHMAC(algorithm=hashes.SHA256(), length=32, salt=salt, otherinfo=key2.encode('utf8'),backend=backend)
    chain_key = kdf.derive(key1.encode('utf8'))
    kdf = ConcatKDFHMAC(algorithm=hashes.SHA256(), length=32, salt=salt, otherinfo=key2.encode('utf8'),backend=backend)
    kdf.verify(key1.encode('utf8'), chain_key) # stampa una eccezione se le chiavi non corrispondono

    # seconda iterazione di kdf
    kdf2 = ConcatKDFHMAC(algorithm=hashes.SHA256(), length=32, salt=salt, otherinfo=key3.encode('utf8'),backend=backend)
    message_key = kdf2.derive(chain_key.hex().encode('utf8'))
    kdf2 = ConcatKDFHMAC(algorithm=hashes.SHA256(), length=32, salt=salt, otherinfo=key3.encode('utf8'),backend=backend)
    kdf2.verify(chain_key.hex().encode('utf8'), message_key)

    return message_key



