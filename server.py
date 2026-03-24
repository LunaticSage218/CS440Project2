import json
import sqlite3
import os
import threading
import urllib.request
import urllib.error
from http.server import SimpleHTTPRequestHandler, HTTPServer


class Contact:
    def __init__(self, id=None, name="", phone="", address=""):
        self.id = id
        self.name = name
        self.phone = phone
        self.address = address

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "phone": self.phone,
            "address": self.address
        }


PORT = int(os.environ.get("PORT", "8000"))
DB_NAME = os.environ.get("DB_NAME", f"contacts_{PORT}.db")
PEERS = [
    p.strip().rstrip("/")
    for p in os.environ.get("PEERS", "").split(",")
    if p.strip()
]

base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, DB_NAME)


def _connect():
    return sqlite3.connect(db_path)


def _init_db():
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            address TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def get_all():
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM contacts")
    rows = cursor.fetchall()
    conn.close()
    return [Contact(*row) for row in rows]


def add(contact: Contact):
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO contacts (name, phone, address) VALUES (?, ?, ?)",
        (contact.name, contact.phone, contact.address)
    )
    contact_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return contact_id


def add_with_id(contact: Contact):
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO contacts (id, name, phone, address) VALUES (?, ?, ?, ?)",
        (contact.id, contact.name, contact.phone, contact.address)
    )
    conn.commit()
    conn.close()


def update(contact: Contact):
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE contacts SET name=?, phone=?, address=? WHERE id=?",
        (contact.name, contact.phone, contact.address, contact.id)
    )
    conn.commit()
    conn.close()


def delete(contact_id: int):
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM contacts WHERE id=?", (contact_id,))
    conn.commit()
    conn.close()


def broadcast_to_peers(message):
    def send(peer_url):
        try:
            req = urllib.request.Request(
                f"{peer_url}/api/sync",
                data=json.dumps(message).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            urllib.request.urlopen(req, timeout=2)
        except Exception:
            pass

    for peer in PEERS:
        threading.Thread(target=send, args=(peer,), daemon=True).start()


class ContactHandler(SimpleHTTPRequestHandler):

    def do_GET(self):
        if self.path == "/api/contacts":
            contacts = get_all()
            response = json.dumps([c.to_dict() for c in contacts]).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(response)

        elif self.path == "/api/peers":
            response = json.dumps({
                "port": PORT,
                "peers": PEERS,
                "database": DB_NAME
            }).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(response)

        else:
            super().do_GET()

    def do_POST(self):
        if self.path == "/api/contacts":
            length = int(self.headers["Content-Length"])
            data = json.loads(self.rfile.read(length))

            new_contact = Contact(
                name=data["name"],
                phone=data["phone"],
                address=data["address"]
            )
            new_id = add(new_contact)

            full_contact = Contact(
                id=new_id,
                name=data["name"],
                phone=data["phone"],
                address=data["address"]
            )

            broadcast_to_peers({
                "type": "create",
                "contact": full_contact.to_dict()
            })

            self.send_response(201)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(full_contact.to_dict()).encode())

        elif self.path == "/api/sync":
            length = int(self.headers["Content-Length"])
            data = json.loads(self.rfile.read(length))

            sync_type = data.get("type")

            if sync_type == "create":
                c = data["contact"]
                add_with_id(Contact(
                    id=c["id"],
                    name=c["name"],
                    phone=c["phone"],
                    address=c["address"]
                ))
                self.send_response(200)
                self.end_headers()

            elif sync_type == "update":
                c = data["contact"]
                update(Contact(
                    id=c["id"],
                    name=c["name"],
                    phone=c["phone"],
                    address=c["address"]
                ))
                self.send_response(200)
                self.end_headers()

            elif sync_type == "delete":
                delete(data["id"])
                self.send_response(200)
                self.end_headers()

            else:
                self.send_response(400)
                self.end_headers()

    def do_PUT(self):
        if self.path.startswith("/api/contacts/"):
            contact_id = int(self.path.split("/")[-1])
            length = int(self.headers["Content-Length"])
            data = json.loads(self.rfile.read(length))

            updated_contact = Contact(
                id=contact_id,
                name=data["name"],
                phone=data["phone"],
                address=data["address"]
            )

            update(updated_contact)

            broadcast_to_peers({
                "type": "update",
                "contact": updated_contact.to_dict()
            })

            self.send_response(200)
            self.end_headers()

    def do_DELETE(self):
        if self.path.startswith("/api/contacts/"):
            contact_id = int(self.path.split("/")[-1])
            delete(contact_id)

            broadcast_to_peers({
                "type": "delete",
                "id": contact_id
            })

            self.send_response(200)
            self.end_headers()


if __name__ == "__main__":
    _init_db()
    static_dir = os.path.join(base_dir, "static")
    os.chdir(static_dir)
    server = HTTPServer(("localhost", PORT), ContactHandler)
    print(f"Peer running at http://localhost:{PORT}")
    print(f"Database: {DB_NAME}")
    print(f"Known peers: {PEERS}")
    server.serve_forever()