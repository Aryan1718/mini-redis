import socket  # noqa: F401
import threading
import time

DATA_STORE = {}
EXPIRY_STORE = {}

class RESPParser:
    def __init__(self, data):
        self.data = data
        self.pos = 0

    def parse(self):
        if self.pos >= len(self.data):
            return None
        
        byte = self.data[self.pos]
        # Array
        if byte == 42:  # '*'
            return self.parse_array()
        # Bulk String
        elif byte == 36: # '$'
            return self.parse_bulk_string()
        # Simple String (Inline commands often behave like this too for PING)
        elif byte == 43: # '+'
            return self.read_line()
        else:
            # Fallback for inline commands (like PING sent via netcat without RESP)
            return self.read_line().split()

    def read_line(self):
        start = self.pos
        while self.pos < len(self.data) and self.data[self.pos] != 13: # \r
            self.pos += 1
        line = self.data[start:self.pos].decode()
        self.pos += 2 # Skip \r\n
        return line

    def read_int(self):
        return int(self.read_line())

    def parse_bulk_string(self):
        self.pos += 1 # Skip $
        length = self.read_int()
        if length == -1:
            return None
        start = self.pos
        self.pos += length
        data = self.data[start:self.pos].decode()
        self.pos += 2 # Skip \r\n
        return data

    def parse_array(self):
        self.pos += 1 # Skip *
        count = self.read_int()
        items = []
        for _ in range(count):
            byte = self.data[self.pos]
            if byte == 36: # '$' indicates bulk string
                items.append(self.parse_bulk_string())
            elif byte == 58: # ':' integer
                # Not standard for command arrays but good for completeness
                self.pos += 1
                items.append(self.read_int())
        return items

def encode_bulk_string(s):
    if s is None:
        return b"$-1\r\n"
    return f"${len(s)}\r\n{s}\r\n".encode()

def encode_simple_string(s):
    return f"+{s}\r\n".encode()

def encode_error(msg):
    return f"-ERR {msg}\r\n".encode()

def handle_command(args):
    if not args:
        return encode_error("no command")
    
    cmd = args[0].upper()
    
    if cmd == "PING":
        return encode_simple_string("PONG")
    
    if cmd == "ECHO":
        if len(args) < 2:
            return encode_error("wrong number of arguments for 'echo' command")
        return encode_bulk_string(args[1])
        
    if cmd == "SET":
        if len(args) < 3:
            return encode_error("wrong number of arguments for 'set' command")
        key = args[1]
        val = args[2]
        expiry = None
        
        # Handle PX argument
        if len(args) > 3:
            for i in range(3, len(args)):
                if args[i].upper() == "PX" and i + 1 < len(args):
                    try:
                        px = int(args[i+1])
                        expiry = time.time() * 1000 + px
                    except ValueError:
                        return encode_error("value is not an integer or out of range")
        
        DATA_STORE[key] = val
        if expiry:
            EXPIRY_STORE[key] = expiry
        else:
            if key in EXPIRY_STORE:
                del EXPIRY_STORE[key] # Remove old expiry if overwriting
                
        return encode_simple_string("OK")
        
    if cmd == "GET":
        if len(args) < 2:
            return encode_error("wrong number of arguments for 'get' command")
        key = args[1]
        
        if key in EXPIRY_STORE:
            if time.time() * 1000 > EXPIRY_STORE[key]:
                del DATA_STORE[key]
                del EXPIRY_STORE[key]
                return encode_bulk_string(None)
                
        val = DATA_STORE.get(key)
        return encode_bulk_string(val)

    return encode_simple_string("PONG") # Fallback for unknown commands in early stages or return error

def main():
    print("Logs from your program will appear here!")
    server_socket = socket.create_server(("localhost", 6379), reuse_port=False)
    
    while True:
        client, addr = server_socket.accept()
        print(f"Accepted connection from {addr}")
        threading.Thread(target=handle_client, args=(client,)).start()

def handle_client(client_socket):
    try:
        data_buffer = b""
        while True:
            chunk = client_socket.recv(1024)
            if not chunk:
                break
            data_buffer += chunk
            
            # Attempt to parse
            while True:
                if not data_buffer:
                    break
                
                try:
                    parser = RESPParser(data_buffer)
                    # Peek to see if we have enough data? 
                    # For simplicity, we assume we get full commands in this stage 
                    # or that the buffer accumulates. 
                    # Real stream parsing is harder, but let's try a simple approach:
                    # If parser fails indexing, Wait for more data?
                    
                    # NOTE: A robust parser needs check validity before consuming. 
                    # Here we just try to parse.
                    
                    args = parser.parse()
                    
                    # If successful parse
                    if args:
                        response = handle_command(args)
                        client_socket.send(response)
                        # Remove consumed data from buffer
                        data_buffer = data_buffer[parser.pos:]
                    else:
                        break # Wait for more data
                        
                except IndexError:
                     # Not enough data yet
                    break
                    
    except ConnectionError:
        pass
    finally:
        client_socket.close()

if __name__ == "__main__":
    main()
