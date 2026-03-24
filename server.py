import json
import sqlite3
import os
import asyncio
import websockets
from http.server import SimpleHTTPRequestHandler, HTTPServer

event_loop = None

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

base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, "contacts.db")

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

subscribers = set()

async def publish(event):
    message = json.dumps(event)

    for ws in list(subscribers):
        try:
            await ws.send(message)
        except:
            subscribers.remove(ws)

async def ws_handler(websocket):
    subscribers.add(websocket)
    try:
        async for _ in websocket:
            pass
    finally:
        subscribers.remove(websocket)


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

    asyncio.run_coroutine_threadsafe(publish({
        "event": "contact_added",
        "contact": {
            "id": contact_id,
            "name": contact.name,
            "phone": contact.phone,
            "address": contact.address
        }
    }), event_loop)


def update(contact: Contact):
    conn = _connect()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE contacts SET name=?, phone=?, address=? WHERE id=?",
        (contact.name, contact.phone, contact.address, contact.id)
    )

    conn.commit()
    conn.close()

    asyncio.run_coroutine_threadsafe(publish({
        "event": "contact_updated",
        "contact": contact.to_dict()
    }), event_loop)


def delete(contact_id: int):
    conn = _connect()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM contacts WHERE id=?", (contact_id,))

    conn.commit()
    conn.close()

    asyncio.run_coroutine_threadsafe(publish({
        "event": "contact_deleted",
        "id": contact_id
    }), event_loop)


class ContactHandler(SimpleHTTPRequestHandler):

    def do_GET(self):
        if self.path == "/api/contacts":

            contacts = get_all()

            response = json.dumps([c.to_dict() for c in contacts]).encode()

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

            add(Contact(
                name=data["name"],
                phone=data["phone"],
                address=data["address"]
            ))

            self.send_response(201)
            self.end_headers()


    def do_PUT(self):
        if self.path.startswith("/api/contacts/"):

            contact_id = int(self.path.split("/")[-1])

            length = int(self.headers["Content-Length"])
            data = json.loads(self.rfile.read(length))

            update(Contact(
                id=contact_id,
                name=data["name"],
                phone=data["phone"],
                address=data["address"]
            ))

            self.send_response(200)
            self.end_headers()


    def do_DELETE(self):
        if self.path.startswith("/api/contacts/"):

            contact_id = int(self.path.split("/")[-1])

            delete(contact_id)

            self.send_response(200)
            self.end_headers()


async def main():
    global event_loop
    event_loop = asyncio.get_running_loop()

    _init_db()

    os.chdir("static")

    http_server = HTTPServer(("localhost", 8000), ContactHandler)

    ws_server = await websockets.serve(ws_handler, "localhost", 8765)

    print("HTTP server running: http://localhost:8000")
    print("WebSocket server running: ws://localhost:8765")

    await asyncio.get_event_loop().run_in_executor(None, http_server.serve_forever)

asyncio.run(main())