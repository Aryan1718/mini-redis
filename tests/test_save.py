import socket
import subprocess
import time
import os
import sys

SERVER_HOST = "localhost"
SERVER_PORT = 6379
DB_FILE = "test_dump.rdb"

def start_server():
    # Remove existing dump if any
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        
    process = subprocess.Popen(
        [sys.executable, "-m", "app.main", "--dbfilename", DB_FILE],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    time.sleep(1) # Wait for startup
    return process

def send_command(sock, command):
    sock.sendall(command.encode())
    response = sock.recv(1024)
    return response.decode()

def test_save_and_restore():
    print("Starting server...")
    server_proc = start_server()
    
    try:
        with socket.create_connection((SERVER_HOST, SERVER_PORT)) as sock:
            print("Connected. Setting key 'foo' to 'bar'")
            # RESP for SET foo bar
            cmd = "*3\r\n$3\r\nSET\r\n$3\r\nfoo\r\n$3\r\nbar\r\n"
            resp = send_command(sock, cmd)
            print(f"SET response: {resp.strip()}")
            assert "+OK" in resp
            
            print("Sending SAVE command")
            cmd = "*1\r\n$4\r\nSAVE\r\n"
            resp = send_command(sock, cmd)
            print(f"SAVE response: {resp.strip()}")
            assert "+OK" in resp
            
    finally:
        print("Killing server...")
        server_proc.terminate()
        server_proc.wait()
        
    print("Server stopped. Checking if RDB file exists...")
    if not os.path.exists(DB_FILE):
        print("FAILURE: RDB file was not created.")
        return
        
    print("RDB file exists. Restarting server to verify load...")
    
    server_proc = subprocess.Popen(
        [sys.executable, "-m", "app.main", "--dbfilename", DB_FILE],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    time.sleep(1)
    
    try:
        with socket.create_connection((SERVER_HOST, SERVER_PORT)) as sock:
            print("Connected. Getting key 'foo'")
            cmd = "*2\r\n$3\r\nGET\r\n$3\r\nfoo\r\n"
            resp = send_command(sock, cmd)
            print(f"GET response: {resp.strip()}")
            # Expecting Bulk String: $3\r\nbar\r\n
            if "$3\r\nbar" in resp:
                print("SUCCESS: Key 'foo' was restored correctly.")
            else:
                print(f"FAILURE: Expected 'bar', got {resp}")
                
    finally:
        server_proc.terminate()
        server_proc.wait()
        # Cleanup
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)

if __name__ == "__main__":
    test_save_and_restore()
