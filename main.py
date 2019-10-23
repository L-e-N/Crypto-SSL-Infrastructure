from PaireClesRSA import *
import Equipement
import Certificat


def create_equipment():
    print('Please enter equipment name : ')
    name = input()
    equipment = Equipment(name)
    equipment.mycert().verif_certif(equipment.mypubkey())
    print(equipment.mycert())
    return equipment


def test():
    pk1 = PaireClesRSA()
    pk2 = PaireClesRSA()
    return (pk1, pk2)


