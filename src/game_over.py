"""Game over screen for the CRx game."""

import pygame
from typing import Optional
from .constants import WINDOW_SIZE, PLAYER_COLORS


class GameOverScreen:
    """Game over screen with play again option."""
    
    def __init__(self, winner: int, num_players: int):
        self.winner = winner
        self.num_players = num_players
        self.screen = pygame.display.get_surface()
        
        # Colors and fonts
        self.bg_color = (30, 30, 40)
        self.title_font = pygame.font.Font(None, 64)
        self.subtitle_font = pygame.font.Font(None, 32)
        self.button_font = pygame.font.Font(None, 36)
        
        # Button setup
        self.button_width = 200
        self.button_height = 60
        self.button_spacing = 30
        
        center_x = WINDOW_SIZE[0] // 2 - self.button_width // 2
        start_y = WINDOW_SIZE[1] // 2 + 50
        
        self.play_again_rect = pygame.Rect(
            center_x, start_y, self.button_width, self.button_height
        )
        self.menu_rect = pygame.Rect(
            center_x, start_y + self.button_height + self.button_spacing,
            self.button_width, self.button_height
        )
        self.quit_rect = pygame.Rect(
            center_x, start_y + 2 * (self.button_height + self.button_spacing),
            self.button_width, self.button_height
        )
        
        self.play_again_hovered = False
        self.menu_hovered = False
        self.quit_hovered = False
        
        self.clock = pygame.time.Clock()
    
    def draw_background(self) -> None:
        """Draw the background with overlay."""
        # Semi-transparent dark overlay
        overlay = pygame.Surface(WINDOW_SIZE)
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
    
    def draw_winner_message(self) -> None:
        """Draw the winner message."""
        title_text = f"Player {self.winner + 1} Wins!"
        subtitle_text = "Congratulations!"
        color = PLAYER_COLORS[self.winner]
        
        # Title
        title_surface = self.title_font.render(title_text, True, color)
        title_rect = title_surface.get_rect(
            center=(WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2 - 100)
        )
        self.screen.blit(title_surface, title_rect)
        
        # Subtitle
        subtitle_surface = self.subtitle_font.render(
            subtitle_text, True, (255, 255, 255)
        )
        subtitle_rect = subtitle_surface.get_rect(
            center=(WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2 - 50)
        )
        self.screen.blit(subtitle_surface, subtitle_rect)
    
    def draw_button(self, rect: pygame.Rect, text: str,
                    is_hovered: bool) -> None:
        """Draw a button with hover effect."""
        color = (100, 100, 100) if is_hovered else (70, 70, 70)
        pygame.draw.rect(self.screen, color, rect)
        pygame.draw.rect(self.screen, (200, 200, 200), rect, 2)
        
        # Draw text
        text_surface = self.button_font.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=rect.center)
        self.screen.blit(text_surface, text_rect)
    
    def draw_buttons(self) -> None:
        """Draw all buttons."""
        self.draw_button(self.play_again_rect, "Play Again", 
                        self.play_again_hovered)
        self.draw_button(self.menu_rect, "Main Menu", self.menu_hovered)
        self.draw_button(self.quit_rect, "Quit", self.quit_hovered)
    
    def handle_mouse_motion(self, pos: tuple[int, int]) -> None:
        """Handle mouse motion for hover effects."""
        self.play_again_hovered = self.play_again_rect.collidepoint(pos)
        self.menu_hovered = self.menu_rect.collidepoint(pos)
        self.quit_hovered = self.quit_rect.collidepoint(pos)
    
    def handle_click(self, pos: tuple[int, int]) -> Optional[str]:
        """Handle mouse clicks on buttons."""
        if self.play_again_rect.collidepoint(pos):
            return "play_again"
        elif self.menu_rect.collidepoint(pos):
            return "menu"
        elif self.quit_rect.collidepoint(pos):
            return "quit"
        return None
    
    def run(self) -> str:
        """Run the game over screen and return the user's choice."""
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                elif event.type == pygame.MOUSEMOTION:
                    self.handle_mouse_motion(event.pos)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    result = self.handle_click(event.pos)
                    if result:
                        return result
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return "menu"
                    elif event.key == pygame.K_RETURN:
                        return "play_again"
            
            # Draw everything
            self.draw_background()
            self.draw_winner_message()
            self.draw_buttons()
            
            pygame.display.flip()
            self.clock.tick(60)
        
        return "quit" 