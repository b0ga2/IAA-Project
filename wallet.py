from flask import Flask
from flask import request

import sqlite3, datetime

app = Flask(__name__)

def create_db():
    conn = sqlite3.connect("wallet.db")
    with open('wallet.sql') as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()

@app.route("/register_vc", methods=["POST"])
def register_vc():
    user_data = request.get_json()

    #initial_date = user_data["initial_date"].date().isoformat()
    #final_date = user_data["initial_date"].date().isoformat()

    # Connect to your SQLite database
    conn = sqlite3.connect("wallet.db")
    cursor = conn.cursor()

    # Insert into the table
    cursor.execute("""
        INSERT INTO vcs (
            original_national_base, rank, division, security_clearance_level,
            health_code, nationality, full_name, holder_id,
            initial_date, final_date, did_identifier, issuer_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_data["original_national_base"], user_data["rank"], user_data["division"], user_data["security_clearance_level"],
        user_data["health_code"], user_data["nationality"], user_data["full_name"], user_data["holder_id"],
        user_data["initial_date"], user_data["final_date"], user_data["did_identifier"], user_data["issuer_id"]
    ))

    # Commit and close the connection
    conn.commit()
    conn.close()

    print(user_data)


    return {'a': 0}

if __name__ == '__main__':
    create_db()
    app.run(debug=True, port=7331)
