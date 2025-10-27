import os
import pygame
from dataclasses import dataclass, field
from typing import Dict, Optional
from isac.settings import CYAN, WHITE, TILE


@dataclass
class Pickup:
    kind: str  # 'bomb' | 'key' | 'magic' | 'arrow'
    x: int
    y: int
    _images: Dict[str, pygame.Surface] = field(default_factory=dict, init=False)
    
    def __post_init__(self):
        # Cargar imágenes solo una vez
        if not self._images:
            try:
                # Cargar imagen de bomba
                bomb_img = pygame.image.load(os.path.join('assets', 'player', 'bomba.png')).convert_alpha()
                self._images['bomb'] = pygame.transform.scale(bomb_img, (20, 20))
                
                # Cargar imagen de llave
                key_img = pygame.image.load(os.path.join('assets', 'player', 'llave.png')).convert_alpha()
                self._images['key'] = pygame.transform.scale(key_img, (20, 20))
                
                # Para otros tipos, mantener el comportamiento original con colores
                self._images['magic'] = None
                self._images['arrow'] = None
                
            except Exception as e:
                print(f"Error cargando imágenes de pickups: {e}")
                self._images = {}

    def rect(self) -> pygame.Rect:
        return pygame.Rect(self.x - 10, self.y - 10, 20, 20)

    def draw(self, surface: pygame.Surface) -> None:
        if self.kind in self._images and self._images[self.kind] is not None:
            # Dibujar la imagen centrada en la posición (x, y)
            img_rect = self._images[self.kind].get_rect(center=(self.x, self.y))
            surface.blit(self._images[self.kind], img_rect)
        else:
            # Comportamiento original para tipos sin imagen
            if self.kind == 'key':
                color = (255, 215, 0)  # Amarillo dorado
            elif self.kind == 'bomb':
                color = (0, 255, 0)    # Verde
            elif self.kind == 'magic':
                color = CYAN
            else:  # 'arrow'
                color = WHITE
                
            pygame.draw.rect(surface, color, self.rect())
