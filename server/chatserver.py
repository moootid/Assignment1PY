import socket
import threading

class ChatServer:
    # Initialize the server with a host address and port number.
    # Set up the server socket and bind it to the specified host and port.
    # Begin listening for incoming connections.
    def __init__(self, host='127.0.0.1', port=65432):
        self.host = host
        self.port = port
        self.clients = {}  # Maps client ID to connection
        self.lock = threading.Lock()
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()
        print(f"Server started on {self.host}:{self.port}")
    # Accept incoming client connections in an infinite loop.
    # For each connection, spawn a new thread to handle the client.
    def accept_connections(self):
        while True:
            conn, addr = self.server_socket.accept()
            print(f"Connection from {addr}")
            threading.Thread(target=self.handle_client, args=(conn, addr), daemon=True).start()

    # Handle communication with a connected client.
    # Receive messages, parse them, and perform actions based on the message content.
    def handle_client(self, conn, addr):
        client_id = None
        try:
            while True:
                message = conn.recv(256)
                if not message:
                    break  # Client has disconnected
                message = message.decode('utf-8')
                dest, src, msg = self.parse_message(message)
                print(f"Received message: {dest} {src} {msg}")
                if src == "-SERVER-":
                    continue  # Ignore messages intended for the server itself
                
                if msg.startswith("Connect"):
                    client_id = src
                    self.add_client(client_id, conn)
                    self.broadcast_client_list()
                elif msg == "@Quit":
                    break
                elif msg == "@List":
                    print(f"Sending client list to {client_id}")
                    self.send_client_list(client_id)
                elif dest and dest in self.clients:
                    print(f"2dest: {dest} src:{src} msg: {msg}")
                    self.forward_message(dest, src, msg)
                elif msg.startswith("@Send"):
                    print(f"dest: {dest} src:{src} msg: {msg}")
                    self.forward_message(dest, src, msg)
                else:
                    print(f"Message to unknown dest: {dest}")

        except Exception as e:
            print(f"Error with client {client_id} at {addr}: {e}")
        finally:
            if client_id:
                self.remove_client(client_id)
            conn.close()
            print(f"Connection closed for client {client_id} at {addr}")

    def add_client(self, client_id, conn):
        with self.lock:
            self.clients[client_id] = conn
            print(f"Client {client_id} added.")

    def remove_client(self, client_id):
        with self.lock:
            if client_id in self.clients:
                del self.clients[client_id]
                print(f"Client {client_id} removed.")

    def forward_message(self, dest, src, msg):
        if dest in self.clients:
            try:
                message_formatted = f"{src:<8}{dest:<8}{msg}".ljust(255, '\x00')
                print(f"Forwarding message: {message_formatted}")
                # print(message_formatted)
                self.clients[dest].sendall(message_formatted.encode('utf-8'))
            except Exception as e:
                print(f"Error forwarding message from {src} to {dest}: {e}")
    
    def send_client_list(self, client_id):
        with self.lock:
            if client_id in self.clients:
                client_list = "Online clients: " + ", ".join(self.clients.keys())
                self.send_message("-SERVER-", self.clients[client_id], client_list)

    def broadcast_client_list(self):
        with self.lock:
            client_list = "Online clients: " + ", ".join(self.clients.keys())
            for client_socket in self.clients.values():
                self.send_message("-SERVER-", client_socket, client_list)
        
    def send_message(self, src, client_socket, msg):
        formatted_msg = f"{src:<8}{'-SERVER-':<8}{msg}".ljust(256, '\x00')
        client_socket.sendall(formatted_msg.encode('utf-8'))

    def parse_message(self, message):
        if len(message) < 16:  # Basic validation
            return None, None, None
        dest = message[:8].strip()
        src = message[8:16].strip()
        msg = message[16:].rstrip('\x00')
        return dest, src, msg

    def start(self):
        try:
            self.accept_connections()
        except Exception as e:
            print(f"Server error: {e}")
        finally:
            self.server_socket.close()
            print("Server shut down.")

if __name__ == "__main__":
    server = ChatServer()
    server.start()
