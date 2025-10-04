import pygame
from dataclasses import dataclass
from isac.settings import YELLOW, CYAN, GREEN, WHITE


@dataclass
class Pickup:
    kind: str  # 'bomb' | 'key' | 'magic' | 'arrow'
    x: int
    y: int

    def rect(self) -> pygame.Rect:
        return pygame.Rect(self.x - 10, self.y - 10, 20, 20)

    def draw(self, surface: pygame.Surface) -> None:
        if self.kind == 'key':
            color = YELLOW
        elif self.kind == 'bomb':
            color = GREEN
        elif self.kind == 'magic':
            color = CYAN
        else:  # 'arrow'
            color = WHITE
        
        pygame.draw.rect(surface, color, self.rect())
