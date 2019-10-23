from PaireClesRSA import *
from Certificat import Certificat

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


class Equipment():

    def __init__(self, name, port = 80, validity_days = 10):
        self.validity_days = validity_days
        self.myname = name
        self.myport = port
        self.mykey = PaireClesRSA()
        self.mycert = Certificat(self.name, self.keypair, self.validity_days)

    def affichage_da(self):
        print()

    def affichage_ca(self):
        print()

    def affichage(self):
        print("Equipment name: ", self.myname(), "Equipment port :", self.myport)

    def myname(self):
        return self.myname

    def mypubkey(self):
        return self.mykey.public()

    def mycert(self):
        return self.mycert




