from flask import Flask

app = Flask(__name__)

@app.route("/get_vc")
def get_vc():
    return {'a': 0}

if __name__ == '__main__':
    app.run(debug=True, port=1337)
