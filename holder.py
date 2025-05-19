import sqlite3, requests, sys, json

def get_vc(holder_vc, data):
    #Sends the name and nationality
    r = requests.post("http://127.0.0.1:1337/register_holder", json=data)

    vc = r.json()
    print("Your pin is " ,vc["vc_json"]["holder_pin"])
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
