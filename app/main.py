import socket  # noqa: F401
import threading


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Uncomment this to pass the first stage
    #
    server_socket = socket.create_server(("localhost", 6379), reuse_port=False)
    
    while True:
        client, addr = server_socket.accept() # wait for client
        print(f"Accepted connection from {addr}")
        threading.Thread(target=handle_client, args=(client,)).start()

def handle_client(client_socket):
    try:
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            client_socket.send(b"+PONG\r\n")
    except ConnectionError:
        pass
    finally:
        client_socket.close()


if __name__ == "__main__":
    main()
