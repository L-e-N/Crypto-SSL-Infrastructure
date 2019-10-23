import datetime
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding

class Certificat:

    def __init__(self, name, pubkey, prikey, validity_days):
        # auto certify
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, name)
        ])
        self.x509 = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            pubkey
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
        ).sign(prikey, hashes.SHA256(), default_backend())

    def verif_certif(self, pubkey):
        try:
            pubkey.verify(
                self.x509.signature,
                self.x509.tbs_certificate_bytes,
                padding.PKCS1v15(),
                self.x509.signature_hash_algorithm,
            )
            return True
        except ValueError:
            return False
