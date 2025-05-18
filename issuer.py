from flask import Flask
from flask import request
import requests

import random
import sys

from cryptography.hazmat.primitives.asymmetric import dsa
from cryptography.hazmat.primitives import serialization

from datetime import datetime, timedelta

app = Flask(__name__)


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

    #generate low LoA key pair
    private_key_low_loa = dsa.generate_private_key(key_size=2048)
    public_key_low_loa = private_key_low_loa.public_key()

    #serialize key pair
    private_pem_low_loa = private_key_low_loa.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode("utf-8")
    public_pem_low_loa = public_key_low_loa.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode("utf-8")

    #generate substantial LoA key pair
    private_key_substantial_loa = dsa.generate_private_key(key_size=2048)
    public_key_substantial_loa = private_key_substantial_loa.public_key()

    #serialize substantial LoA key pair with random 6 digit PIN
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

    return (private_pem_low_loa, public_pem_low_loa, private_pem_substantial_loa, public_pem_substantial_loa, holder_pin)

@app.route("/register_holder", methods=["POST"]) 
def get_vc():
    user_data = request.get_json()

    #Generate key pair and PIN
    (private_pem_low_loa, 
     public_pem_low_loa, 
     private_pem_substantial_loa, 
     public_pem_substantial_loa, 
     holder_pin) = gen_key_pair_holder()

    #Sends the key pair to the blockchain and gets the DID identifier
    r = requests.get("http://127.0.0.1:3173/register_did", 
                      json={"public_pem_low_loa": public_pem_low_loa,
                            "public_pem_substantial_loa": public_pem_substantial_loa})
    
    did_identifier = r.json()["did_identifier"]


    #Sends full data to the wallet   
    original_national_base = random.choice(original_national_base_list)
    rank = random.choice(rank_list)
    division = random.choice(division_list)
    security_clearance_level = random.choice(security_clearance_level_list)
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

    return did_identifier

if __name__ == '__main__':

    if len(sys.argv) < 2:
        print(f"Wrong arguments!\n\tUsage: {sys.argv[0]} <holder id>")
        exit(1)

    issuer_id = sys.argv[1]

    app.run(debug=True, port=1337)
