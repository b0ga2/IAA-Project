import sqlite3, requests, sys, json

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric.utils import Prehashed
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_pem_private_key

def get_vc(holder_vc, data):
    # Sends the name and nationality
    r = requests.post("http://127.0.0.1:1337/register_holder", json=data)

    vc = r.json()
    print("Your pin is:" , r.json()['holder_pin'])
    vc["vc_json"].pop("holder_pin", None)

    with open(holder_vc, "w", encoding="utf-8") as f:
        json.dump(vc, f, indent=4, ensure_ascii=False)

    return vc

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f"Wrong arguments!\n\tUsage: {sys.argv[0]} <holder id>")
        exit(1)

    holder_id = sys.argv[1]
    holder_vc = f"holder_{holder_id}.json"

    vc = get_vc(holder_vc, {'full_name': 'TÓS',"nationality":"Out of this World", "holder_id": holder_id, "health_code": "teste"})
    r = requests.post("http://127.0.0.1:1733/auth_req", json={"did_identifier": vc["vc_json"]["did_identifier"]})

    challenge = r.json()["challenge"]
    LoA = r.json()["loa"]

    # Hash of the challenge
    digest = hashes.Hash(hashes.SHA256())
    digest.update(challenge.encode('utf-8'))
    hashed_challenge = digest.finalize()

    while True:
        # Substantial level means the PIN is required
        try:
            if LoA == "substantial":
                # Obtains the PIN
                pin = input("Enter your PIN: ")

                holder_private_key = load_pem_private_key(
                    vc["vc_json"]["private_pem_substantial_loa"].encode("utf-8"),
                    password=pin.encode('utf-8'),
                    backend=default_backend()
                )
            # Low means only presenting the card is enough
            elif LoA == "low":
                holder_private_key = load_pem_private_key(
                    vc["vc_json"]["private_pem_low_loa"].encode("utf-8"),
                    password=None,
                    backend=default_backend()
                )

            # Encrypt the hash of the challenge
            signature = holder_private_key.sign(
                data=hashed_challenge,
                padding=padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                algorithm=Prehashed(hashes.SHA256())
            )

            signature = [x for x in signature]
        except:
            signature = []

        # Send signature and holder_id to interface
        r = requests.post("http://127.0.0.1:1733/send_challenge_to_verifier", json={"vc": vc, "signature": signature})
        print(r.json())

        if LoA == "low" or r.json()["valid"] == "yes" or ("reason" in r.json() and r.json()["reason"] == "too many tries"):
            break
