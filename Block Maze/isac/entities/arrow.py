import os
import pygame
from dataclasses import dataclass, field
from typing import Optional, Tuple
from isac.settings import ARROW_SPEED, ARROW_SIZE, CYAN, ARROW_DAMAGE


@dataclass
class Arrow:
    x: float
    y: float
    dx: int  # -1, 0, 1
    dy: int  # -1, 0, 1
    arrow_type: str = 'normal'  # 'normal' o 'big_shot'
    damage: int = ARROW_DAMAGE
    damage_multiplier: float = 1.0  # Multiplicador de daño basado en el personaje
    speed: float = ARROW_SPEED
    alive: bool = True
    _sprite: Optional[pygame.Surface] = field(init=False, default=None)
    _angle: float = field(init=False, default=0.0)

    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x) - ARROW_SIZE // 2, int(self.y) - ARROW_SIZE // 2, ARROW_SIZE, ARROW_SIZE)

    def update(self, dt: float) -> None:
        self.x += self.dx * self.speed * dt
        self.y += self.dy * self.speed * dt

    def __post_init__(self):
        # Cargar el sprite apropiado según el tipo de flecha
        try:
            print(f"Creando flecha de tipo: {self.arrow_type}")
            
            if self.arrow_type == 'big_shot':
                sprite_path = os.path.join('assets', 'bullet', 'weirdshot.png')
                self.damage = 5  # Daño fijo de 5 para BIG SHOT
                self.speed = ARROW_SPEED * 0.7  # 70% de la velocidad normal
                print(f"Ruta del sprite BIG SHOT: {sprite_path}")
            else:
                sprite_path = os.path.join('assets', 'bullet', 'spark3.png')
                
            print(f"Intentando cargar sprite desde: {sprite_path}")
            if not os.path.exists(sprite_path):
                print(f"¡Error! No se encontró el archivo: {sprite_path}")
                
            self._sprite = pygame.image.load(sprite_path).convert_alpha()
            print(f"Sprite cargado correctamente. Tamaño original: {self._sprite.get_size()}")
            
            # Escalar el sprite a un tamaño apropiado
            if self.arrow_type == 'big_shot':
                size = int(ARROW_SIZE * 1.5)  # Un poco más grande para el BIG SHOT
                print(f"Escalando BIG SHOT a tamaño: {size*2}x{size*2}")
            else:
                size = ARROW_SIZE
                
            self._sprite = pygame.transform.scale(self._sprite, (size * 2, size * 2))
            
            # Calcular ángulo inicial basado en la dirección
            self._angle = self._calculate_angle()
        except Exception as e:
            print(f"Error loading arrow sprite: {e}")
            self._sprite = None
            
    def get_damage(self) -> int:
        """Get the final damage considering the damage multiplier."""
        return int(self.damage * self.damage_multiplier)

    def _calculate_angle(self) -> float:
        """Calculate the rotation angle based on direction vector."""
        if self.dx == 0 and self.dy == -1:  # Up
            return 0
        elif self.dx == 1 and self.dy == -1:  # Up-Right
            return 45
        elif self.dx == 1 and self.dy == 0:  # Right
            return 90
        elif self.dx == 1 and self.dy == 1:  # Down-Right
            return 135
        elif self.dx == 0 and self.dy == 1:  # Down
            return 180
        elif self.dx == -1 and self.dy == 1:  # Down-Left
            return 225
        elif self.dx == -1 and self.dy == 0:  # Left
            return 270
        elif self.dx == -1 and self.dy == -1:  # Up-Left
            return 315
        return 0  # Default to right if no direction
        
    def draw(self, surface: pygame.Surface) -> None:
        if self._sprite:
            try:
                # Rotate the sprite based on direction
                rotated_sprite = pygame.transform.rotate(self._sprite, self._angle)
                # Get the rect centered on the arrow's position
                sprite_rect = rotated_sprite.get_rect(center=(int(self.x), int(self.y)))
                surface.blit(rotated_sprite, sprite_rect)
                
                # Dibujar un rectángulo de colisión para depuración
                if self.arrow_type == 'big_shot':
                    pygame.draw.rect(surface, (255, 0, 0), self.rect(), 1)  # Rojo para BIG SHOT
                else:
                    pygame.draw.rect(surface, (0, 255, 0), self.rect(), 1)  # Verde para flechas normales
                    
            except Exception as e:
                print(f"Error al dibujar flecha: {e}")
                # Fallback a rectángulo si hay un error con el sprite
                color = (255, 0, 0) if self.arrow_type == 'big_shot' else CYAN
                pygame.draw.rect(surface, color, self.rect())
        else:
            # Fallback to rectangle if sprite loading failed
            color = (255, 0, 0) if self.arrow_type == 'big_shot' else CYAN
            pygame.draw.rect(surface, color, self.rect())
            print(f"No hay sprite para flecha de tipo: {self.arrow_type}")
