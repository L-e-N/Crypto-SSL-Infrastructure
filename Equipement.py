from PaireClesRSA import PaireClesRSA


from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from Certificat import Certificat


class Equipment:

    def __init__(self, name, port = 80, validity_days = 10):
        self.validity_days = validity_days
        self.myname = name
        self.myport = port
        self.mykey = PaireClesRSA()
        self.mycert = Certificat(self.myname, self.mykey.public(),self.mykey.private(), self.validity_days)

    def affichage_da(self):
        print()

    def affichage_ca(self):
        print()

    def affichage(self):
        print("Equipment name: ", self.myname, "Equipment port :", self.myport)
        print(self.mycert.x509.public_bytes(serialization.Encoding.PEM))

    def myname(self):
        return self.myname

    def mypubkey(self):
        return self.mykey.public()

    def mycert(self):
        return self.mycert




