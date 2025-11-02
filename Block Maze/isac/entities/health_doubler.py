import pygame
import math
from isac.settings import TILE

class HealthDoubler:
    def __init__(self, x: int, y: int):
        self.rect = pygame.Rect(x, y, TILE // 2, TILE // 2)
        self.rect.center = (x, y)
        self.collected = False
        self.pulse_timer = 0.0
        self.float_timer = 0.0
        self.original_y = y
        
    def update(self, dt: float):
        """Actualiza los efectos visuales"""
        self.pulse_timer += dt * 4.0  # Velocidad del pulso
        self.float_timer += dt * 1.5  # Velocidad de flotación
        
    def apply_effect(self, player):
        """Duplica la vida máxima del jugador"""
        old_max_hp = player.max_hp
        player.max_hp *= 2
        # Curar completamente al jugador cuando obtiene el item
        player.hp = player.max_hp
        self.collected = True
        
    def draw(self, surface: pygame.Surface):
        """Dibuja el corazón doblador con efectos"""
        if self.collected:
            return
            
        # Flotación suave
        float_offset = math.sin(self.float_timer) * 4
        draw_y = self.original_y + float_offset
        
        # Efecto de pulso
        pulse_scale = 1.0 + 0.3 * math.sin(self.pulse_timer)
        pulse_size = int(self.rect.width * pulse_scale)
        
        # Calcular posición centrada para el pulso
        pulse_rect = pygame.Rect(0, 0, pulse_size, pulse_size)
        pulse_rect.center = (self.rect.centerx, int(draw_y))
        
        # Brillo exterior pulsante
        glow_intensity = int(100 + 80 * math.sin(self.pulse_timer))
        glow_surface = pygame.Surface((pulse_size + 30, pulse_size + 30), pygame.SRCALPHA)
        glow_color = (255, 100, 100, glow_intensity)
        
        # Crear múltiples capas de brillo
        for i in range(3):
            glow_size = pulse_size + 10 + i * 8
            glow_alpha = max(0, glow_intensity - i * 30)
            if glow_alpha > 0:
                glow_rect = pygame.Rect((30 - glow_size) // 2, (30 - glow_size) // 2, 
                                       glow_size, glow_size)
                pygame.draw.ellipse(glow_surface, (255, 100, 100, glow_alpha), glow_rect)
        
        surface.blit(glow_surface, (pulse_rect.centerx - 15, pulse_rect.centery - 15),
                    special_flags=pygame.BLEND_ADD)
        
        # Dibujar corazón principal
        heart_color = (220, 20, 60)  # Rojo intenso
        highlight_color = (255, 105, 180)  # Rosa claro
        
        # Corazón como dos círculos y un triángulo
        heart_size = pulse_size // 2
        
        # Círculos superiores del corazón
        left_circle = pygame.Rect(pulse_rect.centerx - heart_size // 2, 
                                 pulse_rect.centery - heart_size // 4,
                                 heart_size // 2, heart_size // 2)
        right_circle = pygame.Rect(pulse_rect.centerx, 
                                  pulse_rect.centery - heart_size // 4,
                                  heart_size // 2, heart_size // 2)
        
        pygame.draw.ellipse(surface, heart_color, left_circle)
        pygame.draw.ellipse(surface, heart_color, right_circle)
        
        # Parte inferior del corazón (triángulo)
        bottom_points = [
            (pulse_rect.centerx, pulse_rect.centery + heart_size // 2),
            (pulse_rect.centerx - heart_size // 2, pulse_rect.centery),
            (pulse_rect.centerx + heart_size // 2, pulse_rect.centery)
        ]
        pygame.draw.polygon(surface, heart_color, bottom_points)
        
        # Brillos en el corazón
        highlight_alpha = int(150 + 100 * math.sin(self.pulse_timer * 1.5))
        
        # Brillo en círculo izquierdo
        left_highlight = pygame.Rect(left_circle.x + 2, left_circle.y + 2, 
                                    left_circle.width // 3, left_circle.height // 3)
        highlight_surface = pygame.Surface(left_highlight.size, pygame.SRCALPHA)
        highlight_surface.fill((255, 255, 255, highlight_alpha))
        surface.blit(highlight_surface, left_highlight.topleft, special_flags=pygame.BLEND_ADD)
        
        # Brillo en círculo derecho
        right_highlight = pygame.Rect(right_circle.x + 2, right_circle.y + 2,
                                     right_circle.width // 3, right_circle.height // 3)
        highlight_surface = pygame.Surface(right_highlight.size, pygame.SRCALPHA)
        highlight_surface.fill((255, 255, 255, highlight_alpha))
        surface.blit(highlight_surface, right_highlight.topleft, special_flags=pygame.BLEND_ADD)
        
        # Partículas flotantes alrededor del corazón
        particle_count = 6
        for i in range(particle_count):
            angle = (self.pulse_timer * 0.5 + i * (2 * math.pi / particle_count)) % (2 * math.pi)
            particle_distance = 20 + 5 * math.sin(self.pulse_timer + i)
            particle_x = pulse_rect.centerx + math.cos(angle) * particle_distance
            particle_y = pulse_rect.centery + math.sin(angle) * particle_distance
            
            particle_alpha = int(100 + 50 * math.sin(self.pulse_timer * 2 + i))
            if particle_alpha > 0:
                particle_surface = pygame.Surface((6, 6), pygame.SRCALPHA)
                particle_color = (255, 150, 150, particle_alpha)
                pygame.draw.circle(particle_surface, particle_color, (3, 3), 3)
                surface.blit(particle_surface, (int(particle_x) - 3, int(particle_y) - 3),
                           special_flags=pygame.BLEND_ADD)
