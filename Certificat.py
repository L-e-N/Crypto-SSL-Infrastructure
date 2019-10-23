from PaireClesRSA import *
from Equipement import Equipment

class Certificat():

    def __init__(self, name, keypair, validity_days):

        # auto certify
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, name),
        ])
        self.x509 = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            keypair.public()
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
        ).sign(keypair.private(), hashes.SHA256())

        print(cert.public_bytes(serialization.Encoding.PEM))

    def verif_certif(self, pubkey):
        try:
            pubkey.verify(
                self.cert.signature,
                self.cert.tbs_certificate_bytes,
                padding.PKCS1v15(),
                cert_to_check.signature_hash_algorithm,
            )
            return True
        except ValueError:
            return False


p = PaireClesRSA()