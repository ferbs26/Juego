import pygame
import math
from isac.settings import TILE

class SpeedBoots:
    def __init__(self, x: int, y: int):
        self.rect = pygame.Rect(x, y, TILE // 2, TILE // 2)
        self.rect.center = (x, y)
        self.collected = False
        self.glow_timer = 0.0
        self.ray_timer = 0.0
        self.speed_multiplier = 1.5  # 50% más velocidad
        
    def update(self, dt: float):
        """Actualiza los efectos visuales"""
        self.glow_timer += dt * 3.0  # Velocidad del brillo
        self.ray_timer += dt * 2.0   # Velocidad de los rayos
        
    def apply_effect(self, player):
        """Aplica el efecto de velocidad al jugador"""
        if hasattr(player, 'speed_multiplier'):
            player.speed_multiplier *= self.speed_multiplier
        else:
            player.speed_multiplier = self.speed_multiplier
        # NO marcar como collected para que siga mostrando efectos visuales
        # self.collected = True
        
    def draw(self, surface: pygame.Surface):
        """Dibuja las botas sin efectos brillantes"""
        if self.collected:
            return
        
        # Dibujar las botas
        boot_color = (139, 69, 19)  # Marrón
        sole_color = (101, 67, 33)  # Marrón más oscuro
        lace_color = (255, 255, 255)  # Blanco
        
        # Bota izquierda
        left_boot = pygame.Rect(self.rect.x, self.rect.y + 4, 
                               self.rect.width // 2 - 1, self.rect.height - 4)
        pygame.draw.rect(surface, boot_color, left_boot, border_radius=3)
        pygame.draw.rect(surface, sole_color, 
                        (left_boot.x, left_boot.bottom - 3, left_boot.width, 3))
        
        # Bota derecha
        right_boot = pygame.Rect(self.rect.x + self.rect.width // 2 + 1, self.rect.y + 4,
                                self.rect.width // 2 - 1, self.rect.height - 4)
        pygame.draw.rect(surface, boot_color, right_boot, border_radius=3)
        pygame.draw.rect(surface, sole_color,
                        (right_boot.x, right_boot.bottom - 3, right_boot.width, 3))
        
        # Cordones
        pygame.draw.line(surface, lace_color, 
                        (left_boot.centerx, left_boot.y + 2),
                        (left_boot.centerx, left_boot.y + 8), 1)
        pygame.draw.line(surface, lace_color,
                        (right_boot.centerx, right_boot.y + 2),
                        (right_boot.centerx, right_boot.y + 8), 1)
        
        # Brillo adicional en las botas
        highlight_alpha = int(150 + 100 * math.sin(self.glow_timer * 1.5))
        highlight_surface = pygame.Surface((self.rect.width, 4), pygame.SRCALPHA)
        highlight_color = (255, 255, 200, highlight_alpha)
        highlight_surface.fill(highlight_color)
        surface.blit(highlight_surface, (self.rect.x, self.rect.y + 2),
                    special_flags=pygame.BLEND_ADD)
