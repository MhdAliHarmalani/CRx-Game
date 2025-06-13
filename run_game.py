"""Entry point script for running the CRx game."""

import pygame
from src.game import Game

if __name__ == "__main__":
    pygame.init()
    game = Game(num_players=2)
    game.run()
