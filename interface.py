from flask import Flask, request
import requests, random

app = Flask(__name__)

loa = ["high"]

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

high_acces_req_underway = False
curr_high_access_req = {
    'try_count': 0,
    'group': 0,
}

@app.post("/auth_req")
def auth_req():
    global high_acces_req_underway, curr_high_access_req
    vc = request.get_json()["vc"]

    if not high_acces_req_underway:
        LoA = random.choice(loa)

        if LoA == "high":
            print("STARTING HIGH")
            LoA = "substantial"
            high_acces_req_underway = True
            curr_high_access_req['try_count'] = 0
            curr_high_access_req['group'] = original_national_base_list.index(vc["original_national_base"])
    else:
        LoA = "substantial"

    r = requests.post("http://127.0.0.1:3317/auth_req", json={"did_identifier": vc["did_identifier"], "loa": LoA})

    var = r.json()
    var.update({'loa': LoA})
    return var

@app.post("/send_challenge_to_verifier")
def send_challenge_to_verifier():
    global high_acces_req_underway, curr_high_access_req
    signature = request.get_json()["signature"]
    vc = request.get_json()["vc"]
    group = original_national_base_list.index(vc["vc_json"]["original_national_base"])

    r = requests.post("http://127.0.0.1:3317/validate_challenge", json={"vc": vc, "signature": signature})
    if high_acces_req_underway:
        if r.json()["valid"] == "yes" and group == curr_high_access_req['group']:
            curr_high_access_req['try_count'] += 1
        else:
            high_acces_req_underway = False
            return {"valid": "no", "reason": "Invalid group"}

        if curr_high_access_req['try_count'] == 3:
            high_acces_req_underway = False
            print("Door Open!!!!")
    elif r.json()["valid"] == "yes":
        print("Door Open!!!!")

    return r.json()

if __name__ == '__main__':
    app.run(debug=True, port=1733)
