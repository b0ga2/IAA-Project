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
    pin = r.json()['holder_pin']
    vc["vc_json"].pop("holder_pin", None)

    with open(holder_vc, "w", encoding="utf-8") as f:
        json.dump(vc, f, indent=4, ensure_ascii=False)

    return (vc, pin)

def solve_challenge(holder_vc):
    r = requests.post("http://127.0.0.1:1733/auth_req", json={"vc": holder_vc})

    if "valid" in r.json() and r.json()["valid"] == "no":
        return r.json()

    challenge = r.json()["challenge"]
    LoA = r.json()["loa"]

    # hash the challenge
    digest = hashes.Hash(hashes.SHA256())
    digest.update(challenge.encode('utf-8'))
    hashed_challenge = digest.finalize()

    while True:
        try:
            # substantial level means that the PIN is required
            if LoA == "substantial":
                # ask for the PIN
                pin = input("Please enter your PIN: ").strip()

                holder_private_key = load_pem_private_key(
                    vc["vc_json"]["private_pem_substantial_loa"].encode("utf-8"),
                    password=pin.encode('utf-8'),
                    backend=default_backend()
                )
            # low means that only presenting the card is enough
            elif LoA == "low":
                holder_private_key = load_pem_private_key(
                    vc["vc_json"]["private_pem_low_loa"].encode("utf-8"),
                    password=None,
                    backend=default_backend()
                )
            # encrypt the hash of the challenge
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

        # send signature and the holder id to the interface
        r = requests.post("http://127.0.0.1:1733/send_challenge_to_verifier", json={"vc": holder_vc, "signature": signature})

        error_messages = ["No corresponding challenge.", "Invalid group", "Invalid PIN", "Too many tries."]
        if LoA == "low" or r.json()["valid"] == "yes" or ("reason" in r.json() and r.json()["reason"] in error_messages):
            break

    return r.json()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f"Wrong arguments!\n\tUsage: {sys.argv[0]} <holder id>")
        exit(1)

    holder_id = sys.argv[1]
    holder_vc = f"holder_{holder_id}.json"

    print("Menu:\n\t1 - Get VC\n\t2 - Authenticate\n\tOther - Exit")

    vc = None
    choice = input(">> ").lower().strip()
    while choice == "1" or choice == "2":
        if choice == "1":
            name = input("Please enter your name: ").strip()
            nationality = input("Please enter nationality: ").strip()
            health_code = input("Please enter health code: ").strip()
            vc, pin = get_vc(holder_vc, {'full_name': name, "nationality": nationality, "holder_id": holder_id, "health_code": "teste"})
            print(f"Got vc!\n\tPin: {pin}\n\tSaved as: {holder_vc}")
        else:
            if vc == None:
                print("Please request your vc first!")
            else:
                result = solve_challenge(vc)
                if result["valid"] == "yes":
                    print("The challenge resolution was successful!")
                else:
                    print(f"The challenge resolution was NOT successful with the following messsage:\n\t{result["reason"]}")

        choice = input(">> ").lower().strip()
