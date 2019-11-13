import threading

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
        s = '''
            ID: {name}, port: {port}
            {ca}
            {da}'''.format(name=self.name, port=self.port, ca=self.affichage_ca(), da=self.affichage_da())
        return s

    def __repr__(self):
        return self.__str__()

    def affichage_da(self):
        da = "["
        for key, value in self.da.items():
            # da.append(key)
            for key2, value2 in value.items():
                # da.append(key2)
                str = value2.x509.issuer.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value + "->" + \
                      value2.x509.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
                da += str + ", "
        da = da[:-2] + "]"
        s = "DA of {name}: {da}".format(name=self.name, da=da)
        return s

    def affichage_ca(self):
        ca = "["
        for key, value in self.ca.items():
            for key2 in value.keys():
                ca += key2 + ", "
        ca = ca[:-2] + "]"
        s = "CA of {name}: {ca}".format(name=self.name, ca=ca)
        return s

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
        y = threading.Thread(target=open_socket_client, args=(self, 'localhost', equipment))
        y.start()
        y.join()

    def synchronize_to_equipment(self, equipment):
        """ Start a thread that open a client socket connected to the server socket of another equipement """
        """ We should use different open_socket_client to have a different behaviour for what we want to ask to the other equipment (add, sync..) """
        y = threading.Thread(target=synchronize_socket_client, args=(self, 'localhost', equipment))
        y.start()
        y.join()

    def add_ca(self, cert):
        issuer = cert.x509.issuer.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
        subject = cert.x509.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
        # if CA already contains the equipment, simply add the certified equipment
        if self.ca.get(issuer, False):
            self.ca[issuer][subject] = cert
        # else, create a new key for the equipment containing a dictionary with the certified equipment
        else:
            self.ca[issuer] = {subject: cert}

    def add_da(self, cert):
        issuer = cert.x509.issuer.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
        subject = cert.x509.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
        # if CA already contains the equipment, simply add the certified equipment
        if self.da.get(issuer, False):
            self.da[issuer][subject] = cert
        # else, create a new key for the equipment containing a dictionary with the certified equipment
        else:
            self.da[issuer] = {subject: cert}

    def synchronize_da(self, ca, da, verbose=False):
        if verbose :
            print("SYNCHRONIZE DA OF ", self.name)
            print(self.ca)
            print(self.da)
            print(ca)
            print(da)
        # add the (keys,values) from da and ca that are NOT in self.da
        self.da = dict(dict(dict(da, **ca), **self.ca), **self.da)
        self.da = dict(self.ca, **self.da)
        self.da = dict(ca, **self.da)
        self.da = dict(da, **self.da)
        out = self.da
        for key, value in self.da.items():
            for dic in [self.ca, ca, da]:
                    value2 = dic.get(key, False)
                    if value2 :
                        for key2 in value2.keys():
                            out[key][key2] = value2[key2]
        self.da=out
        # for sda in self.da:
        #    # for each key of self.DA, add all the (key,value) of equipment.CA[key] and DA[key] that are not in self.DA[key]
        #    self.da[sda] = dict(dict(da.get(sda, {}), **ca.get(sda, {})), **self.da[sda])
        if verbose:
            print(self.da)





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
