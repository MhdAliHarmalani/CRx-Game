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

    def __init__(
        self, x: int, y: int, player: int, target_cells: List[Tuple[int, int]]
    ):
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
            self.particles.append(
                {
                    "x": self.x * CELL_SIZE + CELL_SIZE // 2,
                    "y": self.y * CELL_SIZE + CELL_SIZE // 2,
                    "dx": math.cos(angle) * speed,
                    "dy": math.sin(angle) * speed,
                    "size": random.randint(3, 8),
                    "alpha": 255,
                }
            )

    def update(self, dt: float) -> None:
        """Update particle positions and states."""
        super().update(dt)
        progress = self.elapsed / self.duration

        for particle in self.particles:
            particle["x"] += particle["dx"]
            particle["y"] += particle["dy"]
            particle["alpha"] = int(255 * (1 - progress))
            particle["size"] = max(1, int(particle["size"] * (1 - progress)))

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the explosion particles."""
        for particle in self.particles:
            if particle["alpha"] > 0:
                color = list(PLAYER_COLORS[self.player])
                color.append(particle["alpha"])
                surface = pygame.Surface(
                    (particle["size"] * 2, particle["size"] * 2),
                    pygame.SRCALPHA,
                )
                pygame.draw.circle(
                    surface,
                    color,
                    (
                        particle["size"],
                        particle["size"],
                    ),
                    particle["size"],
                )
                screen.blit(
                    surface,
                    (
                        particle["x"] - particle["size"],
                        particle["y"] - particle["size"],
                    ),
                )


class OrbAnimation(Animation):
    """Animation for orb movement."""

    def __init__(
        self, start_pos: Tuple[int, int], end_pos: Tuple[int, int], player: int
    ):
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
            size,
        )


class AtomOrbAnimation(Animation):
    """Animation for atom-like orb movement within a cell."""

    def __init__(
        self,
        cell_x: int,
        cell_y: int,
        player: int,
        orb_count: int = 1,
    ):
        super().__init__(float("inf"))  # Continuous animation
        self.cell_x = cell_x
        self.cell_y = cell_y
        self.player = player
        self.orb_count = orb_count
        self.orb_radius = CELL_SIZE // 6
        self.angle = 0
        self.rotation_speed = 2.0  # Radians per second

        # Different behavior based on orb count
        if orb_count == 1:
            # Single orb spins in place at center
            self.orbit_radius = 0
            self.spin_speed = 3.0  # Faster spin for single orb
        elif orb_count == 2:
            # Two orbs opposite each other - closer to center
            self.orbit_radius = CELL_SIZE // 6
        else:
            # Three or more orbs in circular formation - closer to center
            self.orbit_radius = CELL_SIZE // 5

    def update_orb_count(self, new_count: int):
        """Update the animation when orb count changes."""
        self.orb_count = new_count
        if new_count == 1:
            self.orbit_radius = 0
            self.spin_speed = 3.0
        elif new_count == 2:
            self.orbit_radius = CELL_SIZE // 6
        else:
            self.orbit_radius = CELL_SIZE // 5

    def update(self, dt: float) -> None:
        """Update orb positions in atom-like orbits."""
        super().update(dt)
        if self.orb_count == 1:
            # Single orb just spins in place
            self.angle += self.spin_speed * dt
        else:
            # Multiple orbs orbit around center
            self.angle += self.rotation_speed * dt

        if self.angle > 2 * math.pi:
            self.angle -= 2 * math.pi

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the orbiting orbs with atom-like movement."""
        center_x = self.cell_x + CELL_SIZE // 2
        center_y = self.cell_y + CELL_SIZE // 2

        if self.orb_count == 1:
            # Single orb at center with rotation effect
            x = center_x
            y = center_y

            # Draw spinning effect with slight pulsing
            pulse = 1 + 0.1 * math.sin(self.angle * 2)
            current_radius = int(self.orb_radius * pulse)

            # Draw orb shadow
            shadow_offset = 2
            pygame.draw.circle(
                screen,
                (0, 0, 0, 128),
                (x + shadow_offset, y + shadow_offset),
                current_radius,
            )

            # Draw the orb
            pygame.draw.circle(
                screen,
                PLAYER_COLORS[self.player],
                (x, y),
                current_radius,
            )

            # Draw rotating highlight
            highlight_x = x + int((current_radius // 3) * math.cos(self.angle))
            highlight_y = y + int((current_radius // 3) * math.sin(self.angle))
            highlight_color = tuple(
                min(c + 50, 255) for c in PLAYER_COLORS[self.player]
            )
            pygame.draw.circle(
                screen,
                highlight_color,
                (highlight_x, highlight_y),
                current_radius // 3,
            )

        else:
            # Multiple orbs orbiting around center
            for i in range(self.orb_count):
                # Calculate position for each orb
                orb_angle = self.angle + (2 * math.pi * i / self.orb_count)
                x = center_x + int(self.orbit_radius * math.cos(orb_angle))
                y = center_y + int(self.orbit_radius * math.sin(orb_angle))

                # Draw orbit trail (subtle)
                if i == 0:  # Only draw trail for first orb to avoid clutter
                    trail_surface = pygame.Surface(
                        (CELL_SIZE, CELL_SIZE), pygame.SRCALPHA
                    )
                    trail_points = []
                    for j in range(8):
                        trail_angle = orb_angle - (j * 0.2)
                        tx = CELL_SIZE // 2 + int(
                            self.orbit_radius * math.cos(trail_angle)
                        )
                        ty = CELL_SIZE // 2 + int(
                            self.orbit_radius * math.sin(trail_angle)
                        )
                        trail_points.append((tx, ty))

                    if len(trail_points) > 1:
                        for j in range(len(trail_points) - 1):
                            alpha = int(50 * (1 - j / len(trail_points)))
                            color = (*PLAYER_COLORS[self.player], alpha)
                            pygame.draw.line(
                                trail_surface,
                                color,
                                trail_points[j],
                                trail_points[j + 1],
                                1,
                            )
                        screen.blit(trail_surface, (self.cell_x, self.cell_y))

                # Draw orb shadow
                shadow_offset = 2
                pygame.draw.circle(
                    screen,
                    (0, 0, 0, 128),
                    (x + shadow_offset, y + shadow_offset),
                    self.orb_radius,
                )

                # Draw the orb
                pygame.draw.circle(
                    screen,
                    PLAYER_COLORS[self.player],
                    (x, y),
                    self.orb_radius,
                )

                # Draw orb highlight
                highlight_color = tuple(
                    min(c + 50, 255) for c in PLAYER_COLORS[self.player]
                )
                pygame.draw.circle(
                    screen,
                    highlight_color,
                    (x - self.orb_radius // 3, y - self.orb_radius // 3),
                    self.orb_radius // 3,
                )
