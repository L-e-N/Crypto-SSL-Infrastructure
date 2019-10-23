from cryptography.hazmat.primitives import serialization

from PaireClesRSA import PaireClesRSA
from Equipement import *
from Certificat import Certificat


def test():
    e1 = Equipment('myequipment', 80)
    e1.affichage()
    e2 = Equipment('myequipment', 80)

    cert = e1.certify(e2)
    print(cert.x509.public_bytes(serialization.Encoding.PEM))

    v1 = cert.verif_certif(e1.mykey.public())
    v2 = cert.verif_certif(e2.mykey.public())
    print("Verification of cert by e1", v1)
    print("Verification of cert by e2", v2)

def test_socket():
    e1 = Equipment('a', 12500)
    e2 = Equipment('a', 12501)
    time.sleep(2)
    e2.connect_to_equipment(e1)


"""
Problèmes:
- port 80 non autorisé dont j'ai utilisé 12500
- lasiser au socket server le temps de s'ouvrir avant de se connecter (time.sleep) 
- Attention à bien finir le socket server sinon quand on relance c'est déjà pris (clic sur carré rouge)
"""
test_socket()
