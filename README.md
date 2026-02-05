# Build Your Own Redis (Python)

A lightweight, multi-threaded Redis server implementation in Python. This project aims to replicate the core functionality of Redis, including the RESP protocol, key-value storage, and handling concurrent client connections, serving as a deep dive into network programming and database internals.

## 🚀 Project Status
**Current Phase: Phase 1 (Networking & Concurrency)**
The server successfully binds to a port, accepts multiple concurrent TCP connections, and implements the basic Redis protocol handshake.

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

## 🗺️ Roadmap
- [x] **Phase 1**: Networking foundation & Concurrency (Threaded Server)
- [x] **Phase 2**: Command Parsing (`ECHO`, `SET`, `GET`) & Storage Engine
- [x] **Phase 3**: Key Expiry (`PX` argument)
- [ ] **Phase 4**: Persistence (RDB) & Advanced Features

## 🤝 Contributing
This is an educational project. Feel free to fork and build your own!
