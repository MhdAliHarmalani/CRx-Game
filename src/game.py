"""Game class implementation for the CRx game."""

from typing import List, Optional, Dict
import pygame

from .cell import Cell
from .animations import (
    Animation,
    ExplosionAnimation,
    OrbAnimation,
    AtomOrbAnimation,
)
from .constants import (
    ANIMATION_SPEED,
    BACKGROUND_COLORS,
    CELL_SIZE,
    FPS,
    GRID_LINE_COLOR,
    GRID_SIZE,
    WINDOW_SIZE,
)
from .ui_components import GameUI


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
            [Cell(row, col) for col in range(GRID_SIZE)] for row in range(GRID_SIZE)  # noqa: E501
        ]
        self.screen = pygame.display.set_mode(WINDOW_SIZE, pygame.RESIZABLE)
        pygame.display.set_caption("CRx Game")
        self.clock = pygame.time.Clock()

        # Calculate grid offset to center it
        self.grid_offset_x = (WINDOW_SIZE[0] - (GRID_SIZE * CELL_SIZE)) // 2
        self.grid_offset_y = (WINDOW_SIZE[1] - (GRID_SIZE * CELL_SIZE)) // 2

        # Animation system
        self.animations: List[Animation] = []
        self.atom_animations: Dict[tuple[int, int], AtomOrbAnimation] = {}
        self.last_time = pygame.time.get_ticks()
        self.is_animating = False

        # Explosion queue to prevent infinite recursion
        self.explosion_queue: List[tuple[int, int]] = []
        self.processing_explosions = False

        # UI elements
        self.font = pygame.font.Font(None, 36)
        self.hover_cell = None
        self.ui = GameUI(WINDOW_SIZE, num_players)
        
        # Game state
        self.game_should_reset = False
        self.game_should_close = False

    def handle_click(self, pos: tuple[int, int]) -> bool:
        """Handle a click event."""
        if self.is_animating or self.processing_explosions:
            return False

        # Convert screen coordinates to grid coordinates
        grid_x = (pos[0] - self.grid_offset_x) // CELL_SIZE
        grid_y = (pos[1] - self.grid_offset_y) // CELL_SIZE

        if 0 <= grid_y < GRID_SIZE and 0 <= grid_x < GRID_SIZE:
            cell = self.grid[grid_y][grid_x]
            if not cell.orbs or cell.orbs[0] == self.current_player:
                # Add orb and handle explosion if needed
                if cell.add_orb(self.current_player):
                    self.start_explosion_chain(grid_y, grid_x)
                else:
                    # Create or update atom animation for the cell
                    # Use the cell's actual owner, not current_player
                    cell_owner = (
                        cell.owner
                        if cell.owner is not None
                        else self.current_player  # noqa: E501
                    )
                    if (grid_y, grid_x) in self.atom_animations:
                        # Update existing animation with new orb count and correct player  # noqa: E501
                        animation = self.atom_animations[(grid_y, grid_x)]
                        animation.update_orb_count(len(cell.orbs))
                        animation.player = cell_owner  # Update player color
                    else:
                        # Create new animation with correct player
                        self.atom_animations[
                            (
                                grid_y,
                                grid_x,
                            )
                        ] = AtomOrbAnimation(
                            self.grid_offset_x + grid_x * CELL_SIZE,
                            self.grid_offset_y + grid_y * CELL_SIZE,
                            cell_owner,
                            len(cell.orbs),
                        )
                # Only switch player if the move was valid
                self.current_player = (self.current_player + 1) % self.num_players  # noqa: E501
                return True
        return False

    def start_explosion_chain(self, row: int, col: int) -> None:
        """Start a chain of explosions using a queue to prevent recursion."""
        self.processing_explosions = True
        self.explosion_queue = [(row, col)]
        # Don't process all explosions at once - let update_explosions handle them  # noqa: E501

    def update_explosions(self) -> None:
        """Process one explosion per frame to prevent freezing."""
        if self.explosion_queue:
            current_row, current_col = self.explosion_queue.pop(0)
            self.handle_single_explosion(current_row, current_col)
        elif self.processing_explosions:
            # Queue is empty, stop processing explosions
            self.processing_explosions = False

    def handle_single_explosion(self, row: int, col: int) -> None:
        """Handle a single explosion without recursion."""
        cell = self.grid[row][col]
        if len(cell.orbs) >= cell.critical_mass:
            # Store the exploding player before clearing the cell
            exploding_player = cell.owner
            adjacent_cells = cell.explode()

            # Remove atom animation for exploded cell
            if (row, col) in self.atom_animations:
                del self.atom_animations[(row, col)]

            # Create explosion animation
            self.animations.append(
                ExplosionAnimation(col, row, exploding_player, adjacent_cells)
            )

            # Create orb movement animations and add orbs to adjacent cells
            for new_row, new_col in adjacent_cells:
                if 0 <= new_row < GRID_SIZE and 0 <= new_col < GRID_SIZE:
                    target_cell = self.grid[new_row][new_col]
                    self.animations.append(
                        OrbAnimation(
                            (col, row),
                            (new_col, new_row),
                            exploding_player,
                        )
                    )
                    target_cell.add_orb(exploding_player)
                    # Create or update atom animation for the new cell
                    # Use the target cell's actual owner
                    cell_owner = target_cell.owner
                    if (new_row, new_col) in self.atom_animations:
                        animation = self.atom_animations[(new_row, new_col)]
                        animation.update_orb_count(len(target_cell.orbs))
                        animation.player = cell_owner  # Update player color
                    else:
                        self.atom_animations[
                            (
                                new_row,
                                new_col,
                            )
                        ] = AtomOrbAnimation(
                            self.grid_offset_x + new_col * CELL_SIZE,
                            self.grid_offset_y + new_row * CELL_SIZE,
                            cell_owner,
                            len(target_cell.orbs),
                        )
                    # Add to explosion queue if it will explode
                    if len(target_cell.orbs) >= target_cell.critical_mass:
                        if (new_row, new_col) not in self.explosion_queue:
                            self.explosion_queue.append((new_row, new_col))

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
                    if cell.orbs and all(
                        owner == player for owner in cell.orbs
                    ):  # noqa: E501
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

        # Update atom animations
        for animation in self.atom_animations.values():
            animation.update(dt * ANIMATION_SPEED)

        # Process explosions one per frame
        self.update_explosions()

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
                # Don't show orbs if there's an atom animation for this cell
                show_orbs = (cell.row, cell.col) not in self.atom_animations
                cell.draw(
                    self.screen,
                    self.grid_offset_x,
                    self.grid_offset_y,
                    show_orbs,
                )

        # Draw active animations
        for animation in self.animations:
            animation.draw(self.screen)

        # Draw atom animations
        for animation in self.atom_animations.values():
            animation.draw(self.screen)
        
        # Draw responsive UI
        self.ui.draw(self.screen, self.current_player)
    
    def reset_game(self) -> None:
        """Reset the game to initial state."""
        self.current_player = 0
        self.grid = [
            [Cell(row, col) for col in range(GRID_SIZE)] 
            for row in range(GRID_SIZE)
        ]
        self.animations.clear()
        self.atom_animations.clear()
        self.explosion_queue.clear()
        self.processing_explosions = False
        self.is_animating = False
        self.game_should_reset = False
        self.game_should_close = False

    def run(self) -> Optional[int]:
        """Run the main game loop."""
        running = True
        winner = None
        
        while running:
            current_time = pygame.time.get_ticks()
            dt = (current_time - self.last_time) / 1000.0  # Convert to seconds
            self.last_time = current_time

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                elif event.type == pygame.VIDEORESIZE:
                    # Handle window resize
                    new_size = (max(event.w, 600), max(event.h, 600))
                    self.screen = pygame.display.set_mode(
                        new_size, pygame.RESIZABLE
                    )
                    self.ui = GameUI(new_size, self.num_players)
                
                # Handle UI events first
                ui_action = self.ui.handle_event(event)
                if ui_action == "reset":
                    self.game_should_reset = True
                    running = False
                elif ui_action == "close":
                    self.game_should_close = True
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Only handle game clicks if not clicking UI
                    pos = event.pos
                    reset_clicked = self.ui.reset_button.rect.collidepoint(pos)
                    close_clicked = self.ui.close_button.rect.collidepoint(pos)
                    
                    if not reset_clicked and not close_clicked:
                        self.handle_click(pygame.mouse.get_pos())
                        # Check win/lose condition after each move
                        result = self.check_win_condition()
                        if result is not None:
                            winner = result
                            running = False
                elif event.type == pygame.MOUSEMOTION:
                    self.update_hover(pygame.mouse.get_pos())

            self.update_animations(dt)
            self.draw_grid()
            pygame.display.flip()
            self.clock.tick(FPS)

        # Return appropriate result based on game state
        if self.game_should_reset:
            return "reset"
        elif self.game_should_close:
            return "close"
        return winner
