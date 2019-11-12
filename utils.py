from cryptography.hazmat.primitives import serialization

from Certificat import Certificat

''' List of functions to convert object to different formats '''


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
        v = {}  # inner dictionary
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