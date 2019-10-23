from PaireClesRSA import PaireClesRSA
from Equipement import Equipment
from Certificat import Certificat


def create_equipment():
    print('Please enter equipment name : ')
    name = input()
    equipment = Equipment(name)
    equipment.mycert().verif_certif(equipment.mypubkey())
    print(equipment.mycert())
    return equipment


def test():
    pk = PaireClesRSA()
    print(pk)




print(test())