import pygame
import math
from isac.settings import RED, ENEMY_SPEED, ENEMY_SIZE, ENEMY_DEFAULT_HP


class Enemy:
    def __init__(self, x: int, y: int, hp: int | None = None, speed_scale: float = 1.0, color: tuple[int, int, int] | None = None, kind: str = 'grunt'):
        self.rect = pygame.Rect(0, 0, ENEMY_SIZE, ENEMY_SIZE)
        self.rect.center = (x, y)
        self.alive = True
        # Vida y feedback
        self.max_hp = hp if hp is not None else ENEMY_DEFAULT_HP
        self.hp = self.max_hp
        self.hurt_timer: float = 0.0  # segundos de flash si fue golpeado
        self.invuln_timer: float = 0.0  # evitar múltiples golpes en el mismo frame
        self.speed_scale: float = max(0.1, speed_scale)
        self.color: tuple[int, int, int] = color if color is not None else RED
        self.kind: str = kind
        # Estado para comportamientos
        self._zigzag_phase: float = 0.0  # para runner
        self._charge_cd: float = 0.0     # para brute
        self._charge_time: float = 0.0   # para brute
        self.charge_just_started: bool = False  # para telegráfico/sonido
        
        # Inicializar diccionario de sprites y cargarlos
        self.sprites = {}
        self.current_sprite = None
        self.cargar_sprites()

    def cargar_sprites(self):
        """Carga los sprites de los enemigos."""
        try:
            # Cargar sprites básicos
            self.sprites['grunt'] = pygame.transform.scale(
                pygame.image.load('assets/enemies/pale_oni.png').convert_alpha(), 
                (ENEMY_SIZE, ENEMY_SIZE)
            )
            self.sprites['runner'] = pygame.transform.scale(
                pygame.image.load('assets/enemies/pale_oni.png').convert_alpha(), 
                (ENEMY_SIZE, ENEMY_SIZE)
            )

            # Cargar sprites de enemigos de tipo brute con direcciones
            self.sprites['brute_right'] = pygame.transform.scale(
                pygame.image.load('assets/enemies/clay_mask/clay_mask3.png').convert_alpha(), 
                (ENEMY_SIZE, ENEMY_SIZE)
            )
            self.sprites['brute_left'] = pygame.transform.scale(
                pygame.image.load('assets/enemies/clay_mask/clay_mask1.png').convert_alpha(), 
                (ENEMY_SIZE, ENEMY_SIZE)
            )
            self.sprites['brute_down'] = pygame.transform.scale(
                pygame.image.load('assets/enemies/clay_mask/clay_mask4.png').convert_alpha(), 
                (ENEMY_SIZE, ENEMY_SIZE)
            )
            self.sprites['brute_up'] = pygame.transform.scale(
                pygame.image.load('assets/enemies/clay_mask/clay_mask2.png').convert_alpha(), 
                (ENEMY_SIZE, ENEMY_SIZE)
            )
            
            # Establecer sprite inicial
            if self.kind == 'brute':
                self.current_sprite = self.sprites['brute_down']
            else:
                self.current_sprite = self.sprites[self.kind]

        except pygame.error as e:
            print(f"Error al cargar sprites: {e}")
            self.current_sprite = None

    def take_damage(self, dmg: int) -> bool:
        """Aplica daño. Devuelve True si muere tras el golpe."""
        if not self.alive:
            return False
        if self.invuln_timer > 0:
            return False
        self.hp -= max(0, dmg)
        self.hurt_timer = 0.12
        self.invuln_timer = 0.05
        if self.hp <= 0:
            self.alive = False
            return True
        return False

    def update(self, player_rect: pygame.Rect, dt: float, walls: list = None, obstacles: list = None):
        if not self.alive:
            return
        # reset de bandera de inicio de carga
        self.charge_just_started = False
        # Timers
        if self.hurt_timer > 0:
            self.hurt_timer = max(0.0, self.hurt_timer - dt)
        if self.invuln_timer > 0:
            self.invuln_timer = max(0.0, self.invuln_timer - dt)
        
        # Guardar posición anterior para revertir en caso de colisión
        prev_x, prev_y = self.rect.x, self.rect.y
        
        # Moverse hacia el jugador con variaciones por tipo
        to_player = pygame.Vector2(player_rect.centerx - self.rect.centerx,
                                   player_rect.centery - self.rect.centery)
        base_speed = ENEMY_SPEED * self.speed_scale
        if to_player.length_squared() > 0:
            dir_vec = to_player.normalize()
        else:
            dir_vec = pygame.Vector2(0, 0)

        if self.kind == 'runner':
            # Zig-zag: sumamos componente perpendicular oscilante
            self._zigzag_phase += dt * 6.0
            perp = pygame.Vector2(-dir_vec.y, dir_vec.x) * 0.6 * math.sin(self._zigzag_phase)
            move = (dir_vec + perp).normalize() if (dir_vec + perp).length_squared() > 0 else dir_vec
            vx = move.x * base_speed
            vy = move.y * base_speed
        elif self.kind == 'brute':
            # Embestida: períodos de carga más rápida con cooldown
            if self._charge_cd > 0:
                self._charge_cd = max(0.0, self._charge_cd - dt)
            if self._charge_time > 0:
                self._charge_time = max(0.0, self._charge_time - dt)
            # Si está listo para cargar y está a rango, inicia carga
            if self._charge_time == 0 and self._charge_cd == 0 and to_player.length() < 180:
                self._charge_time = 0.6
                self._charge_cd = 2.0
                self.charge_just_started = True
            speed_mul = 2.0 if self._charge_time > 0 else 1.0
            vx = dir_vec.x * base_speed * speed_mul
            vy = dir_vec.y * base_speed * speed_mul
            
            # Actualizar sprite según dirección de movimiento para brute
            if abs(dir_vec.x) > abs(dir_vec.y):
                if dir_vec.x > 0:
                    self.current_sprite = self.sprites.get('brute_right', self.current_sprite)
                else:
                    self.current_sprite = self.sprites.get('brute_left', self.current_sprite)
            else:
                if dir_vec.y > 0:
                    self.current_sprite = self.sprites.get('brute_down', self.current_sprite)
                else:
                    self.current_sprite = self.sprites.get('brute_up', self.current_sprite)
        else:
            vx = dir_vec.x * base_speed
            vy = dir_vec.y * base_speed

        # Aplicar movimiento
        self.rect.x += int(vx * dt)
        self.rect.y += int(vy * dt)
        
        # Verificar colisiones y aplicar navegación inteligente
        collision_detected = False
        
        # Verificar colisiones con paredes
        if walls:
            for wall in walls:
                if self.rect.colliderect(wall):
                    collision_detected = True
                    break
        
        # Verificar colisiones con obstáculos
        if not collision_detected and obstacles:
            for obstacle in obstacles:
                if self.rect.colliderect(obstacle):
                    collision_detected = True
                    break
        
        if collision_detected:
            # Revertir posición
            self.rect.x, self.rect.y = prev_x, prev_y
            
            # Intentar navegación alternativa
            self._navigate_around_obstacle(prev_x, prev_y, vx, vy, dt, walls, obstacles)

    def _navigate_around_obstacle(self, prev_x: int, prev_y: int, vx: float, vy: float, dt: float, walls: list, obstacles: list):
        """Intenta encontrar una ruta alternativa alrededor del obstáculo"""
        # Direcciones alternativas para probar (perpendiculares y diagonales)
        alternative_dirs = [
            (vy, -vx),   # Perpendicular izquierda
            (-vy, vx),   # Perpendicular derecha
            (vx * 0.7 + vy * 0.7, vy * 0.7 - vx * 0.7),  # Diagonal izquierda
            (vx * 0.7 - vy * 0.7, vy * 0.7 + vx * 0.7),  # Diagonal derecha
            (-vx * 0.5, -vy * 0.5),  # Retroceso parcial
        ]
        
        # Probar cada dirección alternativa
        for alt_vx, alt_vy in alternative_dirs:
            # Normalizar velocidad alternativa
            speed = math.sqrt(vx*vx + vy*vy)
            if speed > 0:
                alt_length = math.sqrt(alt_vx*alt_vx + alt_vy*alt_vy)
                if alt_length > 0:
                    alt_vx = (alt_vx / alt_length) * speed * 0.8  # Reducir velocidad al navegar
                    alt_vy = (alt_vy / alt_length) * speed * 0.8
            
            # Probar movimiento alternativo
            test_x = prev_x + int(alt_vx * dt)
            test_y = prev_y + int(alt_vy * dt)
            
            # Crear rect temporal para probar colisión
            test_rect = pygame.Rect(test_x, test_y, self.rect.width, self.rect.height)
            
            # Verificar si esta posición es válida
            collision_found = False
            
            if walls:
                for wall in walls:
                    if test_rect.colliderect(wall):
                        collision_found = True
                        break
            
            if not collision_found and obstacles:
                for obstacle in obstacles:
                    if test_rect.colliderect(obstacle):
                        collision_found = True
                        break
            
            # Si no hay colisión, usar esta dirección
            if not collision_found:
                self.rect.x = test_x
                self.rect.y = test_y
                return
        
        # Si ninguna dirección funciona, quedarse quieto (pero esto es raro)

    def draw(self, surface: pygame.Surface):
        if self.alive:
            # Si tenemos sprite, usarlo; sino, dibujar rectángulo como fallback
            if self.current_sprite:
                sprite_to_draw = self.current_sprite.copy()
                
                # Aplicar efectos de color
                # Parpadeo blanco cuando está herido (prioridad máxima)
                if self.hurt_timer > 0 and int(self.hurt_timer * 15) % 2 == 0:
                    # Crear superficie blanca del mismo tamaño
                    white_surface = pygame.Surface(sprite_to_draw.get_size())
                    white_surface.fill((255, 255, 255))
                    white_surface.set_alpha(180)  # Semi-transparente para mezclar
                    sprite_to_draw.blit(white_surface, (0, 0), special_flags=pygame.BLEND_ADD)
                # Telegraph: brute en carga se tiñe anaranjado (solo si no está herido)
                elif self.kind == 'brute' and self._charge_time > 0:
                    orange_surface = pygame.Surface(sprite_to_draw.get_size())
                    orange_surface.fill((255, 200, 80))
                    orange_surface.set_alpha(100)
                    sprite_to_draw.blit(orange_surface, (0, 0), special_flags=pygame.BLEND_ADD)
                
                surface.blit(sprite_to_draw, self.rect)
            else:
                # Fallback: dibujar rectángulo si no hay sprite
                color = self.color
                if self.hurt_timer > 0 and int(self.hurt_timer * 15) % 2 == 0:
                    color = (255, 255, 255)
                elif self.kind == 'brute' and self._charge_time > 0:
                    color = (255, 200, 80)
                pygame.draw.rect(surface, color, self.rect)
