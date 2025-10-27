import os
import pygame
from dataclasses import dataclass, field
from isac.settings import YELLOW, CYAN, GREEN, WHITE, TILE


@dataclass
class Pickup:
    kind: str  # 'bomb' | 'key' | 'magic' | 'arrow'
    x: int
    y: int
    sprites: dict = field(init=False, default_factory=dict)
    
    def __post_init__(self):
        # Cargar el sprite de la llave si no está cargado
        if self.kind == 'key' and not self.sprites.get('key'):
            try:
                key_sprite = pygame.image.load(os.path.join('assets', 'player', 'llave.png')).convert_alpha()
                # Escalar el sprite a 64x64 píxeles
                self.sprites['key'] = pygame.transform.scale(key_sprite, (32, 32))
            except:
                # Si hay un error al cargar la imagen, usar un rectángulo amarillo como respaldo
                self.sprites['key'] = None

    def rect(self) -> pygame.Rect:
        return pygame.Rect(self.x - 10, self.y - 10, 20, 20)

    def draw(self, surface: pygame.Surface) -> None:
        if self.kind == 'key':
            if 'key' in self.sprites and self.sprites['key'] is not None:
                # Dibujar el sprite de la llave centrado en la posición
                key_rect = self.sprites['key'].get_rect(center=(self.x, self.y))
                surface.blit(self.sprites['key'], key_rect)
                return
            else:
                color = YELLOW
        elif self.kind == 'bomb':
            color = GREEN
        elif self.kind == 'magic':
            color = CYAN
        else:  # 'arrow'
            color = WHITE
        
        # Dibujar un rectángulo de respaldo si no se pudo cargar el sprite
        pygame.draw.rect(surface, color, self.rect())
