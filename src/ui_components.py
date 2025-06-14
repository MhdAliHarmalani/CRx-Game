"""UI components for the CRx game."""

import pygame
from typing import Tuple, Optional
from .constants import (
    BUTTON_COLOR,
    BUTTON_HEIGHT,
    BUTTON_HOVER_COLOR,
    BUTTON_WIDTH,
    UI_FONT_SIZE,
    UI_PADDING,
    UI_TEXT_COLOR,
)


class ResponsiveButton:
    """A responsive button that scales with the UI."""

    def __init__(
        self,
        x: int,
        y: int,
        text: str,
        width: int = BUTTON_WIDTH,
        height: int = BUTTON_HEIGHT,
    ):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.is_hovered = False
        self.is_pressed = False
        self.font = pygame.font.Font(None, UI_FONT_SIZE)

        self.update_rect()

    def update_rect(self) -> None:
        """Update the button rectangle."""
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle mouse events for the button."""
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.is_pressed = True
                return True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.is_pressed = False
        return False

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the button on the screen."""
        # Choose color based on state
        if self.is_pressed:
            color = (50, 50, 60)
        elif self.is_hovered:
            color = BUTTON_HOVER_COLOR
        else:
            color = BUTTON_COLOR

        # Draw button background
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, UI_TEXT_COLOR, self.rect, 1)

        # Draw text
        text_surface = self.font.render(self.text, True, UI_TEXT_COLOR)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)


class GameUI:
    """Responsive UI manager for the game."""

    def __init__(self, window_size: Tuple[int, int], num_players: int):
        self.window_size = window_size
        self.num_players = num_players
        self.font = pygame.font.Font(None, UI_FONT_SIZE + 8)
        self.small_font = pygame.font.Font(None, UI_FONT_SIZE)

        # Calculate responsive positions
        self.setup_ui_elements()

    def setup_ui_elements(self) -> None:
        """Setup UI elements based on window size."""
        # Control buttons in top-right corner
        button_margin = UI_PADDING
        button_y = button_margin

        # Reset button
        self.reset_button = ResponsiveButton(
            self.window_size[0] - BUTTON_WIDTH - button_margin,
            button_y,
            "Reset",
        )

        # Close button
        self.close_button = ResponsiveButton(
            self.window_size[0] - (BUTTON_WIDTH * 2) - (button_margin * 2),
            button_y,
            "Close",
        )

    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        """Handle UI events and return action if any."""
        if self.reset_button.handle_event(event):
            return "reset"
        elif self.close_button.handle_event(event):
            return "close"
        return None

    def draw_player_indicator(
        self, screen: pygame.Surface, current_player: int
    ) -> None:
        """Draw the current player indicator."""
        from .constants import PLAYER_COLORS

        # Player indicator in top-left
        player_text = f"Player {current_player + 1}'s Turn"
        text_surface = self.font.render(player_text, True, UI_TEXT_COLOR)

        # Background rectangle
        text_rect = text_surface.get_rect()
        padding = UI_PADDING
        bg_rect = pygame.Rect(
            padding,
            padding,
            text_rect.width + padding * 2,
            text_rect.height + padding * 2,
        )

        # Draw with player color
        pygame.draw.rect(screen, PLAYER_COLORS[current_player], bg_rect)
        pygame.draw.rect(screen, UI_TEXT_COLOR, bg_rect, 2)

        # Center text in rectangle
        text_rect.center = bg_rect.center
        screen.blit(text_surface, text_rect)

    def draw_game_info(self, screen: pygame.Surface) -> None:
        """Draw game information."""
        # Game info in bottom-left corner
        info_text = f"Players: {self.num_players}"
        text_surface = self.small_font.render(info_text, True, UI_TEXT_COLOR)

        y_pos = self.window_size[1] - text_surface.get_height() - UI_PADDING
        screen.blit(text_surface, (UI_PADDING, y_pos))

    def draw_controls_info(self, screen: pygame.Surface) -> None:
        """Draw control instructions."""
        # Control info in bottom-right corner
        controls = [
            "Click cells to add orbs",
            "Reach critical mass to explode",
        ]

        for i, control in enumerate(controls):
            text_surface = self.small_font.render(
                control,
                True,
                (180, 180, 180),
            )
            x_pos = self.window_size[0] - text_surface.get_width() - UI_PADDING
            y_pos = (
                self.window_size[1]
                - (len(controls) - i) * (text_surface.get_height() + 2)
                - UI_PADDING
            )
            screen.blit(text_surface, (x_pos, y_pos))

    def draw(self, screen: pygame.Surface, current_player: int) -> None:
        """Draw all UI elements."""
        self.draw_player_indicator(screen, current_player)
        self.draw_game_info(screen)
        self.draw_controls_info(screen)

        # Draw buttons
        self.reset_button.draw(screen)
        self.close_button.draw(screen)
