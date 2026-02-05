import socket
import sys

def encode_resp(command_str):
    parts = command_str.split()
    if not parts:
        return None
    proto = f"*{len(parts)}\r\n"
    for part in parts:
        proto += f"${len(part)}\r\n{part}\r\n"
    return proto.encode()

def main():
    print("Welcome to your custom Redis CLI via Python!")
    print("Connecting to localhost:6379...")
    
    try:
        s = socket.create_connection(("localhost", 6379), timeout=20)
        print("Connected! Type your commands (e.g., 'PING', 'SET name aryan', 'GET name'). Type 'exit' to quit.")
    except Exception as e:
        print(f"Could not connect: {e}")
        return

    while True:
        try:
            # Get input
            cmd = input("127.0.0.1:6379> ")
            if cmd.lower().strip() in ('exit', 'n', 'quit'):
                break
            if not cmd.strip():
                continue
            
            # Encode and send
            req = encode_resp(cmd)
            s.sendall(req)
            
            # Read response (simple read)
            response = s.recv(4096).decode()
            print(response.strip())
            
        except BrokenPipeError:
            print("Server disconnected.")
            break
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")
            break
    
    s.close()

if __name__ == "__main__":
    main()
