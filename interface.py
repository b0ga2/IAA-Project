from flask import Flask, request
import requests, random

app = Flask(__name__)

loa = ["low", "substantial"]

@app.post("/auth_req")
def auth_req():
    user_data = request.get_json()
    LoA = random.choice(loa)
    r = requests.post("http://127.0.0.1:3317/auth_req", json={"did_identifier": user_data["did_identifier"], "loa": LoA})

    var = r.json()
    var.update({'loa': LoA})

    return var

@app.post("/send_challenge_to_verifier")
def send_challenge_to_verifier():
    signature = request.get_json()["signature"]
    print(signature)
    did_identifier = request.get_json()["did_identifier"]

    r = requests.post("http://127.0.0.1:3317/validate_challenge", json={"did_identifier": did_identifier, "signature": signature})

    return r.json()

# @app.get("/solve_challenge")
# def solve_challenge():
#     user_data = request.get_json()
#     r = requests.post("http://127.0.0.1:3317/auth_req", json={"did_identifier": user_data["did_identifier"], "loa": random.choice(loa)})
#     return ""

if __name__ == '__main__':
    app.run(debug=True, port=1733)
