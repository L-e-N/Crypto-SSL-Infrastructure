import socket


def socket_serveur(hote, port):
    connexion_principale = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connexion_principale.bind((hote, port))
    connexion_principale.listen(5)

    print("Le serveur écoute à présent sur le port {}".format(port))

    connexion_avec_client, infos_connexion = connexion_principale.accept()
    msg_recu = b""
    while msg_recu != b"fin":
        msg_recu = connexion_avec_client.recv(1024)
        # L'instruction ci-dessous peut lever une exception si le message

        # Réceptionné comporte des accents
        print(msg_recu.decode())
        connexion_avec_client.send(b"5 / 5")
    print("Fermeture de la connexion")
    connexion_avec_client.close()
    connexion_principale.close()


def socket_client(hote, port):
    connexion_avec_serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connexion_avec_serveur.connect((hote, port))
    print("Connexion établie avec le serveur sur le port {}".format(port))
    msg_a_envoyer = b""
    while msg_a_envoyer != b"fin":
        msg_a_envoyer = input("> ")
        # Peut planter si vous tapez des caractères spéciaux
        msg_a_envoyer = msg_a_envoyer.encode() # encore un str en byte
        # On envoie le message
        connexion_avec_serveur.send(msg_a_envoyer)
        msg_recu = connexion_avec_serveur.recv(1024)
        print(msg_recu.decode())  # Là encore, peut planter s'il y a des accents

    print("Fermeture de la connexion")
    connexion_avec_serveur.close()