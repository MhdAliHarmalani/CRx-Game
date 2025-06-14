"""Menu system for the CRx game."""

import pygame
import sys
from typing import Optional, Tuple
from .constants import WINDOW_SIZE, PLAYER_COLORS


class Button:
    """A clickable button with hover effects."""
    
    def __init__(self, x: int, y: int, width: int, height: int, text: str, 
                 color: Tuple[int, int, int] = (70, 70, 70), 
                 hover_color: Tuple[int, int, int] = (100, 100, 100),
                 text_color: Tuple[int, int, int] = (255, 255, 255)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hovered = False
        self.font = pygame.font.Font(None, 32)
        
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the button on the screen."""
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, (200, 200, 200), self.rect, 2)
        
        # Draw text centered on button
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle mouse events for the button."""
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False


class Menu:
    """Main menu for the CRx game."""
    
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption("CRx - Chain Reaction Game")
        
        # Colors and fonts
        self.bg_color = (30, 30, 40)
        self.title_color = (255, 255, 255)
        self.subtitle_color = (200, 200, 200)
        self.title_font = pygame.font.Font(None, 72)
        self.subtitle_font = pygame.font.Font(None, 32)
        
        # Button setup
        button_width = 200
        button_height = 50
        button_spacing = 20
        start_y = WINDOW_SIZE[1] // 2 - 50
        center_x = WINDOW_SIZE[0] // 2 - button_width // 2
        
        self.buttons = [
            Button(center_x, start_y, button_width, button_height, "2 Players", 
                   PLAYER_COLORS[0], (255, 50, 50)),
            Button(center_x, start_y + button_height + button_spacing, 
                   button_width, button_height, "3 Players", 
                   (0, 150, 0), (50, 200, 50)),
            Button(center_x, start_y + 2 * (button_height + button_spacing), 
                   button_width, button_height, "4 Players", 
                   (150, 0, 150), (200, 50, 200)),
            Button(center_x, start_y + 3 * (button_height + button_spacing), 
                   button_width, button_height, "Quit", 
                   (100, 100, 100), (150, 150, 150))
        ]
        
        self.clock = pygame.time.Clock()
        
    def draw_background(self) -> None:
        """Draw the background with gradient effect."""
        # Simple gradient background
        for y in range(WINDOW_SIZE[1]):
            color = (
                30 + int(20 * y / WINDOW_SIZE[1]),
                30 + int(20 * y / WINDOW_SIZE[1]),
                40 + int(30 * y / WINDOW_SIZE[1])
            )
            pygame.draw.line(self.screen, color, (0, y), (WINDOW_SIZE[0], y))
    
    def draw_title(self) -> None:
        """Draw the game title and subtitle."""
        # Main title
        title_text = self.title_font.render("CRx", True, self.title_color)
        title_rect = title_text.get_rect(center=(WINDOW_SIZE[0] // 2, 150))
        self.screen.blit(title_text, title_rect)
        
        # Subtitle
        subtitle_text = self.subtitle_font.render(
            "Chain Reaction Game", True, self.subtitle_color
        )
        subtitle_rect = subtitle_text.get_rect(
            center=(WINDOW_SIZE[0] // 2, 200)
        )
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # Game instructions
        instructions = [
            "Click on cells to add orbs",
            "Orbs explode when they reach critical mass",
            "Capture all cells to win!"
        ]
        
        for i, instruction in enumerate(instructions):
            text = pygame.font.Font(None, 24).render(
                instruction, True, (180, 180, 180)
            )
            text_rect = text.get_rect(
                center=(WINDOW_SIZE[0] // 2, 250 + i * 25)
            )
            self.screen.blit(text, text_rect)
    
    def draw_decorations(self) -> None:
        """Draw decorative elements."""
        # Draw some animated orbs as decoration
        import math
        time = pygame.time.get_ticks() / 1000.0
        
        # Top decorative orbs
        for i in range(3):
            x = WINDOW_SIZE[0] // 2 + math.sin(time + i * 2) * 150
            y = 100 + math.cos(time + i * 1.5) * 30
            color = PLAYER_COLORS[i % 2]
            pygame.draw.circle(self.screen, color, (int(x), int(y)), 8)
            pygame.draw.circle(
                self.screen, (255, 255, 255), (int(x), int(y)), 8, 2
            )
        
        # Bottom decorative orbs
        for i in range(4):
            x = WINDOW_SIZE[0] // 2 + math.sin(time * 0.8 + i * 1.5) * 200
            y = WINDOW_SIZE[1] - 100 + math.cos(time * 0.6 + i) * 20
            color = PLAYER_COLORS[i % 2]
            pygame.draw.circle(self.screen, color, (int(x), int(y)), 6)
            pygame.draw.circle(
                self.screen, (255, 255, 255), (int(x), int(y)), 6, 1
            )
    
    def run(self) -> Optional[int]:
        """Run the menu loop and return the selected number of players."""
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                # Handle button events
                for i, button in enumerate(self.buttons):
                    if button.handle_event(event):
                        if i == 3:  # Quit button
                            pygame.quit()
                            sys.exit()
                        else:
                            return i + 2  # Return 2, 3, or 4 players
            
            # Draw everything
            self.draw_background()
            self.draw_title()
            self.draw_decorations()
            
            for button in self.buttons:
                button.draw(self.screen)
            
            pygame.display.flip()
            self.clock.tick(60)
        
        return None 