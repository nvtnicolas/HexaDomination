# Game Logic for HexaDomination

class Game:
    def __init__(self):
        self.board = self.initialize_board()
        self.current_turn = None
        self.players = []

    def initialize_board(self):
        # Initialize the game board with hexagonal tiles
        return [[None for _ in range(10)] for _ in range(10)]  # Example size

    def add_player(self, player):
        if len(self.players) < 2:
            self.players.append(player)
            if len(self.players) == 2:
                self.start_game()
        else:
            raise Exception("Game is already full.")

    def start_game(self):
        self.current_turn = self.players[0]

    def make_move(self, player, position):
        if player != self.current_turn:
            raise Exception("It's not your turn.")
        if self.is_valid_move(position):
            self.board[position[0]][position[1]] = player
            self.check_victory(player)
            self.switch_turn()
        else:
            raise Exception("Invalid move.")

    def is_valid_move(self, position):
        # Check if the move is valid (e.g., within bounds and on an empty tile)
        return (0 <= position[0] < len(self.board) and
                0 <= position[1] < len(self.board[0]) and
                self.board[position[0]][position[1]] is None)

    def switch_turn(self):
        self.current_turn = self.players[1] if self.current_turn == self.players[0] else self.players[0]

    def check_victory(self, player):
        # Implement victory condition checks
        pass

# Additional helper functions can be added as needed.