"""Entry point script for running the CRx game."""

import pygame
import sys
from src.menu import Menu
from src.game import Game
from src.game_over import GameOverScreen


def main():
    """Main game loop handling menu, game, and game over screens."""
    pygame.init()
    
    while True:
        # Show menu
        menu = Menu()
        num_players = menu.run()
        
        if not num_players:
            pygame.quit()
            sys.exit()
        
        # Play the game
        game = Game(num_players=num_players)
        winner = game.run()
        
        # Show game over screen
        game_over = GameOverScreen(winner, num_players)
        choice = game_over.run()
        
        if choice == "quit":
            pygame.quit()
            sys.exit()
        elif choice == "menu":
            continue  # Go back to menu
        elif choice == "play_again":
            # Play again with same number of players
            game = Game(num_players=num_players)
            winner = game.run()
            
            # Show game over again
            game_over = GameOverScreen(winner, num_players)
            choice = game_over.run()
            
            if choice == "quit":
                pygame.quit()
                sys.exit()


if __name__ == "__main__":
    main()
