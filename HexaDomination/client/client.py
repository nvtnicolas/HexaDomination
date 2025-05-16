import socket
import json

class HexaDominationClient:
    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port
        self.socket = None

    def connect_to_server(self):
        """Establish a connection to the game server."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.server_ip, self.server_port))
            print("Connected to server at {}:{}".format(self.server_ip, self.server_port))
        except Exception as e:
            print("Failed to connect to server: {}".format(e))

    def send_message(self, message):
        """Send a message to the server."""
        try:
            self.socket.sendall(json.dumps(message).encode('utf-8'))
        except Exception as e:
            print("Failed to send message: {}".format(e))

    def receive_message(self):
        """Receive a message from the server."""
        try:
            response = self.socket.recv(4096)
            return json.loads(response.decode('utf-8'))
        except Exception as e:
            print("Failed to receive message: {}".format(e))
            return None

    def close_connection(self):
        """Close the connection to the server."""
        if self.socket:
            self.socket.close()
            print("Connection closed.")

if __name__ == "__main__":
    client = HexaDominationClient("127.0.0.1", 12345)
    client.connect_to_server()
    # Additional client logic would go here
    client.close_connection()