from Equipement import Equipment
from Certificat import Certificat
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa


class PaireClesRSA():

    def __init__(self):
        # generate key pair
        keypair = rsa.generate_private_key(public_exponent=65537,
                                           key_size=2048,
                                           backend=default_backend())
        self.keypair = keypair

    def public(self):
        return self.keypair.public_key()

    def private(self):
        return self.keypair

