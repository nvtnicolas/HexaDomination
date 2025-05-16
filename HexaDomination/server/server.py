import socket
import threading
import json

class HexaDominationServer:
    def __init__(self, host='127.0.0.1', port=12345):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((host, port))
        self.server_socket.listen(5)
        self.clients = []
        print(f"Server started on {host}:{port}")

    def handle_client(self, client_socket, address):
        print(f"Connection established with {address}")
        self.clients.append(client_socket)

        while True:
            try:
                message = client_socket.recv(1024).decode('utf-8')
                if not message:
                    break
                self.broadcast(message, client_socket)
            except Exception as e:
                print(f"Error: {e}")
                break

        client_socket.close()
        self.clients.remove(client_socket)
        print(f"Connection closed with {address}")

    def broadcast(self, message, sender_socket):
        for client in self.clients:
            if client != sender_socket:
                try:
                    client.send(message.encode('utf-8'))
                except Exception as e:
                    print(f"Error sending message: {e}")

    def start(self):
        while True:
            client_socket, address = self.server_socket.accept()
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket, address))
            client_thread.start()

if __name__ == "__main__":
    server = HexaDominationServer()
    server.start()