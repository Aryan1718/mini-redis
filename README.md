# Build Your Own Redis (Python)

A lightweight, multi-threaded Redis server implementation in Python. This project aims to replicate the core functionality of Redis, including the RESP protocol, key-value storage, and handling concurrent client connections, serving as a deep dive into network programming and database internals.

## 🚀 Project Status
**Current Phase: Phase 2 (Command Parsing & Storage)**
The server is now a fully functional Key-Value store with support for `SET`, `GET`, `ECHO`, and key expiry (`PX`), using a custom-built RESP parser.

## ✨ Features
- **TCP Server**: Listens on `localhost:6379`.
- **Concurrency**: Multi-threaded architecture to handle multiple clients simultaneously.
- **Redis Protocol (RESP)**:
    - [x] Responds to `PING` with `+PONG`.
    - [x] Full RESP Parsing (Arrays, Bulk Strings).
- **Storage Engine**:
    - [x] In-memory Key-Value Store (`SET`, `GET`).
    - [x] Key Expiration (`PX` argument).
- **Cross-Platform**: Tuned to work on Windows and Linux (socket reuse options handled).

## 🛠️ How to Run

### Prerequisites
- Python 3.8+

### Start the Server
You can run the server directly using Python:

```bash
# From the root directory
python -m app.main
```

Or use the provided helper script (Linux/Git Bash):
```bash
./your_program.sh
```

### Test Connectivity
You can connect using `netcat` or `redis-cli`:

```bash
$ redis-cli ping
PONG
```

### 🖥️ Native CLI Tool (Included)
If you don't have `redis-cli` installed, you can use the included Python CLI:

```bash
python cli.py
```
It supports interactions like:
```text
127.0.0.1:6379> SET name aryan
OK
127.0.0.1:6379> GET name
aryan
```

## 🏗️ Architecture
The server follows a multi-threaded request-response model:

```mermaid
sequenceDiagram
    participant Client
    participant Server (Main)
    participant Worker Thread
    participant RESP Parser
    participant Data Store

    Client->>Server (Main): Connect (TCP 6379)
    Server (Main)->>Worker Thread: Spawn new thread
    loop Request Cycle
        Client->>Worker Thread: Send Command (*3\r\n$3\r\nSET...)
        Worker Thread->>RESP Parser: Parse Bytes
        RESP Parser-->>Worker Thread: Return ["SET", "key", "val"]
        Worker Thread->>Data Store: Execute Command (Write/Read)
        Data Store-->>Worker Thread: Return Result
        Worker Thread->>Client: Send Response (+OK)
    end
```

**Key Components:**
1.  **Transport Layer**: `socket` + `threading` handles concurrent connections.
2.  **Protocol Layer**: `RESPParser` decodes raw bytes into Python lists.
3.  **Command Layer**: A dispatcher routes commands (`PING`, `SET`, `GET`, `ECHO`) to their handlers.
4.  **Storage Layer**: A thread-safe global dictionary holds data with optional expiry timestamps.

## 🗺️ Roadmap
- [x] **Phase 1**: Networking foundation & Concurrency (Threaded Server)
- [x] **Phase 2**: Command Parsing (`ECHO`, `SET`, `GET`) & Storage Engine
- [x] **Phase 3**: Key Expiry (`PX` argument)
- [ ] **Phase 4**: Persistence (RDB) & Advanced Features

## 🤝 Contributing
This is an educational project. Feel free to fork and build your own!
