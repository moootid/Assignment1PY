import socket
import threading
import time

class ChatClient:
    def __init__(self, client_id, host='127.0.0.1', port=65432):
        self.client_id = client_id
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.alive = True

    def connect_to_server(self):
        self.socket.connect((self.host, self.port))
        self.send_message("-SERVER-", f"Connect {self.client_id}")
        threading.Thread(target=self.listen_for_messages).start()
        threading.Thread(target=self.send_alive_message, daemon=True).start()

    def listen_for_messages(self):
        try:
            while self.alive:
                message = self.socket.recv(256).decode('utf-8')
                if message:
                    dest, src, msg = self.parse_message(message)
                    if msg:
                        print(f"Message from {dest}: {msg}")
        except Exception as e:
            print(f"Error receiving message: {e}")
        finally:
            self.socket.close()

    def send_message(self, dest, msg):
        full_msg = f"{dest:<8}{self.client_id:<8}{msg}".ljust(255, '\x00')
        self.socket.sendall(full_msg.encode('utf-8'))

    def send_alive_message(self):
        while self.alive:
            time.sleep(10) 
            self.send_message("-SERVER-", "Alive " + self.client_id)

    def parse_message(self, message):
        dest = message[:8].strip()
        src = message[8:16].strip()
        msg = message[16:].strip('\x00')
        return dest, src, msg
    


    def user_input_loop(self):
        try:
            while True:
                user_input = input("Enter command: ")
                if user_input.lower().startswith("@send"):
                    _, recipient_id, *message_parts = user_input.split()
                    message = ' '.join(message_parts)
                    self.send_message(recipient_id, message)
                elif user_input.lower() == "@quit":
                    self.send_message("-SERVER-", "@Quit")
                    break
                elif user_input.lower() == "@list":
                    self.send_message("-SERVER-", "@List")
                else:
                    print("Unknown command.")
        except KeyboardInterrupt:
            self.send_message("-SERVER-", "@Quit")
        finally:
            self.socket.close()

if __name__ == "__main__":
    client_id = input("Enter your client ID (max 8 characters): ").strip()[:8]
    client = ChatClient(client_id)
    client.connect_to_server()
    client.user_input_loop()
