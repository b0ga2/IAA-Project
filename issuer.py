from datetime import datetime, date
from flask import Flask, request
import requests, sqlite3

import random, sys, json, base64
from random import randrange

from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key
from cryptography.hazmat.primitives.asymmetric.utils import Prehashed
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes

from datetime import datetime, timedelta

app = Flask(__name__)

def create_db():
    conn = sqlite3.connect("issuer.db")
    with open('issuer.sql') as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()

# Arrays with 10 sample values each
original_national_base_list = [
    "NAT-001", "NAT-002", "NAT-003", "NAT-004", "NAT-005",
    "NAT-006", "NAT-007", "NAT-008", "NAT-009", "NAT-010"
]

rank_list = [
    "Private", "Corporal", "Sergeant", "Lieutenant", "Captain",
    "Major", "Colonel", "General", "Warrant Officer", "Commander"
]

division_list = [
    "Infantry", "Artillery", "Engineering", "Signals", "Air Force",
    "Navy", "Medical", "Logistics", "Special Forces", "Cyber Defense"
]

security_clearance_level_list = [
    "Unclassified", "Restricted", "Confidential", "Secret", "Top Secret",
    "NATO Secret", "SCI", "Codeword", "Cosmic Top Secret", "Eyes Only"
]

def gen_key_pair_holder():
    # generate low LoA key pair
    private_key_low_loa = rsa.generate_private_key(public_exponent=65537,key_size=2048)
    public_key_low_loa = private_key_low_loa.public_key()

    # serialize key pair
    private_pem_low_loa = private_key_low_loa.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode("utf-8")
    public_pem_low_loa = public_key_low_loa.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode("utf-8")

    # generate substantial LoA key pair
    private_key_substantial_loa = rsa.generate_private_key(public_exponent=65537,key_size=2048)
    public_key_substantial_loa = private_key_substantial_loa.public_key()

    # serialize substantial LoA key pair with random 6 digit PIN
    holder_pin = f"{random.randint(0, 999999):06d}".encode("utf-8") 
    private_pem_substantial_loa = private_key_substantial_loa.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.BestAvailableEncryption(holder_pin),
    ).decode("utf-8")
    public_pem_substantial_loa = public_key_substantial_loa.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode("utf-8")

    return (private_pem_low_loa, public_pem_low_loa, private_pem_substantial_loa, public_pem_substantial_loa, holder_pin.decode("utf-8"))

@app.route("/register_holder", methods=["POST"]) 
def register_holder():
    user_data = request.get_json()

    # Generate key pair and PIN
    (private_pem_low_loa, 
     public_pem_low_loa, 
     private_pem_substantial_loa, 
     public_pem_substantial_loa, 
     holder_pin) = gen_key_pair_holder()

    # Sends the key pair to the blockchain and gets the DID identifier
    r = requests.get("http://127.0.0.1:3173/register_did", 
                      json={"public_pem_low_loa": public_pem_low_loa, "public_pem_substantial_loa": public_pem_substantial_loa})

    did_identifier = r.json()["did_identifier"]

    # Sends full data to the wallet
    idx = randrange(len(original_national_base_list))
    original_national_base = original_national_base_list[idx]
    rank = rank_list[idx]
    division = division_list[idx]
    security_clearance_level = security_clearance_level_list[idx]
    holder_id = user_data["holder_id"]
    initial_date = datetime.now()
    final_date = (initial_date + timedelta(days=365)).strftime('%Y/%d/%m')

    r = requests.post("http://127.0.0.1:7331/register_vc", json={
        "original_national_base": original_national_base,
        "rank": rank,
        "division": division,
        "health_code": user_data["health_code"],
        "nationality": user_data["nationality"],
        "full_name": user_data["full_name"],
        "security_clearance_level": security_clearance_level,
        "holder_id": holder_id,
        "initial_date": initial_date.strftime('%Y/%d/%m'),
        "final_date": final_date,
        "issuer_id": issuer_id,
        "did_identifier": did_identifier,
    })

    # load issuer private key from file
    with open("issuer-private.pem", "rb") as key_file:
        try:
            issuer_private_key = load_pem_private_key(
                key_file.read(),
                password=None,
                backend=default_backend()
            )
        except:
            print("Error reading private key")
            exit(1)

    # Returns the signed VCs to the holder
    vc_json = {
        "original_national_base": original_national_base,
        "rank": rank,
        "division": division,
        "health_code": user_data["health_code"],
        "nationality": user_data["nationality"],
        "full_name": user_data["full_name"],
        "security_clearance_level": security_clearance_level,
        "initial_date": str(initial_date.strftime('%Y/%d/%m')),
        "final_date": str(final_date),
        "issuer_id": issuer_id,
        "did_identifier": did_identifier,
        "private_pem_low_loa": private_pem_low_loa, 
        "public_pem_low_loa": public_pem_low_loa, 
        "private_pem_substantial_loa": private_pem_substantial_loa, 
        "public_pem_substantial_loa": public_pem_substantial_loa,
    }

    # hash the vc_json
    digest = hashes.Hash(hashes.SHA256())
    digest.update(json.dumps(vc_json, sort_keys=True).encode('utf-8'))
    hashed_vc = digest.finalize()

    # sign the vc_json
    signature = issuer_private_key.sign(
        data=hashed_vc,
        padding=padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        algorithm=Prehashed(hashes.SHA256())
    )

    return {"vc_json": vc_json, "holder_pin": holder_pin, "signature": base64.b64encode(signature).decode('utf-8')}

@app.post("/check_vc_validity")
def check_vc_valifity():
    vc = request.get_json()["vc"]

    with open("issuer-public.pub", "rb") as f:
        issuer_pub_key = load_pem_public_key(f.read())

    # Hash of the vc
    digest = hashes.Hash(hashes.SHA256())
    digest.update(json.dumps(vc, sort_keys=True).encode('utf-8'))
    hashed_vc = digest.finalize()

    # check if the vc is revoked
    conn = sqlite3.connect("issuer.db")
    cursor = conn.cursor()

    revoked = cursor.execute("SELECT motive FROM crls WHERE vc_hash=?", (base64.b64encode(hashed_vc),)).fetchone()

    # Commit and close
    conn.commit()
    conn.close()

    if revoked != None:
        print("VC is revoked.")
        return {"valid": "no"}

    # Hash of the vc json
    digest = hashes.Hash(hashes.SHA256())
    digest.update(json.dumps(vc["vc_json"], sort_keys=True).encode('utf-8'))
    hashed_vc = digest.finalize()

    # check the signature
    try:
        issuer_pub_key.verify(
            base64.b64decode(request.get_json()["vc"]["signature"]),
            hashed_vc,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            Prehashed(hashes.SHA256())
        )
    except Exception as inst:
        print("exception: ", inst)
        print(f"Signature is invalid.")
        return {"valid": "no"}
 
    # check the date validity
    today = date.today()
    initial_date = datetime.strptime(vc["vc_json"]["initial_date"], "%Y/%d/%m").date()
    final_date = datetime.strptime(vc["vc_json"]["final_date"], "%Y/%d/%m").date()

    if initial_date > today or final_date < today:
        return {"valid": "no"}

    return {"valid": "yes"}

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f"Wrong arguments!\n\tUsage: {sys.argv[0]} <issuer id>")
        exit(1)

    issuer_id = sys.argv[1]
    create_db()
    app.run(debug=True, port=1337)
