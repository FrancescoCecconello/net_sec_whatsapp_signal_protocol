import hashlib
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.concatkdf import ConcatKDFHMAC
from cryptography.hazmat.backends import default_backend



def concat_KDF(key1, key2, key3):
    # GENERO IL SEGRETO CONDIVISO

    # prima iterazione di KDF
    backend = default_backend()
    salt = b'saltsaltsalt'
    kdf = ConcatKDFHMAC(algorithm=hashes.SHA256(), length=32, salt=salt, otherinfo=None,backend=backend)
    chain_key = kdf.derive(key1)
    kdf = ConcatKDFHMAC(algorithm=hashes.SHA256(), length=32, salt=salt, otherinfo=None,backend=backend)
    kdf.verify(key1, chain_key) # stampa una eccezione se le chiavi non corrispondono

    # seconda iterazione di kdf
    kdf2 = ConcatKDFHMAC(algorithm=hashes.SHA256(), length=32, salt=salt, otherinfo=None,backend=backend)
    message_key = kdf2.derive(chain_key.hex().encode('utf8'))
    kdf2 = ConcatKDFHMAC(algorithm=hashes.SHA256(), length=32, salt=salt, otherinfo=None,backend=backend)
    kdf2.verify(chain_key.hex().encode('utf8'), message_key)

    return message_key



