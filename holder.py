import sqlite3, requests, sys


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f"Wrong arguments!\n\tUsage: {sys.argv[0]} <holder id>")
        exit(1)

    holder_id = sys.argv[1]
    hodler_vc = f"holder_{holder_id}.json"

    r = requests.get("http://127.0.0.1:1337/get_vc", {'name': 'sadsad'})
    print(r.json())
