from flask import Flask, request
import requests, random, string

app = Flask(__name__)

challenges = []

@app.route("/auth_req", methods=["POST"])
def auth_req():
    user_data = request.get_json()
    r = requests.get("http://127.0.0.1:3173/resolve_did", json={"did_identifier": user_data["did_identifier"], "loa": user_data["loa"]})

    public_key = r.json()["public_key"]
    challenge = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(64))
    challenges.append((user_data["did_identifier"], challenge, public_key))

    return {"challenge": challenge}

if __name__ == '__main__':
    app.run(debug=True, port=3317)
