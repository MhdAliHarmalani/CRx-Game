"""Game class implementation for the CRx game."""

from typing import List, Optional
import pygame

from .cell import Cell
from .animations import Animation, ExplosionAnimation, OrbAnimation
from .constants import (
    ANIMATION_SPEED,
    BACKGROUND_COLORS,
    CELL_SIZE,
    FPS,
    GRID_LINE_COLOR,
    GRID_SIZE,
    WINDOW_SIZE,
)


class Game:
    """Main game class for CRx."""

    def __init__(self, num_players: int) -> None:
        """Initialize the game.

        Args:
            num_players: Number of players in the game
        """
        self.num_players = num_players
        self.current_player = 0
        self.grid = [
            [Cell(row, col) for col in range(GRID_SIZE)]
            for row in range(GRID_SIZE)  # noqa: E501
        ]
        self.screen = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption("CRx Game")
        self.clock = pygame.time.Clock()

        # Calculate grid offset to center it
        self.grid_offset_x = (WINDOW_SIZE[0] - (GRID_SIZE * CELL_SIZE)) // 2
        self.grid_offset_y = (WINDOW_SIZE[1] - (GRID_SIZE * CELL_SIZE)) // 2

        # Animation system
        self.animations: List[Animation] = []
        self.last_time = pygame.time.get_ticks()
        self.is_animating = False

        # UI elements
        self.font = pygame.font.Font(None, 36)
        self.hover_cell = None

    def handle_click(self, pos: tuple[int, int]) -> bool:
        """Handle a click event."""
        if self.is_animating:
            return False

        # Convert screen coordinates to grid coordinates
        grid_x = (pos[0] - self.grid_offset_x) // CELL_SIZE
        grid_y = (pos[1] - self.grid_offset_y) // CELL_SIZE

        if 0 <= grid_y < GRID_SIZE and 0 <= grid_x < GRID_SIZE:
            cell = self.grid[grid_y][grid_x]
            if not cell.orbs or cell.orbs[0] == self.current_player:
                # Add orb and handle explosion if needed
                if cell.add_orb(self.current_player):
                    self.handle_explosion(grid_y, grid_x)
                # Only switch player if the move was valid
                self.current_player = (
                    self.current_player + 1
                ) % self.num_players  # noqa: E501
                return True
        return False

    def handle_explosion(self, row: int, col: int) -> None:
        """Handle an explosion at the specified cell."""
        cell = self.grid[row][col]
        if len(cell.orbs) >= cell.critical_mass:
            current_player = self.current_player
            cell.orbs = []
            adjacent_cells = cell.explode()

            # Create explosion animation
            self.animations.append(
                ExplosionAnimation(col, row, current_player, adjacent_cells)
            )

            # Create orb movement animations
            for new_row, new_col in adjacent_cells:
                if 0 <= new_row < GRID_SIZE and 0 <= new_col < GRID_SIZE:
                    target_cell = self.grid[new_row][new_col]
                    self.animations.append(
                        OrbAnimation(
                            (col, row),
                            (new_col, new_row),
                            current_player,
                        )
                    )
                    target_cell.add_orb(current_player)
                    if len(target_cell.orbs) >= target_cell.critical_mass:
                        self.handle_explosion(new_row, new_col)

    def check_win_condition(self) -> Optional[int]:
        """Check if any player has won or lost.

        Returns:
            int: The winning player's index if someone has won,
                 -1 if a player has lost all orbs,
                 None if the game continues
        """
        # First check if any player has lost all orbs
        for player in range(self.num_players):
            player_has_orbs = False
            for row in self.grid:
                for cell in row:
                    if cell.orbs and all(owner == player for owner in cell.orbs):  # noqa: E501
                        player_has_orbs = True
                        break
                if player_has_orbs:
                    break
            if not player_has_orbs:
                # Only return loss if both players have made at least one move
                if self.current_player != player:  # If it's not the first move
                    return -1  # A player has lost all orbs

        # Then check if any player has won by controlling the entire grid
        for player in range(self.num_players):
            if all(
                cell.orbs and all(owner == player for owner in cell.orbs)
                for row in self.grid
                for cell in row
            ):
                return player
        return None

    def update_animations(self, dt: float) -> None:
        """Update all active animations."""
        self.is_animating = len(self.animations) > 0
        for animation in self.animations[:]:
            animation.update(dt * ANIMATION_SPEED)
            if animation.is_finished:
                self.animations.remove(animation)

    def update_hover(self, pos: tuple[int, int]) -> None:
        """Update hover state for cells."""
        # Reset all cells' hover state
        for row in self.grid:
            for cell in row:
                cell.hover = False

        # Convert screen coordinates to grid coordinates
        grid_x = (pos[0] - self.grid_offset_x) // CELL_SIZE
        grid_y = (pos[1] - self.grid_offset_y) // CELL_SIZE

        # Set hover state for the cell under the mouse
        if 0 <= grid_y < GRID_SIZE and 0 <= grid_x < GRID_SIZE:
            self.grid[grid_y][grid_x].hover = True

    def draw_grid(self) -> None:
        """Draw the game grid and all cells."""
        # Fill background with current player's color
        self.screen.fill(BACKGROUND_COLORS[self.current_player])

        # Draw grid lines with anti-aliasing
        for i in range(GRID_SIZE + 1):
            # Vertical lines
            pygame.draw.line(
                self.screen,
                GRID_LINE_COLOR,
                (self.grid_offset_x + i * CELL_SIZE, self.grid_offset_y),
                (
                    self.grid_offset_x + i * CELL_SIZE,
                    self.grid_offset_y + GRID_SIZE * CELL_SIZE,
                ),
                2,
            )
            # Horizontal lines
            pygame.draw.line(
                self.screen,
                GRID_LINE_COLOR,
                (self.grid_offset_x, self.grid_offset_y + i * CELL_SIZE),
                (
                    self.grid_offset_x + GRID_SIZE * CELL_SIZE,
                    self.grid_offset_y + i * CELL_SIZE,
                ),
                2,
            )

        # Draw cells
        for row in self.grid:
            for cell in row:
                cell.draw(self.screen, self.grid_offset_x, self.grid_offset_y)

        # Draw active animations
        for animation in self.animations:
            animation.draw(self.screen)

    def run(self) -> None:
        """Run the main game loop."""
        running = True
        while running:
            current_time = pygame.time.get_ticks()
            dt = (current_time - self.last_time) / 1000.0  # Convert to seconds
            self.last_time = current_time

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(pygame.mouse.get_pos())
                    # Check win/lose condition after each move
                    result = self.check_win_condition()
                    if result is not None:
                        if result == -1:
                            print("Game Over! A player has lost all orbs!")
                        else:
                            print(f"Player {result} wins!")
                        running = False
                elif event.type == pygame.MOUSEMOTION:
                    self.update_hover(pygame.mouse.get_pos())

            self.update_animations(dt)
            self.draw_grid()
            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
