import requests, random, string, json
from flask import Flask, request

from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric.utils import Prehashed
import base64

app = Flask(__name__)

challenges = []

@app.route("/auth_req", methods=["POST"])
def auth_req():
    vc = request.get_json()["vc"]
    user_data = vc["vc_json"]

    # check if the vc signature or date is invalid
    r = requests.post("http://127.0.0.1:1337/check_vc_validity", json={"vc": vc})
    if r.json()["valid"] == "no":
        return {"valid": "no", "reason": "Invalid challenge signature."}

    r = requests.get("http://127.0.0.1:3173/resolve_did", json={"did_identifier": user_data["did_identifier"], "loa": request.get_json()["loa"]})

    public_key = r.json()["public_key"]
    challenge = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(64))
    challenges.append([user_data["did_identifier"], challenge, public_key])

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
            challenge_index = i

    if challenge_index == -1:
        return {"valid": "no", "reason": "No corresponding challenge."}

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
        print("exception:", inst)
        print(f"Signature is invalid.")
        return {"valid": "no"}

    challenges.remove([did_identifier, original_chall, original_holder_pub_key.encode('utf-8').decode('utf-8')])
    return {"valid": "yes"}

if __name__ == '__main__':
    app.run(debug=True, port=3317)
