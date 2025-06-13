"""Animation system for the CRx game."""

import math
import random
from typing import List, Tuple
import pygame
from .constants import CELL_SIZE, PLAYER_COLORS

class Animation:
    """Base animation class."""
    def __init__(self, duration: float):
        self.duration = duration
        self.elapsed = 0
        self.is_finished = False

    def update(self, dt: float) -> None:
        """Update animation state."""
        self.elapsed += dt
        if self.elapsed >= self.duration:
            self.is_finished = True

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the animation."""
        pass

class ExplosionAnimation(Animation):
    """Animation for cell explosions."""
    def __init__(self, x: int, y: int, player: int, target_cells: List[Tuple[int, int]]):
        super().__init__(0.5)  # 0.5 seconds duration
        self.x = x
        self.y = y
        self.player = player
        self.target_cells = target_cells
        self.particles = []
        self._init_particles()

    def _init_particles(self):
        """Initialize explosion particles."""
        num_particles = 20
        for _ in range(num_particles):
            angle = math.radians(random.randint(0, 360))
            speed = random.uniform(2, 5)
            self.particles.append({
                'x': self.x * CELL_SIZE + CELL_SIZE // 2,
                'y': self.y * CELL_SIZE + CELL_SIZE // 2,
                'dx': math.cos(angle) * speed,
                'dy': math.sin(angle) * speed,
                'size': random.randint(3, 8),
                'alpha': 255
            })

    def update(self, dt: float) -> None:
        """Update particle positions and states."""
        super().update(dt)
        progress = self.elapsed / self.duration
        
        for particle in self.particles:
            particle['x'] += particle['dx']
            particle['y'] += particle['dy']
            particle['alpha'] = int(255 * (1 - progress))
            particle['size'] = max(1, int(particle['size'] * (1 - progress)))

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the explosion particles."""
        for particle in self.particles:
            if particle['alpha'] > 0:
                color = list(PLAYER_COLORS[self.player])
                color.append(particle['alpha'])
                surface = pygame.Surface((particle['size'] * 2, particle['size'] * 2), pygame.SRCALPHA)
                pygame.draw.circle(
                    surface,
                    color,
                    (particle['size'], particle['size']),
                    particle['size']
                )
                screen.blit(surface, (particle['x'] - particle['size'], particle['y'] - particle['size']))

class OrbAnimation(Animation):
    """Animation for orb movement."""
    def __init__(self, start_pos: Tuple[int, int], end_pos: Tuple[int, int], player: int):
        super().__init__(0.3)  # 0.3 seconds duration
        self.start_x = start_pos[0] * CELL_SIZE + CELL_SIZE // 2
        self.start_y = start_pos[1] * CELL_SIZE + CELL_SIZE // 2
        self.end_x = end_pos[0] * CELL_SIZE + CELL_SIZE // 2
        self.end_y = end_pos[1] * CELL_SIZE + CELL_SIZE // 2
        self.player = player
        self.current_x = self.start_x
        self.current_y = self.start_y

    def update(self, dt: float) -> None:
        """Update orb position."""
        super().update(dt)
        progress = self.elapsed / self.duration
        # Use smooth easing function
        progress = 1 - (1 - progress) * (1 - progress)
        self.current_x = self.start_x + (self.end_x - self.start_x) * progress
        self.current_y = self.start_y + (self.end_y - self.start_y) * progress

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the moving orb."""
        size = int(CELL_SIZE * 0.4)
        pygame.draw.circle(
            screen,
            PLAYER_COLORS[self.player],
            (int(self.current_x), int(self.current_y)),
            size
        ) 