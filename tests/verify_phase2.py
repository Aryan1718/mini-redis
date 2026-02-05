import socket
import time

def send_command(sock, command):
    # Very simple RESP encoder for flat lists of commands
    parts = command.split()
    cmd = f"*{len(parts)}\r\n"
    for p in parts:
        cmd += f"${len(p)}\r\n{p}\r\n"
    sock.sendall(cmd.encode())
    
    # Read response (naive)
    data = sock.recv(1024).decode()
    return data

def test_phase_2():
    try:
        s = socket.create_connection(("localhost", 6379), timeout=2)
        print("[Connected]")
        
        # Test 1: PING
        res = send_command(s, "PING")
        print(f"PING -> {res.strip()}")
        assert "+PONG" in res
        
        # Test 2: ECHO
        res = send_command(s, "ECHO hello-world")
        print(f"ECHO hello-world -> {res.strip()}")
        assert "$11\r\nhello-world" in res
        
        # Test 3: SET and GET
        res = send_command(s, "SET mykey myvalue")
        print(f"SET mykey myvalue -> {res.strip()}")
        assert "+OK" in res
        
        res = send_command(s, "GET mykey")
        print(f"GET mykey -> {res.strip()}")
        assert "$7\r\nmyvalue" in res
        
        # Test 4: Expiry
        res = send_command(s, "SET tempkey tempval PX 100")
        print(f"SET tempkey tempval PX 100 -> {res.strip()}")
        assert "+OK" in res
        
        res = send_command(s, "GET tempkey")
        print(f"GET tempkey (immediate) -> {res.strip()}")
        assert "tempval" in res
        
        print("Waiting 0.2s for expiry...")
        time.sleep(0.2)
        
        res = send_command(s, "GET tempkey")
        print(f"GET tempkey (after wait) -> {res.strip()}")
        assert "$-1" in res # Null bulk string
        
        print("ALL TESTS PASSED")
        s.close()
    except Exception as e:
        print(f"TEST FAILED: {e}")

if __name__ == "__main__":
    test_phase_2()
