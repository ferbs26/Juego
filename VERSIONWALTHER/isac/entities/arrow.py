import pygame
from dataclasses import dataclass
from isac.settings import ARROW_SPEED, ARROW_SIZE, CYAN


@dataclass
class Arrow:
    x: float
    y: float
    dx: int  # -1, 0, 1
    dy: int  # -1, 0, 1
    alive: bool = True

    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x) - ARROW_SIZE // 2, int(self.y) - ARROW_SIZE // 2, ARROW_SIZE, ARROW_SIZE)

    def update(self, dt: float) -> None:
        self.x += self.dx * ARROW_SPEED * dt
        self.y += self.dy * ARROW_SPEED * dt

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, CYAN, self.rect())
