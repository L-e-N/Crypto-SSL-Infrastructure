from PaireClesRSA import PaireClesRSA
from Equipement import *
from create_socket import *
from cli import *
from Certificat import Certificat


def main():

    # List of equipments in the network
    network = []

    # Already create an equipement for test
    new_equipment = Equipment("Dang", 12500)
    network.append(new_equipment)

    # User input to do a command
    command = ""
    while command != "end":

        command = cli_command(network)
        print(command)
        if command == 'create equipment':
            new_equipment = cli_create_equipment()
            network.append(new_equipment)
            print('New equipement created')

        elif command == 'show network':
            print(network)

            # à ajouter dans la classe Equipement
            """def __str__(self):
                return "(ID: %s, port: %d)" % (self.name, self.port)

            def __repr__(self):
                return self.__str__()"""

        elif command == 'show detail':
            selected_equipment = cli_select_equipment(network)
            print(selected_equipment)
            print(selected_equipment.name)
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
main()
