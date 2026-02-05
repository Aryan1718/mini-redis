import socket
import threading
import time

def test_single_client(client_id):
    try:
        s = socket.create_connection(("localhost", 6379), timeout=5)
        print(f"[Client {client_id}] Connected")
        
        # Test 1: PING
        s.sendall(b"PING\r\n")
        response = s.recv(1024)
        print(f"[Client {client_id}] Received: {response.decode().strip()}")
        assert response == b"+PONG\r\n"
        
        # Test 2: Another PING (Persistent connection check)
        s.sendall(b"PING\r\n")
        response = s.recv(1024)
        print(f"[Client {client_id}] Received 2: {response.decode().strip()}")
        assert response == b"+PONG\r\n"
        
        s.close()
        return True
    except Exception as e:
        print(f"[Client {client_id}] Error: {e}")
        return False

# Run concurrent tests
threads = []
print("Starting concurrency test...")
for i in range(3):
    t = threading.Thread(target=test_single_client, args=(i,))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

print("Test finished.")
