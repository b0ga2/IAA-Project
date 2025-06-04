import requests, sqlite3, random, string
from flask import Flask, request

# TODO: Correct the db in the blockchain when a new user is added

app = Flask(__name__)

def generate_random_did(length=64):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def create_db():
    conn = sqlite3.connect("blockchain.db")
    with open('blockchain.sql') as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()

@app.route("/register_did", methods=["GET"]) 
def register_did():
    # Obtain the body from the request
    user_data = request.get_json()

    # Connect to the database
    conn = sqlite3.connect("blockchain.db")
    cursor = conn.cursor()

    # Generate a random 64-character DID identifier
    did_identifier = generate_random_did()

    # Insert the record
    cursor.execute("INSERT INTO did_document (public_key_low_loa, public_key_susbtantial_loa, did_identifier) VALUES (?, ?, ?);",
        (user_data["public_pem_low_loa"], user_data["public_pem_substantial_loa"], did_identifier))

    # Commit and close
    conn.commit()
    conn.close()

    return {"did_identifier": did_identifier}

@app.get("/resolve_did")
def resolve_did():
    user_data = request.get_json()

    # Connect to the database
    conn = sqlite3.connect("blockchain.db")
    cursor = conn.cursor()

    # Resolve the DID identifier
    if user_data["loa"] == "low":
        public_key = cursor.execute("SELECT public_key_low_loa FROM did_document WHERE did_identifier=?", (user_data["did_identifier"],)).fetchone()[0]
    else:
        public_key = cursor.execute("SELECT public_key_susbtantial_loa FROM did_document WHERE did_identifier=?", (user_data["did_identifier"],)).fetchone()[0]

    # Commit and close
    conn.commit()
    conn.close()

    return {"public_key": public_key}

@app.post("/revoke_vc")
def revoke_vc():
    did_identifier = request.get_json()["did_identifier"]

    # Connect to the database
    conn = sqlite3.connect("blockchain.db")
    cursor = conn.cursor()

    # Resolve the DID identifier
    cursor.execute("DELETE FROM did_document WHERE did_identifier=?", (did_identifier,))

    # Commit and close
    conn.commit()
    conn.close()

    return {"a": 0}

if __name__ == '__main__':
    create_db()
    app.run(debug=True, port=3173)
