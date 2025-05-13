from flask import Flask
import sqlite3

app = Flask(__name__)
con = sqlite3.connect("issuer.db")

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"
