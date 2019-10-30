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
from itertools import chain

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

    def synchronize_da(self, equipment):
        # add the (keys,values) from equipment.da and equipment.ca that are NOT in self.da
        self.da = dict(dict(equipment.da, **equipment.ca), **self.da)
        for sda in self.da:
            # for each key of self.DA, add all the (key,value) of equipment.CA[key] and DA[key] that are not in self.DA[key]
            self.da[sda] = dict(dict(equipment.da.get(sda, {}), **equipment.ca.get(sda, {})), **self.da[sda])

    # is there a path from the current equipment to another equipment ?
    def chain_exists(self, equipment):
        # pick a dictionary which contains the end node
        dic = {}
        for eda, v in chain(equipment.da):
            if v.get(self.name, False):
                dic = v
                break
        if dic == {}:
            return False  # the chain does not exist
        else:
            findchain(self.name, equipment.name, v)


def findchain(start, end, graph):
    return ""


# tests for dictionary unions
"""  a -- b -- c """
CAa = {'b': {'a': ('certba', 'pubb')}}
CAb = {'a': {'b': ('certab', 'puba')}, 'c': {'b': ('certcb', 'pubc')}}
CAc = {'b': {'c': ('certbc', 'pubc')}}
DAa = {'c': {'b': ('certcb', 'pubc')}}
DAb = {}
DAc = {'c': {'b': ('certcbprime', 'pubc')}}
# NOTE : dict(CAa, **DAc) union only with the keys. Does not go in depth. If key conflict, DAc values are used
# Same for CAa.update(DAc), which updates the CAa values with the DAc values



# DAafter = defaultdict(list)
# for k, v in chain(CAa.items(), DAa.items()):
#    DAafter[k].append(v)


def synchrodict(DAa, DAc, CAc):
    DAabis = dict(dict(DAc, **CAc), **DAa)

    for sda in DAa:
        # for each key of self.DA, add all the keys of equipment.CA and DA that are not in self.DA
        DAabis[sda] = dict(dict(DAc.get(sda, {}), **CAc.get(sda, {})), **DAa[sda])
    return DAabis
