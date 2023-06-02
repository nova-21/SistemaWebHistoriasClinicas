import os
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


# Encryption function
def encrypt_aes(key, plaintext):
    # Generate a random initialization vector (IV)
    iv = os.urandom(16)

    # Create a Cipher object using the AES algorithm in CBC mode
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())

    # Create an encryptor object from the Cipher object
    encryptor = cipher.encryptor()

    # Encrypt the plaintext using the encryptor object
    ciphertext = encryptor.update(plaintext) + encryptor.finalize()

    # Concatenate the IV and ciphertext, and encode the result using base64
    return base64.b64encode(iv + ciphertext).decode('utf-8')


# Decryption function
def decrypt_aes(key, ciphertext):
    # Decode the ciphertext from base64
    ciphertext = base64.b64decode(ciphertext.encode('utf-8'))

    # Extract the IV and ciphertext from the concatenated value
    iv = ciphertext[:16]
    ciphertext = ciphertext[16:]

    # Create a Cipher object using the AES algorithm in CBC mode
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())

    # Create a decryptor object from the Cipher object
    decryptor = cipher.decryptor()

    # Decrypt the ciphertext using the decryptor object
    plaintext = decryptor.update(ciphertext) + decryptor.finalize()

    # Return the plaintext
    return plaintext.decode('utf-8')
