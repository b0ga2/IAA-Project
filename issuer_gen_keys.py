from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

# generate private key
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048
)

# generate public key
public_key = private_key.public_key()

# serialize private key
private_pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)

# serialize public key
public_pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo,
)

private_key_file = open("issuer-private.pem", "w")
private_key_file.write(private_pem.decode())
private_key_file.close()

public_key_file = open("issuer-public.pub", "w")
public_key_file.write(public_pem.decode())
public_key_file.close()
