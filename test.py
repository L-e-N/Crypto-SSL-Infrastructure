from random import randint

from cryptography.hazmat.primitives import serialization

from PaireClesRSA import PaireClesRSA
from Equipement import *
from create_socket import *
from Certificat import Certificat
#from PyInquirer import prompt


def test2():
    _port = randint(10000, 12500)
    A = Equipment('A', _port)
    B = Equipment('B', _port + 1)
    C = Equipment('C', _port + 2)
    A.connect_to_equipment(B)

def test():
    _port = randint(10000,12500)
    A = Equipment('A', _port)
    B = Equipment('B', _port+1)
    C = Equipment('C', _port + 2)

    A.connect_to_equipment(B)
    time.sleep(1)
    print("")
    print("CONNECTING C TO B")
    #sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #print(sock.connect_ex(('localhost', _port+1)) == 0) #le port s'est ferme
    C.connect_to_equipment(B)

    print(A.ca)
    print(B.ca)
    print(C.ca)
    print(A.da)
    print(B.da)
    print(C.da)
    cert = B.da['B']['C']
    certB=B.cert
    print(certB.x509.signature_hash_algorithm)
    keyA = A.pub_key()
    path, cert_chain = find_chain('A','C',B.da)
    print(cert_chain[0].x509.signature_hash_algorithm) # identical
    key = cert_chain[0].x509.public_key()

    print(certB.verif_certif(B.pub_key()))

    start_key = A.pub_key()
    verify_chain(start_key, cert_chain)
    print(cert.x509.issuer.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value)



"""
Problèmes:
- port 80 non autorisé dont j'ai utilisé 12500
- lasiser au socket server le temps de s'ouvrir avant de se connecter (time.sleep) 
- Attention à bien finir le socket server sinon quand on relance c'est déjà pris (clic sur carré rouge)
"""
test2()

