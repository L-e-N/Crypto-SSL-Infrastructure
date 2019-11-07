import datetime
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding

class Certificat:

    def __init__(self, pem=None):
        if pem:
            self.x509 = x509.load_pem_x509_certificate(pem, default_backend())
        else:
            self.x509 = None
    
    def create_cert(self, client_name, server_name, pub_key, pri_key, validity_days=10):

        if client_name == server_name : #autocertify
            subject = issuer = x509.Name([
                x509.NameAttribute(NameOID.COMMON_NAME, server_name)
            ])
        else :
            subject = x509.Name([
                x509.NameAttribute(NameOID.COMMON_NAME, client_name)
            ])
            issuer = x509.Name([
                x509.NameAttribute(NameOID.COMMON_NAME, server_name)
            ])
        self.x509 = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            pub_key
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.datetime.utcnow()
        ).not_valid_after(  # Our certificate will be valid for 10 days
            datetime.datetime.utcnow() + datetime.timedelta(days=validity_days)
        ).add_extension(
            x509.SubjectAlternativeName([x509.DNSName(u"localhost")]),
            critical=False,
            # Sign our certificate with our private key
        ).sign(pri_key, hashes.SHA256(), default_backend())


    def verif_certif(self, pub_key):
        try:
            pub_key.verify(
                self.x509.signature,
                self.x509.tbs_certificate_bytes,
                padding.PKCS1v15(),
                self.x509.signature_hash_algorithm,
            )
            return True
        except ValueError:
            return False
