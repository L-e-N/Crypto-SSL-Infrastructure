import pickle
import socket
import threading
import time

from Certificat import Certificat
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import load_pem_public_key

""" TODO: Add different behaviour according to what the server receive """


def open_socket_server(equipment_server, hote):
    socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_server.bind((hote, equipment_server.port))
    socket_server.listen(5) # 5 The backlog argument specifies the maximum number of queued connections

    print("Le serveur écoute à présent sur le port {}".format(equipment_server.port))

    socket_client, infos_connexion = socket_server.accept()

    mode_recu = ""
    while mode_recu != "end":
        print("Attente d'un message")
        mode_recu = socket_client.recv(1024)
        mode_recu = mode_recu.decode()
        print("Mode reçu %s" % mode_recu)
        if mode_recu == "":
            print("Empty mode received by", equipment_server.name)
            time.sleep(1)
        if mode_recu.startswith("Certificate exchange"):
            client_name = mode_recu.split()[-1]
            #if not confirm(equipment_server.name, client_name): return "Not connecting equipments"

            socket_client.send(equipment_server.name.encode())
            # waiting for client to say that he received the name
            socket_client.recv(1024)
            # send key to client
            socket_client.send(serialize_key_to_pem(equipment_server.pub_key()))

            #recv_pub_key(socket_client)
            recv_pem_cert = socket_client.recv(1024)
            print("Received cert ", recv_pem_cert)
            recv_cert = Certificat(recv_pem_cert)

            socket_client.send("Received cert".encode())

            client_pub_key = socket_client.recv(1024)
            print("Received key ", client_pub_key)
            client_pub_key = load_pem_public_key(client_pub_key, backend=default_backend())

            if not recv_cert.verif_certif(client_pub_key): print("Could not verify certificate received by ", equipment_server.name)
            else:
                print("Certificate from client verified")
                equipment_server.add_ca(client_name, equipment_server.name, recv_cert, client_pub_key)
                #equipment_server.affichage_ca()

            sent_cert = equipment_server.certify(client_pub_key)
            socket_client.send(serialize_cert_to_pem(sent_cert))

            # sending CA to client
            socket_client.send(pickle.dumps(dictionary_to_pem_dictionary(equipment_server.ca)))

            # receive confirmation
            msg = socket_client.recv(1024).decode()
            print(msg)

            # sending DA to client
            socket_client.send(pickle.dumps(dictionary_to_pem_dictionary(equipment_server.da)))

    print("Fermeture de la connexion server de l'équipement: %s" % equipment_server.name)
    socket_client.close()

    # socket_server.close()


def open_socket_client(equipment_client, hote, equipment_server):
    #if not confirm(equipment_client.name, equipment_server.name): return "Not connecting equipments"
    socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_client.connect((hote, equipment_server.port))
    print("Connexion établie avec le serveur sur le port {}".format(equipment_server.port))
    mode = "Certificate exchange request from " + equipment_client.name
    mode = mode.encode()
    socket_client.send(mode)

    server_name = socket_client.recv(1024).decode()

    msg = "Establishing connection between " + equipment_client.name + " and " + server_name
    socket_client.send(msg.encode())

    server_pub_key = recv_pub_key(socket_client)
    cert = equipment_client.certify(server_pub_key)
    socket_client.send(serialize_cert_to_pem(cert))

    socket_client.recv(1024)

    socket_client.send(serialize_key_to_pem(equipment_client.pub_key()))

    recv_pem_cert = socket_client.recv(1024)
    recv_cert = Certificat(recv_pem_cert)
    if not recv_cert.verif_certif(server_pub_key): print("Could not verify certificate received by ", equipment_client.name)
    else:
        print("Certificate from server", server_name, " verified, updating CA")
        equipment_client.add_ca(server_name, equipment_client.name, recv_cert, server_pub_key)
        #equipment_client.affichage_ca()

    # receive CA in pem from the server to the client
    CA = pickle.loads(socket_client.recv(4096))
    CA = pem_dictionary_to_dictionary(CA)

    # send a message for to make the server send it's DA
    socket_client.send("CA server received".encode())

    #receive DA in pem
    DA = pickle.loads(socket_client.recv(4096))
    DA = pem_dictionary_to_dictionary(DA)

    equipment_client.synchronize_da(CA, DA, verbose = False)
    # socket_client.send(serialize_to_pem(equipment_client.pub_key()))
    print("Fermeture de la connexion client")
    socket_client.send("end".encode())
    socket_client.close()


# Open a socket connection to the listening server to close it
def open_close_socket_client(hote, equipment_server):
    socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_client.connect((hote, equipment_server.port))
    print("Connexion établie avec le serveur sur le port {}".format(equipment_server.port))
    msg = "end".encode()
    socket_client.send(msg)
    print("Fermeture de la connexion client")
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


# Convert certificate to bytecode to be able to send it! (socket.send())


def recv_pub_key(socket_client):
    msg_recu = socket_client.recv(1024)
    msg_recu = load_pem_public_key(msg_recu, backend=default_backend())
    print(('Mesage reçu: %s' % msg_recu))
    return msg_recu


def thread_func(name):
    print("Thread %s: Hello" % name)
    time.sleep(2)
    print("Thread %s: Close this thread" % name)


def confirm(stra, strb):
    answer = ""
    while answer not in ["y", "n"]:
        print("Connect equipment", stra, " to new equipment", strb)
        answer = input("[Y/N]? ").lower()
    return answer == "y"


def test():
    print("Main    : before creating thread")
    x = threading.Thread(target=open_socket_server, args=('equipement1', 12500))
    y = threading.Thread(target=open_socket_client, args=('equipement2', 12500))
    print("Main    : before running thread")
    x.start()
    y.start()
    print("Main    : wait for the thread to finish")
    x.join()
    y.join()
    print("Main    : all done")
