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
        
        # Cargar el sprite de las botas
        try:
            self.sprite = pygame.image.load('assets/player/speedboots.png').convert_alpha()
            # Escalar el sprite al tamaño del objeto
            self.sprite = pygame.transform.scale(self.sprite, (self.rect.width, self.rect.height))
        except pygame.error as e:
            print(f"Error al cargar el sprite de las botas: {e}")
            self.sprite = None
        
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
        """Dibuja las botas con el sprite"""
        if self.collected or not hasattr(self, 'sprite') or self.sprite is None:
            return
        
        # Dibujar el sprite
        surface.blit(self.sprite, self.rect)
        
        # Mantener el efecto de brillo
        highlight_alpha = int(150 + 100 * math.sin(self.glow_timer * 1.5))
        highlight_surface = pygame.Surface((self.rect.width, 4), pygame.SRCALPHA)
        highlight_color = (255, 255, 200, highlight_alpha)
        highlight_surface.fill(highlight_color)
        surface.blit(highlight_surface, (self.rect.x, self.rect.y + 2),
                    special_flags=pygame.BLEND_ADD)
