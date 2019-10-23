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
from create_socket import *


class Equipment:

    def __init__(self, name, port = 80, validity_days = 10):
        self.validity_days = validity_days
        self.myname = name
        self.myport = port
        self.mykey = PaireClesRSA()
        self.mycert = Certificat(self.myname, self.mykey.public(),self.mykey.private(), self.validity_days)

        ''' When we create an equipment, we start a thread that opens a server socket to listen to others '''
        self.thread_server = threading.Thread(target=open_socket_server, args=(self, 'localhost', port))
        self.thread_server.start()

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

    def certify(self, other_equipment):
        cert = Certificat(self.myname, other_equipment.mykey.public(), self.mykey.private(), 10)
        return cert

    def connect_to_equipment(self, equipment):
        """ Start a thread that open a client socket connected to the server socket of another equipement """
        """ We should use different open_socket_client to have a different behaviour for what we want to ask to the other equipment (add, sync..) """
        y = threading.Thread(target=open_socket_client, args=(self, 'localhost', equipment.myport))
        y.start()
        y.join()







