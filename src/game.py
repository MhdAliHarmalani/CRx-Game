"""Game class implementation for the CRx game."""

import datetime
import os
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

    def __init__(self, num_players: int, debug: bool = False) -> None:
        """Initialize the game.

        Args:
            num_players: Number of players in the game
            debug: Enable debug logging to file
        """
        self.num_players = num_players
        self.debug = debug
        self.move_count = 0

        # Setup debug logging
        if self.debug:
            self.setup_debug_logging()

        self.current_player = 0
        self.grid = [
            [Cell(row, col) for col in range(GRID_SIZE)]
            for row in range(GRID_SIZE)  # noqa: E501
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
        self.post_explosion_winner = None
        self.game_started = False  # Track if any player has made a move
        self.players_who_played = set()  # Track which players have made moves

        self.debug_log(
            "Game initialized",
            {
                "num_players": num_players,
                "debug_mode": debug,
                "grid_size": GRID_SIZE,
            },
        )

    def setup_debug_logging(self) -> None:
        """Setup debug logging to file."""
        # Create logs directory if it doesn't exist
        if not os.path.exists("logs"):
            os.makedirs("logs")

        # Create log file with timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_filename = f"logs/crx_game_{timestamp}.log"

        # Write initial log header
        with open(self.log_filename, "w") as f:
            f.write(f"CRx Game Debug Log - {datetime.datetime.now()}\n")
            f.write("=" * 50 + "\n\n")

    def debug_log(self, message: str, data: dict = None) -> None:
        """Log debug message to file if debug mode is enabled."""
        if not self.debug:
            return

        timestamp = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
        log_entry = f"[{timestamp}] {message}"

        if data:
            log_entry += f" - Data: {data}"

        log_entry += "\n"

        # Write to file
        try:
            with open(self.log_filename, "a") as f:
                f.write(log_entry)
        except Exception as e:
            print(f"Debug logging error: {e}")

    def log_game_state(self) -> None:
        """Log current game state."""
        if not self.debug:
            return

        # Count orbs for each player
        player_orbs = {}
        for player in range(self.num_players):
            count = 0
            for row in self.grid:
                for cell in row:
                    if cell.orbs and cell.owner == player:
                        count += len(cell.orbs)
            player_orbs[f"player_{player}"] = count

        self.debug_log(
            "Game state",
            {
                "current_player": self.current_player,
                "move_count": self.move_count,
                "players_who_played": list(self.players_who_played),
                "game_started": self.game_started,
                "is_animating": self.is_animating,
                "processing_explosions": self.processing_explosions,
                "orb_counts": player_orbs,
            },
        )

    def handle_click(self, pos: tuple[int, int]) -> bool:
        """Handle a click event."""
        if self.is_animating or self.processing_explosions:
            self.debug_log("Click ignored - animations/explosions in progress")
            return False

        # Convert screen coordinates to grid coordinates
        grid_x = (pos[0] - self.grid_offset_x) // CELL_SIZE
        grid_y = (pos[1] - self.grid_offset_y) // CELL_SIZE

        self.debug_log(
            "Click detected",
            {
                "screen_pos": pos,
                "grid_pos": (grid_x, grid_y),
                "current_player": self.current_player,
            },
        )

        if 0 <= grid_y < GRID_SIZE and 0 <= grid_x < GRID_SIZE:
            cell = self.grid[grid_y][grid_x]

            self.debug_log(
                "Cell state before move",
                {
                    "position": (grid_y, grid_x),
                    "orb_count": len(cell.orbs),
                    "owner": cell.owner,
                    "critical_mass": cell.critical_mass,
                },
            )

            if not cell.orbs or cell.orbs[0] == self.current_player:
                # Mark game as started when first move is made
                if not self.game_started:
                    self.game_started = True
                    self.debug_log("Game started!")

                # Track that this player has played
                self.players_who_played.add(self.current_player)
                self.move_count += 1

                self.debug_log(
                    "Valid move",
                    {
                        "player": self.current_player,
                        "move_number": self.move_count,
                        "players_who_played": list(self.players_who_played),
                    },
                )

                # Add orb and handle explosion if needed
                if cell.add_orb(self.current_player):
                    self.debug_log(
                        "Explosion triggered",
                        {
                            "position": (grid_y, grid_x),
                            "orb_count_after_add": len(cell.orbs),
                            "critical_mass": cell.critical_mass,
                        },
                    )
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
                old_player = self.current_player
                self.current_player = (
                    self.current_player + 1
                ) % self.num_players  # noqa: E501

                self.debug_log(
                    "Turn ended",
                    {
                        "previous_player": old_player,
                        "new_current_player": self.current_player,
                    },
                )

                # Log game state after move
                self.log_game_state()

                return True
            else:
                self.debug_log(
                    "Invalid move - cell belongs to different player",
                    {
                        "cell_owner": cell.orbs[0] if cell.orbs else None,
                        "current_player": self.current_player,
                    },
                )
        else:
            self.debug_log(
                "Click outside grid",
                {
                    "grid_bounds": f"0-{GRID_SIZE-1}",
                    "attempted_pos": (grid_x, grid_y),
                },
            )
        return False

    def start_explosion_chain(self, row: int, col: int) -> None:
        """Start a chain of explosions using a queue to prevent recursion."""
        self.processing_explosions = True
        self.explosion_queue = [(row, col)]
        self.debug_log(
            "Explosion chain started",
            {
                "initial_position": (row, col),
                "queue_size": len(self.explosion_queue),
            },
        )
        # Don't process all explosions at once - let update_explosions handle them  # noqa: E501

    def update_explosions(self) -> None:
        """Process one explosion per frame to prevent freezing."""
        if self.explosion_queue:
            current_row, current_col = self.explosion_queue.pop(0)
            self.debug_log(
                "Processing explosion",
                {
                    "position": (current_row, current_col),
                    "remaining_in_queue": len(self.explosion_queue),
                },
            )
            self.handle_single_explosion(current_row, current_col)
        elif self.processing_explosions:
            # Queue is empty, stop processing explosions
            self.processing_explosions = False
            self.debug_log("Explosion chain completed")
            # Check win condition after all explosions are complete
            self.check_post_explosion_win()

    def handle_single_explosion(self, row: int, col: int) -> None:
        """Handle a single explosion without recursion."""
        cell = self.grid[row][col]
        if len(cell.orbs) >= cell.critical_mass:
            # Store the exploding player before clearing the cell
            exploding_player = cell.owner
            adjacent_cells = cell.explode()

            self.debug_log(
                "Cell exploded",
                {
                    "position": (row, col),
                    "exploding_player": exploding_player,
                    "orb_count_before": len(cell.orbs),
                    "critical_mass": cell.critical_mass,
                    "adjacent_cells": adjacent_cells,
                },
            )

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

                    old_orb_count = len(target_cell.orbs)
                    old_owner = target_cell.owner

                    self.animations.append(
                        OrbAnimation(
                            (col, row),
                            (new_col, new_row),
                            exploding_player,
                        )
                    )
                    target_cell.add_orb(exploding_player)

                    self.debug_log(
                        "Orb transferred",
                        {
                            "from": (row, col),
                            "to": (new_row, new_col),
                            "player": exploding_player,
                            "target_orbs_before": old_orb_count,
                            "target_orbs_after": len(target_cell.orbs),
                            "target_owner_before": old_owner,
                            "target_owner_after": target_cell.owner,
                        },
                    )

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
                            self.debug_log(
                                "Chain explosion queued",
                                {
                                    "position": (new_row, new_col),
                                    "orb_count": len(target_cell.orbs),
                                    "critical_mass": target_cell.critical_mass,
                                },
                            )

    def check_win_condition(self) -> Optional[int]:
        """Check if any player has won or lost.

        Returns:
            int: The winning player's index if someone has won,
                 None if the game continues
        """
        # Don't check for wins until the game has actually started
        if not self.game_started:
            self.debug_log("Win condition check skipped - game not started")
            return None

        self.debug_log(
            "Checking win condition",
            {
                "players_who_played": list(self.players_who_played),
                "num_players": self.num_players,
            },
        )

        # Count how many players have orbs on the board
        players_with_orbs = set()

        # Check which players have orbs
        for player in range(self.num_players):
            has_orbs = False
            for row in self.grid:
                for cell in row:
                    if cell.orbs and cell.owner == player:
                        has_orbs = True
                        players_with_orbs.add(player)
                        break
                if has_orbs:
                    break

        self.debug_log(
            "Players with orbs",
            {
                "players_with_orbs": list(players_with_orbs),
                "count": len(players_with_orbs),
            },
        )

        # If only one player has orbs remaining, they win
        # But ONLY if ALL players have had at least one turn to play
        all_players_played = len(self.players_who_played) == self.num_players
        if len(players_with_orbs) == 1 and all_players_played:
            # Make sure at least one move has been made by someone
            total_orbs = sum(
                len(cell.orbs) for row in self.grid for cell in row
            )  # noqa: E501
            if total_orbs > 0:
                winner = list(players_with_orbs)[0]
                self.debug_log(
                    "WIN BY ELIMINATION",
                    {
                        "winner": winner,
                        "total_orbs": total_orbs,
                        "all_players_played": all_players_played,
                    },
                )
                return winner

        # Alternative win condition: player controls entire grid
        # This can happen even early in the game
        for player in range(self.num_players):
            if all(
                cell.orbs and cell.owner == player
                for row in self.grid
                for cell in row
                if cell.orbs  # Only check cells that have orbs
            ):
                # Make sure there are actually orbs on the board
                # AND all players have had a chance to play
                has_orbs = any(cell.orbs for row in self.grid for cell in row)
                all_played = len(self.players_who_played) == self.num_players
                if has_orbs and all_played:
                    self.debug_log(
                        "WIN BY DOMINATION",
                        {
                            "winner": player,
                            "controlled_all_cells": True,
                            "all_players_played": True,
                        },
                    )
                    return player

        self.debug_log("No win condition met - game continues")
        return None

    def check_post_explosion_win(self) -> None:
        """Check for win condition after explosions complete."""
        self.debug_log("Checking post-explosion win condition")
        result = self.check_win_condition()
        if result is not None:
            # Set a flag to indicate game should end with this winner
            self.post_explosion_winner = result
            self.debug_log(
                "Post-explosion winner detected",
                {"winner": result},
            )

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
        self.debug_log("Game reset initiated")

        self.current_player = 0
        self.move_count = 0
        self.grid = [
            [Cell(row, col) for col in range(GRID_SIZE)]
            for row in range(GRID_SIZE)  # noqa: E501
        ]
        self.animations.clear()
        self.atom_animations.clear()
        self.explosion_queue.clear()
        self.processing_explosions = False
        self.is_animating = False
        self.game_should_reset = False
        self.game_should_close = False
        self.post_explosion_winner = None
        self.game_started = False
        self.players_who_played.clear()

        self.debug_log(
            "Game reset completed",
            {
                "grid_cleared": True,
                "animations_cleared": True,
                "game_state_reset": True,
            },
        )

    def run(self) -> Optional[int]:
        """Run the main game loop."""
        self.debug_log("Starting main game loop")
        running = True
        winner = None

        while running:
            current_time = pygame.time.get_ticks()
            dt = (current_time - self.last_time) / 1000.0  # Convert to seconds
            self.last_time = current_time

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.debug_log("Game quit by user")
                    return None
                elif event.type == pygame.VIDEORESIZE:
                    # Handle window resize
                    new_size = (max(event.w, 600), max(event.h, 600))
                    self.screen = pygame.display.set_mode(
                        new_size,
                        pygame.RESIZABLE,
                    )
                    self.ui = GameUI(new_size, self.num_players)
                    self.debug_log("Window resized", {"new_size": new_size})

                # Handle UI events first
                ui_action = self.ui.handle_event(event)
                if ui_action == "reset":
                    self.debug_log("Reset button clicked")
                    self.game_should_reset = True
                    running = False
                elif ui_action == "close":
                    self.debug_log("Close button clicked")
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

            # Check for post-explosion win condition
            if self.post_explosion_winner is not None:
                self.debug_log(
                    "Post-explosion winner detected in main loop",
                    {"winner": self.post_explosion_winner},
                )
                winner = self.post_explosion_winner
                running = False

            self.draw_grid()
            pygame.display.flip()
            self.clock.tick(FPS)

        # Return appropriate result based on game state
        if self.game_should_reset:
            self.debug_log("Game ending - reset requested")
            return "reset"
        elif self.game_should_close:
            self.debug_log("Game ending - close requested")
            return "close"

        self.debug_log("Game ending - winner determined", {"winner": winner})
        return winner
