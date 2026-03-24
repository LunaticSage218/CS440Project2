## Running the Peer-to-Peer Version

### Requirements
- Python 3.x

### Steps
Run three peers in separate terminals.

#### Terminal 1
```powershell
$env:PORT="8000"
$env:DB_NAME="contacts_8000.db"
$env:PEERS="http://localhost:8001,http://localhost:8002"
python server.py