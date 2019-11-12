import pickle
import socket

from cli import cli_validate
from utils import *

from Certificat import Certificat
from cryptography.hazmat.backends import default_backend

from cryptography.hazmat.primitives.serialization import load_pem_public_key


'''
Remarques:
- Lors de l'instruction socket.accept(), le thread se bloque jusqu'à ce qu'il recoive une connection
- Pas besoin de ping pong send/receive, on peut send plusieurs fois de suite et receive plusieurs fois de suite
=> Non enfait problem parce manque de place d'input EOF?
- Echanger des string en convertissant en bytecode avec String.encode()/decode()
- Echanger les certificats et clé en pem
'''


# SERVEUR: Fonction pour ouvrir le socket du serveur afin de répondre aux clients qui se connectent selon le mode reçu
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
        client_name = mode_recu.split()[-1]
        print("%s a reçu une connexion avec le mode [%s]" % (server_name, mode_recu))

        # Début du fonctionnement du serveur pour une insertion d'équipement
        if mode_recu.startswith("Certificate exchange"):

            validation = cli_validate("%s: Do you want to add %s?" % (server_name, client_name))
            # 1: Envoi de la confirmation pour continuer ou de la fin de connexion si non validation
            if not validation:
                print("%s do not want to add %s, End of the connection" % (server_name, client_name))
                socket_client.send("end".encode())
                socket_client.close()
                continue
            else:
                socket_client.send("continue".encode())

            # ETAPE: Echange des clefs et des certificats
            if not echange_cle_cert_server(socket_client, equipment_server, server_name, client_name):
                continue

            # ETAPE: Synchronisation des DA
            sync_da_server(socket_client, equipment_server)

            print("%s: Insertion de %s réussie" % (server_name, client_name))

        if mode_recu.startswith("Chain proof"):
            # TODO: Vérification de la chaine de certificat reçu avant d'échanger les clés, les certifs et mettre à jour les DA

            # ETAPE: Echange des clefs et des certificats
            if not echange_cle_cert_server(socket_client, equipment_server, server_name, client_name):
                continue

            # ETAPE: Synchronisation des DA
            sync_da_server(socket_client, equipment_server)

            print("%s: Synchronisation avec %s réussie" % (server_name, client_name))

        print("%s: Fermeture de la connexion entre %s et %s" % (server_name, client_name, server_name))
        socket_client.close()

    print("Fermeture de la connexion server de l'équipement :%s" % server_name)
    socket_server.close()

# COMPORTEMENTS: Comportement du serveur et du client lors d'étape récurrentes dans différents modes de fonctionnement
# Comportement du serveur lors de l'échange de clé et de certificat
def echange_cle_cert_server(socket_client, equipment_server, server_name, client_name):
    # ETAPE: Echange des clés
    # 2: Envoi de la clé publique du serveur
    socket_client.send(serialize_key_to_pem(equipment_server.pub_key()))

    # 3: Reception de la clé publique du client
    client_pub_key = socket_client.recv(1024)  # Reception en format pem
    client_pub_key = load_pem_public_key(client_pub_key,
                                         backend=default_backend())  # Conversion de la clé publique de pem à pub key

    # ETAPE: Echange des certificats
    # 4: Reception du certificat du client sur la clé du serveur
    recv_pem_cert = socket_client.recv(1024)  # Reception en format pem
    recv_cert = Certificat(recv_pem_cert)  # Conversion du certificat de pem à l'object Certificat

    # 5: Envoi du résultat de la vérification du certificat reçu
    if not recv_cert.verif_certif(client_pub_key):
        print("Could not verify certificate received by ", server_name)
        socket_client.send("Certificate not verified".encode())
        socket_client.close()
        return False
    else:
        socket_client.send("Certificate verified".encode())
        # Mise à jour du CA du serveur
        equipment_server.add_ca(recv_cert)

    # 6: Envoi du certificat du serveur sur la clé du client
    sent_cert = equipment_server.certify(client_pub_key, client_name)
    socket_client.send(serialize_cert_to_pem(sent_cert))

    # 7: Reception de la vérification du certificat envoyé
    verification = socket_client.recv(1024).decode()
    if not verification == "Certificate verified":
        socket_client.close()
        return False

    return True


# Comportement du client lors de l'échange de clé et de certificat
def echange_cle_cert_client(socket_client, equipment_client, client_name, server_name):
    # ETAPE: Echange des clés
    # 2: Réception de la clé publique du serveur
    server_pub_key = socket_client.recv(1024)
    server_pub_key = load_pem_public_key(server_pub_key, backend=default_backend())

    # 3: Envoi de la clé publique du client
    socket_client.send(serialize_key_to_pem(equipment_client.pub_key()))

    # ETAPE: Echange des certificats
    # 4: Envoi du certificat du client sur la clé du serveur
    cert = equipment_client.certify(server_pub_key, server_name)
    socket_client.send(serialize_cert_to_pem(cert))

    # 5: Reception de la vérification du certificat envoyé
    verification = socket_client.recv(1024).decode()
    if not verification == "Certificate verified":
        socket_client.close()
        return False

    # 6: Reception du certificat du serveur sur la clé du client
    recv_pem_cert = socket_client.recv(1024)
    recv_cert = Certificat(recv_pem_cert)

    # 7: Envoie de la vérification du certificat
    if not recv_cert.verif_certif(server_pub_key):
        print("Could not verify certificate received by ", client_name)
        socket_client.send("Certificate not verified".encode())
        socket_client.close()
        return False
    else:
        socket_client.send("Certificate verified".encode())
        # Ajout du certificat dans du serveur dans le CA du client
        equipment_client.add_ca(recv_cert)

    return True


# Comportement du serveur lors de la synchronisation des DA
def sync_da_server(socket_client, equipment_server):
    # ETAPE: Synchronisation des DA
    # 8: Envoi du CA du serveur au client
    socket_client.send(pickle.dumps(dictionary_to_pem_dictionary(equipment_server.ca)))

    # 9: Réception bateau
    msg = socket_client.recv(1024).decode(),

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
    equipment_server.synchronize_da(CA, DA, verbose=False)


# Comportement du client lors de la synchronisation des DA
def sync_da_client(socket_client, equipment_client):
    # ETAPE: Synchronisation des DA
    # 8: Reception du CA du serveur
    CA = pickle.loads(socket_client.recv(16384))
    CA = pem_dictionary_to_dictionary(CA)

    # 9: Envoi bateau
    socket_client.send("CA server received".encode())

    # 10: Réception du DA du serveur
    DA = pickle.loads(socket_client.recv(16384))
    DA = pem_dictionary_to_dictionary(DA)

    # Synchronisation du DA du client avec le CA et DA du serveur
    equipment_client.synchronize_da(CA, DA, verbose=False)

    # 11: Envoi du CA
    socket_client.send(pickle.dumps(dictionary_to_pem_dictionary(equipment_client.ca)))

    # 12: Réception bateau
    msg = socket_client.recv(1024).decode()

    # 13: Envoi du DA
    socket_client.send(pickle.dumps(dictionary_to_pem_dictionary(equipment_client.da)))


# CLIENT: Function pour l'ouverture de socket client afin d'effectuer une interaction avec le serveur pour un certain mode
def open_socket_client(equipment_client, hote, equipment_server):
    client_name = equipment_client.name
    server_name = equipment_server.name

    validation = cli_validate("%s: Do you want to connect to %s?" % (client_name, server_name))
    if not validation:
        print("%s do not want to add %s, End of the connection" % (client_name, server_name))
        return

    # Connexion du socket client avec le socket du serveur par son port
    socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_client.connect((hote, equipment_server.port))
    print("Connexion de %s avec %s" % (client_name, server_name))

    # 0: Envoi du mode de fonctionnement au serveur
    mode = "Certificate exchange request from " + equipment_client.name
    mode = mode.encode()
    socket_client.send(mode)

    # 1: Réception du nom de la réponse du serveur pour continuer le process
    server_validation = socket_client.recv(4096).decode()
    if server_validation == "end":
        socket_client.close()
        return

    # Echange des clefs et des certificats
    if not echange_cle_cert_client(socket_client, equipment_client, client_name, server_name):
        return

    # Synchronisation des DA
    sync_da_client(socket_client, equipment_client)

    print("%s: Insertion dans le réseau de %s réussie" % (client_name, server_name))
    print("%s: Fermeture de la connexion entre %s et %s" % (client_name, client_name, server_name))
    socket_client.close()


def synchronize_socket_client(equipment_client, hote, equipment_server):
    client_name = equipment_client.name
    server_name = equipment_server.name
    try:
        print("Searching chain from ", server_name, " to ", equipment_client.name, " in ", equipment_client.da)
        path, cert_chain = find_chain(server_name, equipment_client.name, equipment_client.da)
    except ValueError:
        print('Error in find_chain from ', equipment_client.name, ' to ', server_name)
    if cert_chain == [] or not cert_chain:
        print("Pas de chaine, fermeture de la connexion entre %s et %s" % (client_name, server_name))
    else:
        cert_chain = [serialize_cert_to_pem(cert) for cert in cert_chain]

        # Connexion du socket client avec le socket du serveur par son port
        socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_client.connect((hote, equipment_server.port))
        print("Connexion de %s avec %s" % (client_name, server_name))

        # 0: Envoi du mode de fonctionnement au serveur
        mode = "Chain proof from " + equipment_client.name
        mode = mode.encode()
        socket_client.send(mode)

        # 1: Réception du nom du serveur
        server_name = socket_client.recv(4096).decode()
        # 2: Envoi de la chaine de certificat
        print('Cert chain :', cert_chain)
        socket_client.send(pickle.dumps(cert_chain))

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
            equipment_client.add_ca(recv_cert)

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


def find_chain(start, end, d):
    if start == end:
        print("Error, start == end")
        return False, False
    current_node = d.get(start)
    if not current_node:
        print("Error in find_chain: could not find start ", start, "in ", d)
        return False, False
    path = [start]
    cert_chain = []
    while not current_node.get(end, False):
        _next = list(current_node.keys())[0]
        if _next in path:
            print("Error in find_chain: cycle detection on ", _next, "in ", d)
            return False, False
        path.append(_next)
        cert_chain.append(current_node[_next])
        current_node = d.get(_next)
    _next = list(current_node.keys())[0]  # note : this value should be equal to end
    path.append(_next)
    cert_chain.append(current_node[_next])
    return path, cert_chain

def verify_chain(start_pub_key, cert_chain):
    for x in cert_chain:
        try:
            if x.verif_certif(start_pub_key):
                start_pub_key = x.x509.public_key()
        except:
            print("Chain certification error, breaking")
            return False
    #print("The chain has been verified")
    return True


