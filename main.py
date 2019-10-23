from cryptography.hazmat.primitives import serialization

from PaireClesRSA import PaireClesRSA
from Equipement import *
from Certificat import Certificat


def create_equipment():
    print('Please enter equipment name : ')
    name = input()
    equipment = Equipment(name)
    equipment.mycert().verif_certif(equipment.mypubkey())
    print(equipment.mycert())
    return equipment


def test():
    e = Equipment('myequipment', 80)
    e.affichage()
    print(e.mycert.verif_certif(e.mykey.public()))


test()