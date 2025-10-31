import pygame
import math
from isac.settings import TILE

class Spike:
    def __init__(self, x: int, y: int, target_x: int, target_y: int):
        self.x = float(x)
        self.y = float(y)
        self.speed = 200.0  # píxeles por segundo
        self.alive = True
        self.damage = 0.5  # Daño muy bajo
        
        # Calcular dirección hacia el objetivo
        dx = target_x - x
        dy = target_y - y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 0:
            self.vx = (dx / distance) * self.speed
            self.vy = (dy / distance) * self.speed
        else:
            self.vx = self.vy = 0
            
    def update(self, dt: float):
        """Actualiza la posición del pincho"""
        if not self.alive:
            return
            
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        # Eliminar si sale de pantalla
        if self.x < -50 or self.x > 850 or self.y < -50 or self.y > 650:
            self.alive = False
    
    def rect(self) -> pygame.Rect:
        """Devuelve el rectángulo de colisión del pincho"""
        return pygame.Rect(int(self.x) - 3, int(self.y) - 3, 6, 6)
    
    def draw(self, surface: pygame.Surface):
        """Dibuja el pincho"""
        if not self.alive:
            return
            
        # Pincho como pequeña línea puntiaguda
        spike_color = (139, 69, 19)  # Marrón
        tip_color = (160, 82, 45)    # Marrón claro
        
        # Calcular ángulo para orientar el pincho
        angle = math.atan2(self.vy, self.vx)
        
        # Puntos del pincho (triángulo alargado)
        length = 8
        width = 3
        
        # Punta del pincho
        tip_x = self.x + math.cos(angle) * length
        tip_y = self.y + math.sin(angle) * length
        
        # Base del pincho
        base_angle1 = angle + math.pi * 0.8
        base_angle2 = angle - math.pi * 0.8
        base1_x = self.x + math.cos(base_angle1) * width
        base1_y = self.y + math.sin(base_angle1) * width
        base2_x = self.x + math.cos(base_angle2) * width
        base2_y = self.y + math.sin(base_angle2) * width
        
        # Dibujar pincho como triángulo
        points = [(tip_x, tip_y), (base1_x, base1_y), (base2_x, base2_y)]
        pygame.draw.polygon(surface, spike_color, points)
        pygame.draw.polygon(surface, tip_color, points, 1)


class Companion:
    def __init__(self, x: int, y: int):
        # Cargar el sprite de la estatua
        self.sprite = pygame.image.load('C:/Users/herna/OneDrive/Documentos/GitHub/VERSIONWALTHER/assets/player/statue.png').convert_alpha()
        
        # Escalar el sprite a 32x32 píxeles
        sprite_size = (32, 32)  # Tamaño fijo de 32x32 píxeles
        self.sprite = pygame.transform.scale(self.sprite, sprite_size)
        
        # Crear el rectángulo de colisión
        self.rect = self.sprite.get_rect()
        self.rect.center = (x, y)
        self.collected = False
        self.active = False
        
        # Propiedades de combate
        self.detection_range = 150
        self.shoot_cooldown = 1.0  # segundos entre disparos
        self.shoot_timer = 0.0
        
        # Duración limitada
        self.duration = 10.0  # 10 segundos de duración
        self.time_remaining = 10.0
        
        # Animación
        self.bob_timer = 0.0
        self.original_y = y
        
    def update(self, dt: float, player_rect: pygame.Rect = None):
        """Actualiza el compañero"""
        if self.collected and not self.active:
            return
            
        # Reducir tiempo restante
        if self.active:
            self.time_remaining -= dt
            if self.time_remaining <= 0:
                self.active = False
                return
            
        # Animación de flotación
        self.bob_timer += dt * 2.0
        bob_offset = math.sin(self.bob_timer) * 3
        
        if self.active and player_rect:
            # Seguir al jugador a cierta distancia
            target_x = player_rect.centerx + 30
            target_y = player_rect.centery - 20 + bob_offset
            
            # Movimiento suave hacia el jugador
            dx = target_x - self.rect.centerx
            dy = target_y - self.rect.centery
            
            move_speed = 100.0
            if abs(dx) > 5:
                self.rect.centerx += int(dx * move_speed * dt / 100)
            if abs(dy) > 5:
                self.rect.centery += int(dy * move_speed * dt / 100)
        else:
            # Flotación en el lugar
            self.rect.centery = int(self.original_y + bob_offset)
        
        # Cooldown de disparo
        if self.shoot_timer > 0:
            self.shoot_timer = max(0.0, self.shoot_timer - dt)
    
    def apply_effect(self, player):
        """Activa el compañero y lo posiciona junto al jugador"""
        self.collected = True
        self.active = True
        # Posicionar el compañero junto al jugador
        self.rect.centerx = player.rect.centerx + 30
        self.rect.centery = player.rect.centery - 20
        
    def can_shoot(self) -> bool:
        """Verifica si puede disparar"""
        return self.active and self.shoot_timer <= 0
    
    def shoot_at_enemy(self, enemy_rect: pygame.Rect) -> list[Spike]:
        """Dispara tres pinchos hacia un enemigo en diferentes direcciones"""
        if not self.can_shoot():
            return []
            
        # Verificar si el enemigo está en rango
        dx = enemy_rect.centerx - self.rect.centerx
        dy = enemy_rect.centery - self.rect.centery
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance <= self.detection_range:
            self.shoot_timer = self.shoot_cooldown
            
            # Calcular ángulo hacia el enemigo
            angle_to_enemy = math.atan2(dy, dx)
            
            # Crear tres pinchos con diferentes ángulos
            spikes = []
            angles = [
                angle_to_enemy - 0.3,  # 17 grados a la izquierda
                angle_to_enemy,        # Directo al enemigo
                angle_to_enemy + 0.3   # 17 grados a la derecha
            ]
            
            for angle in angles:
                # Calcular posición objetivo para cada ángulo
                target_distance = distance
                target_x = self.rect.centerx + math.cos(angle) * target_distance
                target_y = self.rect.centery + math.sin(angle) * target_distance
                
                spike = Spike(self.rect.centerx, self.rect.centery, target_x, target_y)
                spikes.append(spike)
            
            return spikes
        
        return []
    
    def find_nearest_enemy(self, enemies: list):
        """Encuentra el enemigo más cercano en rango"""
        if not self.active or not enemies:
            return None
            
        nearest_enemy = None
        nearest_distance = float('inf')
        
        for enemy in enemies:
            if not enemy.alive:
                continue
                
            dx = enemy.rect.centerx - self.rect.centerx
            dy = enemy.rect.centery - self.rect.centery
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance <= self.detection_range and distance < nearest_distance:
                nearest_distance = distance
                nearest_enemy = enemy
                
        return nearest_enemy
    
    def draw(self, surface: pygame.Surface):
        """Dibuja el compañero usando el sprite de estatua"""
        if self.collected and not self.active:
            return
            
        # Dibujar el sprite de la estatua
        if hasattr(self, 'sprite'):
            # Aplicar animación de flotación
            bob_offset = math.sin(self.bob_timer * 2) * 3
            draw_pos = self.rect.copy()
            draw_pos.y += bob_offset
            
            # Dibujar el sprite centrado en la posición del rectángulo
            sprite_rect = self.sprite.get_rect(center=self.rect.center)
            sprite_rect.y += bob_offset
            surface.blit(self.sprite, sprite_rect)
        
        # Indicador de rango de detección (solo si está activo)
        if self.active and self.can_shoot():
            range_surface = pygame.Surface((self.detection_range * 2, self.detection_range * 2), pygame.SRCALPHA)
            range_color = (135, 206, 235, 30)  # Azul claro (#87CEEB) translúcido
            pygame.draw.circle(range_surface, range_color, 
                             (self.detection_range, self.detection_range), self.detection_range)
            surface.blit(range_surface, 
                        (self.rect.centerx - self.detection_range, 
                         self.rect.centery - self.detection_range))
