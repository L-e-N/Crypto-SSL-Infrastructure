import threading
import time

from Equipement import Equipment
from create_socket import *
from cli import *


def main():

    # List of equipments in the network and graph to display it with nodes and edges
    network = []

    # Already create an equipement for test
    new_equipment = Equipment("Dang", 12513)
    network.append(new_equipment)
    new_equipment = Equipment("Dang2", 12512)
    network.append(new_equipment)

    # User input to do a command
    command = ""
    while command != "end":

        command = cli_command(network)
        print(command)
        if command == 'create equipment':
            equipement_id, port = cli_create_equipment()
            new_equipment = Equipment(equipement_id, port)
            network.append(new_equipment)
            print('New equipement %s was created' % equipement_id)

        elif command == 'show network':
            print(network)

        elif command == 'show detail':
            selected_equipment = cli_select_equipment(network, "Select the equipment to detail")
            selected_equipment.affichage_ca()
            selected_equipment.affichage_da()

        elif command == 'insert equipment':
            added_equipment, host_equipment = cli_select_two_equipments(network, "Select the equipement to insert", "Select the equipement to be added to")
            added_equipment.connect_to_equipment(host_equipment)

        elif command == 'sync equipment':
            syncing_equipment, synced_equipment = cli_select_two_equipments(network, "Select the equipement to to synchronize", "Select the equipement to be synchronized to")
            # TODO: replace the method with the new one to synchronize
            syncing_equipment.connect_to_equipment(synced_equipment)

        time.sleep(1)  # Sleep before the next command

    for equipment in network:
        # Fermer tous les sockets serveurs en ouvrant un connexion à eux et leur dire de fermer
        y = threading.Thread(target=open_close_socket_client, args=('localhost', equipment))
        y.start()
        y.join()


main()

"""
Problèmes:
- port 80 non autorisé dont j'ai utilisé 12500
- lasiser au socket server le temps de s'ouvrir avant de se connecter (time.sleep) 
- Attention à bien finir le socket server sinon quand on relance c'est déjà pris (clic sur carré rouge)
"""

