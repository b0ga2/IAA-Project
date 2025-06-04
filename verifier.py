import requests, random, string, json
from flask import Flask, request

from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric.utils import Prehashed
import base64

app = Flask(__name__)

challenges = []

# TODO: do revocation lists and verify them

@app.route("/auth_req", methods=["POST"])
def auth_req():
    user_data = request.get_json()
    r = requests.get("http://127.0.0.1:3173/resolve_did", json={"did_identifier": user_data["did_identifier"], "loa": user_data["loa"]})

    public_key = r.json()["public_key"]
    challenge = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(64))
    challenges.append([user_data["did_identifier"], challenge, public_key, 0])

    return {"challenge": challenge}

@app.route("/validate_challenge", methods=["POST"]) 
def validate_challenge():
    vc = request.get_json()["vc"]
    signature = bytes(request.get_json()["signature"])
    did_identifier = vc["vc_json"]["did_identifier"]

    challenge_index = -1
    for i, challenge in enumerate(challenges):
        if did_identifier == challenge[0]:
            original_chall = challenge[1]
            original_holder_pub_key = challenge[2]
            number_of_tries = challenge[3]
            challenge_index = i

    if challenge_index == -1:
        return {"valid": "no", "reason": "No corresponding challenge."}

    # revoke the card if the user misses the pin at least 3 times
    challenges[challenge_index][3] += 1
    if number_of_tries >= 2:
        digest = hashes.Hash(hashes.SHA256())
        digest.update(json.dumps(vc, sort_keys=True).encode('utf-8'))
        vc_hash = [x for x in digest.finalize()]

        challenges.remove([did_identifier, original_chall, original_holder_pub_key.encode('utf-8').decode('utf-8'), number_of_tries + 1])
        requests.post("http://127.0.0.1:1337/revoke_vc", json={"vc_hash": vc_hash, "motive": "Entered the wrong pin too many times."})
        requests.post("http://127.0.0.1:3173/revoke_vc", json={"did_identifier": vc["vc_json"]["did_identifier"]})
        return {"valid": "no", "reason": "Too many tries."}

    # check if the vc signature or date is invalid
    r = requests.post("http://127.0.0.1:1337/check_vc_validity", json={"vc": vc})
    if r.json()["valid"] == "no":
        return {"valid": "no", "reason": "Invalid challenge signature."}

    holder_pub_key = load_pem_public_key(original_holder_pub_key.encode("utf-8"))

    # Hash of the challenge
    digest = hashes.Hash(hashes.SHA256())
    digest.update(original_chall.encode('utf-8'))
    hashed_challenge = digest.finalize()

    # check the attribute signature
    try:
        holder_pub_key.verify(
            signature,
            hashed_challenge,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            Prehashed(hashes.SHA256())
        )
    except Exception as inst:
        print(inst)
        print(f"Signature is invalid.")
        return {"valid": "no"}

    challenges.remove([did_identifier, original_chall, original_holder_pub_key.encode('utf-8').decode('utf-8'), number_of_tries + 1])
    return {"valid": "yes"}

if __name__ == '__main__':
    app.run(debug=True, port=3317)
