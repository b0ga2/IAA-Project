from flask import Flask
import sqlite3

app = Flask(__name__)

def create_db():
    conn = sqlite3.connect("wallet.db")
    with open('wallet.sql') as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()

@app.route("/get_vc")
def get_vc():
    return {'a': 0}

if __name__ == '__main__':
    create_db()
    app.run(debug=True, port=7331)
    
    
