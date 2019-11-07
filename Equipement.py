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
        self.cert.create_cert(self.name, self.name, self.keypair.public(), self.keypair.private(), self.validity_days)

        ''' When we create an equipment, we start a thread that opens a server socket to listen to others '''
        self.thread_server = threading.Thread(target=open_socket_server, args=(self, 'localhost'))
        self.thread_server.start()
        self.ca = {}
        self.da = {}

    def __str__(self):
            return "(ID: %s, port: %d)" % (self.name, self.port)

    def __repr__(self):
            return self.__str__()

    def affichage_da(self):
        print("Printing the DA of ", self.name, " : ", self.da)

    def affichage_ca(self):
        print("Printing the CA of ", self.name, " : ", self.ca)

    def affichage(self):
        print("Equipment name: ", self.name, "Equipment port :", self.port)
        print(self.cert.x509.public_bytes(serialization.Encoding.PEM))

    def name(self):
        return self.name

    def pub_key(self):
        return self.keypair.public()

    def cert(self):
        return self.cert

    def certify(self, pub_key, client_name):
        cert = Certificat()
        cert.create_cert(self.name, client_name, pub_key, self.keypair.private(), 10)
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
            self.ca[certifying_equipment_name][certified_equipment_name] = cert
        # else, create a new key for the equipment containing a dictionary with the certified equipment
        else:
            self.ca[certifying_equipment_name] = {certified_equipment_name: cert}

    def synchronize_da(self, ca, da, verbose=False):
        if verbose :
            print("SYNCHRONIZE DA OF ", self.name)
            print(self.ca)
            print(self.da)
            print(ca)
            print(da)
        # add the (keys,values) from da and ca that are NOT in self.da
        #self.da = dict(dict(dict(da, **ca), **self.ca), **self.da)
        self.da = dict(self.ca, **self.da)
        self.da = dict(ca, **self.da)
        self.da = dict(da, **self.da)

        #for sda in self.da:
        #    # for each key of self.DA, add all the (key,value) of equipment.CA[key] and DA[key] that are not in self.DA[key]
        #    self.da[sda] = dict(dict(da.get(sda, {}), **ca.get(sda, {})), **self.da[sda])
        if verbose:
            print(self.da)




def find_chain(start, end, d):
    current_node = d.get(start)
    path = [start]
    cert_chain = []
    while not current_node.get(end, False):
        next = list(current_node.keys())[0]
        path.append(next)
        cert_chain.append(current_node[next])
        current_node = d.get(next)
    next = list(current_node.keys())[0] #note : this value should be equal to end
    path.append(next)
    cert_chain.append(current_node[next])
    return path, cert_chain

def verify_chain(start_pub_key, cert_chain):
    for x in cert_chain :
        try : 
            if x.verif_certif(start_pub_key):
                start_pub_key = x.x509.public_key()
        except : 
            print("Chain certification error, breaking")
            return False
    print("The chain has been verified")
    return True


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
