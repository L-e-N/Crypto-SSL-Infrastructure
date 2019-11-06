from cryptography.hazmat.primitives import serialization

from PaireClesRSA import PaireClesRSA
from Equipement import *
from create_socket import *
from Certificat import Certificat
#from PyInquirer import prompt


def test():
    _port = 11800
    A = Equipment('A', _port)
    B = Equipment('B', _port+1)
    C = Equipment('C', _port + 2)

    A.connect_to_equipment(B)
    time.sleep(1)
    print("")
    print("CONNECTING C TO B")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(sock.connect_ex(('localhost', _port+1)) == 0) #le port s'est ferme
    C.connect_to_equipment(B)

    print(A.ca)
    print(B.ca)
    print(C.ca)
    print(A.da)
    print(B.da)
    print(C.da)


def cli_create_equipment():
    questions = [
        {
            'type': 'input',
            'name': 'ID',
            'message': 'ID of the new equipment?'
        }
    ]
    answers = prompt(questions)
    print(answers)


def test_socket():

    # List of equipments in the network
    network = []

    # Already create an equipement for test
    new_equipment = Equipment("Dang", 12500)
    network.append(new_equipment)

    # HELP displaying the list of the available commands
    command_list = [
        'List of the available commands:'
        'create a new equipement: create equipment',
        'display the network: display network'
    ]
    for command in command_list:
        print(command)

    # User input to do a command
    command = ""
    while command != "end":
        print('Type a command:')
        command = input("> ")

        if command == "create equipment":
            print('Type the ID of the new equipement')
            id = input("> ")
            print('Type the port of the new equipement')
            port = input("> ")
            new_equipment = Equipment(id, int(port))
            network.append(new_equipment)
            print('New equipement created with id %s and port %s' % (id, port))

        elif command == "display network":
            print(network)

            # à ajouter dans la classe Equipement
            """def __str__(self):
                return "(ID: %s, port: %d)" % (self.name, self.port)

            def __repr__(self):
                return self.__str__()"""

    for equipment in network:
        # To close all listening sockets in equipement server thread, you can open a connection to these sockets and tell them to close.
        y = threading.Thread(target=open_close_socket_client, args=('localhost', equipment))
        y.start()
        y.join()

"""
Problèmes:
- port 80 non autorisé dont j'ai utilisé 12500
- lasiser au socket server le temps de s'ouvrir avant de se connecter (time.sleep) 
- Attention à bien finir le socket server sinon quand on relance c'est déjà pris (clic sur carré rouge)
"""
test()
