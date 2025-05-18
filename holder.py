import sqlite3, requests, sys

#TODO: Do registation in holder and issuer

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f"Wrong arguments!\n\tUsage: {sys.argv[0]} <holder id>")
        exit(1)

    holder_id = sys.argv[1]
    holder_vc = f"holder_{holder_id}.json"

    #Sends the name and nationality
    r = requests.post("http://127.0.0.1:1337/register_holder", json={'full_name': 'TÓS',"nationality":"Out of this World", "holder_id": holder_id, "health_code": "teste"})
    #print(r.json())
