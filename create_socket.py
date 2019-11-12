import pickle
import socket
import threading
import time

from cli import cli_validate

from Certificat import Certificat
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import load_pem_public_key

'''
Remarques:
- Lors de l'instruction socket.accept(), le thread se bloque jusqu'à ce qu'il recoive une connection
- Pas besoin de ping pong send/receive, on peut send plusieurs fois de suite et receive plusieurs fois de suite
=> Non enfait problem parce manque de place d'input EOF?
- Echanger des string en convertissant en bytecode avec String.encode()/decode()
- Echanger les certificats et clé en pem
'''


def open_socket_server(equipment_server, hote):
    server_name = equipment_server.name

    # Création du socket serveur lié à son port et ouverture à la connexion
    socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_server.bind((hote, equipment_server.port))
    socket_server.listen(5) # 5 The backlog argument specifies the maximum number of queued connections

    print("%s écoute à présent sur le port %s" % (server_name, equipment_server.port))

    mode_recu = ""
    while mode_recu != "end":
        # Attente de connexion du socket serveur
        print("%s est en attente de connexion" % server_name)
        socket_client, infos_connexion = socket_server.accept()

        # 0: Reception d'une connexion et d'un mode de fonctionnement
        mode_recu = socket_client.recv(1024).decode()
        print("%s a reçu une connexion avec le mode [%s]" % (server_name, mode_recu))

        # Début du fonctionnement du serveur pour une insertion d'équipement
        if mode_recu.startswith("Certificate exchange"):
            client_name = mode_recu.split()[-1]

            validation = cli_validate("%s: Do you want to add %s?" % (server_name, client_name))
            if validation:
                # 1: Envoi du nom du serveur
                socket_client.send(server_name.encode())

                # 2: Reception bateau
                socket_client.recv(1024)

                # 3: Envoi de la clé publique du serveur
                socket_client.send(serialize_key_to_pem(equipment_server.pub_key()))

                # 4: Reception du certificat du client sur la clé du serveur
                recv_pem_cert = socket_client.recv(1024)  # Reception en format pem
                recv_cert = Certificat(recv_pem_cert)  # Conversion du certificat de pem à l'object Certificat

                # 5: Envoi bateau
                socket_client.send("Received cert".encode())

                # 6: Reception de la clé publique du client
                client_pub_key = socket_client.recv(1024) # Reception en format pem
                client_pub_key = load_pem_public_key(client_pub_key, backend=default_backend())  # Conversion de la clé publique de pem à pub key

                # Vérification du certificat reçu avec la clé publique du client
                if not recv_cert.verif_certif(client_pub_key): print("Could not verify certificate received by ", server_name)
                else:
                    # Mise à jour du CA du serveur
                    equipment_server.add_ca(client_name, server_name, recv_cert, client_pub_key)

                # 7: Envoi du certificat du serveur sur la clé du client
                sent_cert = equipment_server.certify(client_pub_key, client_name)
                socket_client.send(serialize_cert_to_pem(sent_cert))

                # 8: Envoi du CA du serveur au client
                socket_client.send(pickle.dumps(dictionary_to_pem_dictionary(equipment_server.ca)))

                # 9: Réception bateau
                msg = socket_client.recv(1024).decode()

                # 10: Envoi du DA du serveur au client
                socket_client.send(pickle.dumps(dictionary_to_pem_dictionary(equipment_server.da)))

                # 11: Reception du CA
                CA = pickle.loads(socket_client.recv(16384))
                CA = pem_dictionary_to_dictionary(CA)

                # 12: Envoi bateau
                socket_client.send("CA client received".encode())

                # 13: Réception du DA
                DA = pickle.loads(socket_client.recv(16384))
                DA = pem_dictionary_to_dictionary(DA)

                # Synchronisation du DA
                equipment_server.synchronize_da(CA, DA, verbose = False)
            
            socket_client.close()

    print("Fermeture de la connexion server de l'équipement: %s" % server_name)
    socket_server.close()


def open_socket_client(equipment_client, hote, equipment_server):
    client_name = equipment_client.name
    server_name = equipment_server.name

    validation = cli_validate("%s: Do you want to connect to %s?" % (client_name, server_name))

    if not validation:
        return

    # Connexion du socket client avec le socket du serveur par son port
    socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_client.connect((hote, equipment_server.port))
    print("Connexion de %s avec %s" % (client_name, server_name))

    # 0: Envoi du mode de fonctionnement au serveur
    mode = "Certificate exchange request from " + equipment_client.name
    mode = mode.encode()
    socket_client.send(mode)

    # 1: Réception du nom du serveur
    server_name = socket_client.recv(4096).decode()

    # 2: Envoi bateau
    msg = "Establishing connection between " + client_name + " and " + server_name
    socket_client.send(msg.encode())

    # 3: Réception de la clé du serveur
    server_pub_key = socket_client.recv(1024)
    server_pub_key = load_pem_public_key(server_pub_key, backend=default_backend())

    # 4: Envoi du certificat du client sur la clé du serveur
    cert = equipment_client.certify(server_pub_key, server_name)
    socket_client.send(serialize_cert_to_pem(cert))

    # 5: Réception bateau
    socket_client.recv(1024)

    # 6: Envoi de la clé publique du client
    socket_client.send(serialize_key_to_pem(equipment_client.pub_key()))

    # 7: Reception du certificat du serveur sur la clé du client
    recv_pem_cert = socket_client.recv(1024)
    recv_cert = Certificat(recv_pem_cert)

    # Vérification du certificat
    if not recv_cert.verif_certif(server_pub_key): print("Could not verify certificate received by ", client_name)
    else:
        # Mise à jour du CA du client
        equipment_client.add_ca(server_name, equipment_client.name, recv_cert, server_pub_key)

    # 8: Reception du CA du serveur
    CA = pickle.loads(socket_client.recv(16384))
    CA = pem_dictionary_to_dictionary(CA)

    # 9: Envoi bateau
    socket_client.send("CA server received".encode())

    # 10: Réception du DA du serveur
    DA = pickle.loads(socket_client.recv(16384))
    DA = pem_dictionary_to_dictionary(DA)

    # Synchronisation du DA du client avec le CA et DA du serveur
    equipment_client.synchronize_da(CA, DA, verbose = False)

    # 11: Envoi du CA
    socket_client.send(pickle.dumps(dictionary_to_pem_dictionary(equipment_client.ca)))

    # 12: Réception bateau
    msg = socket_client.recv(1024).decode()

    # 13: Envoi du DA 
    socket_client.send(pickle.dumps(dictionary_to_pem_dictionary(equipment_client.da)))

    print("Fermeture de la connexion entre %s et %s" % (client_name, server_name))
    socket_client.close()


# Open a socket connection and connect to an equipement server to close it
def open_close_socket_client(hote, equipment_server):
    socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_client.connect((hote, equipment_server.port))
    msg = "end".encode()
    socket_client.send(msg)
    socket_client.close()


def serialize_key_to_pem(object):
    # msg = msg.encode() does not work for public keys
    try:
        pem = object.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo)
    except ValueError:
        print("The key could not be converted to PEM")
    return pem

def pem_dictionary_to_dictionary(d):
    d_out = {}
    for k1, v1 in d.items():
        v = {} # inner dictionary
        for k2, v2 in v1.items():
            v[k2] = Certificat(v2)
        d_out[k1] = v
    return d_out

def dictionary_to_pem_dictionary(d):
    d_out = {}
    for k1, v1 in d.items():
        v = {}# inner dictionary
        for k2, v2 in v1.items():
            v[k2] = serialize_cert_to_pem(v2)
        d_out[k1] = v
    return d_out

def serialize_cert_to_pem(object):
    # msg = msg.encode() does not work for public keys
    try:
        pem = object.x509.public_bytes(serialization.Encoding.PEM)
    except ValueError:
        print("The cert could not be converted to PEM")
    return pem


def recv_pub_key(socket_client):
    msg_recu = socket_client.recv(1024)
    msg_recu = load_pem_public_key(msg_recu, backend=default_backend())
    return msg_recu


def confirm(stra, strb):
    answer = ""
    while answer not in ["y", "n"]:
        print("Connect equipment", stra, " to new equipment", strb)
        answer = input("[Y/N]? ").lower()
    return answer == "y"



