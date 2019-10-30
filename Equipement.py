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

    def __init__(self, name, port=80, validity_days=10):
        self.validity_days = validity_days
        self.name = name
        self.port = port
        self.keypair = PaireClesRSA()
        self.cert = Certificat()
        self.cert.create_cert(self.name, self.keypair.public(), self.keypair.private(), self.validity_days)

        ''' When we create an equipment, we start a thread that opens a server socket to listen to others '''
        self.thread_server = threading.Thread(target=open_socket_server, args=(self, 'localhost'))
        self.thread_server.start()
        self.ca = {}
        self.da = {}

    def affichage_da(self):
        print()

    def affichage_ca(self):
        print(self.ca)

    def affichage(self):
        print("Equipment name: ", self.name, "Equipment port :", self.port)
        print(self.cert.x509.public_bytes(serialization.Encoding.PEM))

    def name(self):
        return self.name

    def pub_key(self):
        return self.keypair.public()

    def cert(self):
        return self.cert

    def certify(self, pub_key):
        cert = Certificat()
        cert.create_cert(self.name, pub_key, self.keypair.private(), 10)
        return cert

    def connect_to_equipment(self, equipment):
        """ Start a thread that open a client socket connected to the server socket of another equipement """
        """ We should use different open_socket_client to have a different behaviour for what we want to ask to the other equipment (add, sync..) """
        y = threading.Thread(target=open_socket_client, args=(self, 'localhost', equipment))
        y.start()
        y.join()

    def add_ca(self, certifying_equipment_name, certified_equipment_name, cert, certifying_equipment_pub_key):
        # if CA already contains the equipment, simply add the certified equipment
        if self.ca.get(certifying_equipment_name, False):
            self.ca[certifying_equipment_name][certified_equipment_name] = (cert, certifying_equipment_pub_key)
        # else, create a new key for the equipment containing a dictionary with the certified equipment
        else:
            self.ca[certifying_equipment_name] = {certified_equipment_name: (cert, certifying_equipment_pub_key)}



