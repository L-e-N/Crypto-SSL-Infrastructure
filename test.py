from random import randint

from cryptography.hazmat.primitives import serialization

from PaireClesRSA import PaireClesRSA
from Equipement import *
from create_socket import *
from Certificat import Certificat
from chain_utils import find_chain, verify_chain


def test2():
    _port = randint(10000, 12500)
    A = Equipment('A', _port)
    B = Equipment('B', _port + 1)
    C = Equipment('C', _port + 2)
    A.connect_to_equipment(B)

def test():
    _port = randint(10000,12500)
    Equipments = []
    A = Equipment('A', _port)
    B = Equipment('B', _port + 1)
    C = Equipment('C', _port + 2)
    D = Equipment('D', _port + 3)
    E = Equipment('E', _port + 4)
    Equipments = [A, B, C, D, E]
    A.connect_to_equipment(B)
    B.connect_to_equipment(C)
    C.connect_to_equipment(A)
    E.connect_to_equipment(D)
    D.connect_to_equipment(B)

    for x in Equipments:
        x.affichage_ca()
    for x in Equipments:
        x.affichage_da()

    print(find_chain('A', 'C', C.da))
    print(find_chain('A', 'C', C.da))
    print(find_chain('A', 'C', C.da))
    path, cert_chain = find_chain('A','C', C.da)
    print(verify_chain(A.pub_key(),cert_chain))

    C.synchronize_to_equipment(A)

    print(find_chain('C', 'D', D.da)[0])
    print(find_chain('D', 'C', C.da)[0])
    C.synchronize_to_equipment(D)
    D.synchronize_to_equipment(C)

    D.synchronize_to_equipment(C)

    C.synchronize_to_equipment(D)
    #key = cert_chain[0].x509.public_key()

    #print(certB.verif_certif(B.pub_key()))




"""
Problèmes:
- port 80 non autorisé dont j'ai utilisé 12500
- lasiser au socket server le temps de s'ouvrir avant de se connecter (time.sleep) 
- Attention à bien finir le socket server sinon quand on relance c'est déjà pris (clic sur carré rouge)
"""
test()

