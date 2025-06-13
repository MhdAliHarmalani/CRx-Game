"""Cell class for the game grid."""

from typing import List, Optional, Tuple

import pygame
import math

from .constants import CELL_SIZE, PLAYER_COLORS


class Cell:
    """Represents a cell in the game grid.

    Each cell can contain orbs from different players and has a critical mass
    that determines when it explodes.
    """

    def __init__(self, row: int, col: int) -> None:
        """Initialize a cell.

        Args:
            row: Row index in the grid
            col: Column index in the grid
        """
        self.row = row
        self.col = col
        self.orbs: List[int] = []
        self.owner: Optional[int] = None
        self.critical_mass = self._calculate_critical_mass()
        self.hover = False

    def _calculate_critical_mass(self) -> int:
        """Calculate the critical mass for this cell based on its position.

        Returns:
            int: Critical mass value (2 for corners, 3 for edges, 4 for inner)
        """
        is_corner = self.row in (0, 5) and self.col in (0, 5)
        is_edge = self.row in (0, 5) or self.col in (0, 5)

        if is_corner:
            return 2
        if is_edge:
            return 3
        return 4

    def add_orb(self, player: int) -> bool:
        """Add an orb to the cell.

        Args:
            player: Player index (0 or 1)

        Returns:
            bool: True if the cell will explode, False otherwise
        """
        if not self.orbs or self.owner == player:
            self.orbs.append(player)
            self.owner = player
        else:
            # Convert orbs to the new player's color
            self.orbs = [player] * len(self.orbs)
            self.owner = player

        return len(self.orbs) >= self.critical_mass

    def explode(self) -> List[Tuple[int, int]]:
        """Handle cell explosion.

        Returns:
            List[Tuple[int, int]]: List of adjacent cell coordinates
        """
        self.orbs = []
        self.owner = None

        # Return coordinates of adjacent cells
        return [
            (self.row + 1, self.col),  # Down
            (self.row - 1, self.col),  # Up
            (self.row, self.col + 1),  # Right
            (self.row, self.col - 1),  # Left
        ]

    def draw(
        self,
        screen: pygame.Surface,
        offset_x: int,
        offset_y: int,
    ) -> None:
        """Draw the cell and its orbs.

        Args:
            screen: Pygame surface to draw on
            offset_x: X offset of the grid
            offset_y: Y offset of the grid
        """
        # Calculate cell position
        cell_x = offset_x + self.col * CELL_SIZE
        cell_y = offset_y + self.row * CELL_SIZE

        # Draw cell background with hover effect
        bg_color = (220, 220, 220) if self.hover else (200, 200, 200)
        pygame.draw.rect(
            screen,
            bg_color,
            (
                cell_x,
                cell_y,
                CELL_SIZE,
                CELL_SIZE,
            ),
        )

        # Draw cell border with gradient effect
        border_color = (120, 120, 120) if self.hover else (100, 100, 100)
        pygame.draw.rect(
            screen,
            border_color,
            (cell_x, cell_y, CELL_SIZE, CELL_SIZE),
            2,
        )

        # Draw critical mass indicator
        if not self.orbs:
            font = pygame.font.Font(None, 24)
            text = font.render(str(self.critical_mass), True, (150, 150, 150))
            text_rect = text.get_rect(
                center=(cell_x + CELL_SIZE // 2, cell_y + CELL_SIZE // 2),
            )
            screen.blit(text, text_rect)

        # Draw orbs with improved visuals
        if self.orbs:
            # Calculate orb size based on cell size and number of orbs
            orb_radius = min(CELL_SIZE // 3, CELL_SIZE // (2 * len(self.orbs)))
            spacing = CELL_SIZE // 3

            for i, player in enumerate(self.orbs):
                angle = (2 * math.pi * i) / len(self.orbs)
                x = cell_x + CELL_SIZE // 2 + int(spacing * math.cos(angle))
                y = cell_y + CELL_SIZE // 2 + int(spacing * math.sin(angle))

                # Draw orb shadow
                shadow_offset = 2
                pygame.draw.circle(
                    screen,
                    (0, 0, 0, 128),
                    (x + shadow_offset, y + shadow_offset),
                    orb_radius,
                )

                # Draw orb with gradient effect
                color = PLAYER_COLORS[player]
                pygame.draw.circle(screen, color, (x, y), orb_radius)

                # Draw orb highlight
                highlight_color = tuple(min(c + 50, 255) for c in color)
                pygame.draw.circle(
                    screen,
                    highlight_color,
                    (x - orb_radius // 3, y - orb_radius // 3),
                    orb_radius // 3,
                )
