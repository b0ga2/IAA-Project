from flask import Flask
from flask import request
import requests

import sqlite3
import random
import string

def generate_random_did(length=64):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

app = Flask(__name__)

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
    cursor.execute("""
    INSERT INTO did_document (public_key_low_loa, public_key_susbtantial_loa, did_identifier)
    VALUES (?, ?, ?);
    """, (user_data["public_pem_low_loa"], user_data["public_pem_substantial_loa"], did_identifier))

    # Commit and close
    conn.commit()
    conn.close()

    return {"did_identifier":did_identifier}

if __name__ == '__main__':
    create_db()
    app.run(debug=True, port=3173)