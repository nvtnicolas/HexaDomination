# Import necessary libraries
import pygame
import sys

class GameInterface:
    def __init__(self, width, height):
        # Initialize Pygame
        pygame.init()
        
        # Set up the display
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("HexaDomination")
        
        # Set up colors
        self.bg_color = (255, 255, 255)  # White background
        self.board_color = (0, 128, 0)   # Green for the board
        self.text_color = (0, 0, 0)      # Black for text
        
        # Set up fonts
        self.font = pygame.font.Font(None, 36)

    def draw_board(self):
        # Clear the screen
        self.screen.fill(self.bg_color)
        
        # Draw the game board (placeholder for actual board drawing logic)
        pygame.draw.rect(self.screen, self.board_color, (50, 50, 700, 700))
        
        # Update the display
        pygame.display.flip()

    def display_message(self, message):
        # Render the message
        text = self.font.render(message, True, self.text_color)
        self.screen.blit(text, (50, 10))
        pygame.display.flip()

    def run(self):
        # Main loop
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            
            self.draw_board()
            self.display_message("Welcome to HexaDomination!")
            pygame.time.delay(100)

# Example usage
if __name__ == "__main__":
    game_interface = GameInterface(800, 800)
    game_interface.run()