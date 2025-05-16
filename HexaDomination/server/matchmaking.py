# matchmaking.py

import socket
import threading
from queue import Queue

class Matchmaking:
    def __init__(self):
        self.waiting_players = Queue()
        self.lock = threading.Lock()

    def add_player(self, player):
        with self.lock:
            self.waiting_players.put(player)
            print(f"Player {player} added to the queue.")

    def match_players(self):
        while True:
            if self.waiting_players.qsize() >= 2:
                player1 = self.waiting_players.get()
                player2 = self.waiting_players.get()
                self.start_game(player1, player2)

    def start_game(self, player1, player2):
        print(f"Starting game between {player1} and {player2}.")
        # Here you would initiate the game logic, e.g., creating a game session

# Example usage
if __name__ == "__main__":
    matchmaking = Matchmaking()
    # This would typically be called when a player connects
    matchmaking.add_player("Player1")
    matchmaking.add_player("Player2")
    
    # Start the matchmaking process in a separate thread
    threading.Thread(target=matchmaking.match_players, daemon=True).start()