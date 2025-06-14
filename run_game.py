"""Entry point script for running the CRx game."""

import pygame
import sys
import argparse
from src.menu import Menu
from src.game import Game
from src.game_over import GameOverScreen


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='CRx Chain Reaction Game')
    parser.add_argument('--debug', action='store_true',
                        help='Enable debug logging to file')
    return parser.parse_args()


def main():
    """Main game loop handling menu, game, and game over screens."""
    args = parse_arguments()
    debug_mode = args.debug
    
    if debug_mode:
        print("Debug mode enabled - logs will be saved to logs/ directory")
    
    pygame.init()
    
    while True:
        # Show menu
        menu = Menu()
        num_players = menu.run()
        
        if not num_players:
            pygame.quit()
            sys.exit()
        
        # Play the game with reset functionality
        while True:
            game = Game(num_players=num_players, debug=debug_mode)
            result = game.run()
            
            if result == "close":
                break  # Go back to main menu
            elif result == "reset":
                continue  # Reset and play again with same settings
            elif result is None:
                # Player quit during game
                pygame.quit()
                sys.exit()
            else:
                # Game ended with a winner
                winner = result
                
                # Show game over screen
                game_over = GameOverScreen(winner, num_players)
                choice = game_over.run()
                
                if choice == "quit":
                    pygame.quit()
                    sys.exit()
                elif choice == "menu":
                    break  # Go back to menu
                elif choice == "play_again":
                    continue  # Play again with same settings


if __name__ == "__main__":
    main()
