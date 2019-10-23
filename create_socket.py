import socket
import threading
import time


""" TODO: Add different behaviour according to what the server receive """
def open_socket_server(equipment, hote, port):
    socker_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socker_server.bind((hote, port))
    socker_server.listen(5)

    print("Le serveur écoute à présent sur le port {}".format(port))

    socket_client, infos_connexion = socker_server.accept()
    '''
    msg_recu = b""
    while msg_recu != b"fin":
        msg_recu = socket_client.recv(1024)
        print(msg_recu.decode())
        socket_client.send(b"5 / 5")
    print("Fermeture de la connexion")
    '''
    echange_certificat_server(socket_client)
    print("Fermeture de la connexion server de l'équipement: %s" % equipment.myname)
    socket_client.close()
    socker_server.close()


def open_socket_client(equipment, hote, port):
    socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_client.connect((hote, port))
    print("Connexion établie avec le serveur sur le port {}".format(port))

    '''msg_a_envoyer = b""
    while msg_a_envoyer != b"fin":
        msg_a_envoyer = input("> ")
        msg_a_envoyer = msg_a_envoyer.encode() # encore un str en byte
        socket_client.send(msg_a_envoyer)
        msg_recu = socket_client.recv(1024)
        print(msg_recu.decode())  # Là encore, peut planter s'il y a des accents
    '''
    echange_certificat_client(socket_client)
    print("Fermeture de la connexion client")
    socket_client.close()


def echange_certificat_client(socket_client):
    msg = "Salut"
    msg = msg.encode()
    socket_client.send(msg)

    # Convert certificate to bytecode to be able to send it! (socket.send())


def echange_certificat_server(socket_client):
    msg_recu = socket_client.recv(1024)
    msg_recu = msg_recu.decode()
    print(('Mesage reçu: %s' % msg_recu))

def thread_func(name):
    print("Thread %s: Hello" % name)
    time.sleep(2)
    print("Thread %s: Close this thread" % name)


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
