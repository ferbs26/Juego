import pygame
import math
from isac.settings import (
    BLUE,
    PLAYER_SIZE,
    PLAYER_SPEED,
    PLAYER_MAX_HP,
    PLAYER_INVULN_TIME,
    MAGIC_MAX,
    MAGIC_REGEN,
    MELEE_COOLDOWN,
    MELEE_RANGE,
)


class Player:
    def __init__(self, x: int, y: int, speed: int = PLAYER_SPEED) -> None:
        self.rect = pygame.Rect(0, 0, PLAYER_SIZE, PLAYER_SIZE)
        self.rect.center = (x, y)
        self.speed = speed
        self.speed_multiplier = 1.0  # Para efectos de velocidad
        
        # Efectos visuales temporales
        self.speed_boots_timer = 0.0
        self.speed_boots_glow_timer = 0.0
        self.max_hp = PLAYER_MAX_HP
        self.hp = self.max_hp
        self.invuln = 0.0  # tiempo restante de invulnerabilidad
        # Estado Zelda-like
        self.facing = "down"  # 'up','down','left','right'
        self.magic = float(MAGIC_MAX)
        self.melee_cd = 0.0
        self.melee_active_time = 0.0  # duración breve del golpe visible
        self.shield = False
        self._prev_center = self.rect.center
        
        # Inicializar sistema de sprites
        self.sprites = {}
        self.current_sprite = None
        self.cargar_sprites()

    def update(self, dt: float, walls: list, obstacles: list) -> None:
        # Reducir cooldowns
        if self.melee_cd > 0:
            self.melee_cd -= dt
        if self.melee_active_time > 0:
            self.melee_active_time -= dt
        if self.invuln > 0:
            self.invuln -= dt
            
        # Actualizar efectos temporales de botas
        if self.speed_boots_timer > 0:
            self.speed_boots_timer -= dt
            self.speed_boots_glow_timer += dt * 5.0  # Velocidad del brillo
            if self.speed_boots_timer <= 0:
                # Resetear velocidad cuando se acaba el efecto
                self.speed_multiplier = 1.0

        # Movimiento con teclas
        keys = pygame.key.get_pressed()
        vx = vy = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            vx = -1
            self.facing = "left"
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            vx = 1
            self.facing = "right"
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            vy = -1
            self.facing = "up"
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            vy = 1
            self.facing = "down"

        # Normalizar diagonal
        if vx != 0 and vy != 0:
            vx *= 0.707
            vy *= 0.707

        # Aplicar multiplicador de velocidad
        effective_speed = self.speed * self.speed_multiplier
        vx *= effective_speed
        vy *= effective_speed

        # Movimiento con colisiones
        self._prev_center = self.rect.center
        self.rect.x += int(vx * dt)
        self.rect.y += int(vy * dt)

        # Escudo: mantener consume magia por segundo
        if self.shield and self.magic > 0:
            # consumo se calcula desde escena por precisión, aquí solo clamp
            pass
        else:
            # Regenerar magia si no está el escudo
            self.magic = min(MAGIC_MAX, self.magic + MAGIC_REGEN * dt)
        
        # Actualizar sprite según dirección
        self.actualizar_sprite()

    def cargar_sprites(self):
        """Carga los sprites del jugador."""
        try:
            # Cargar sprites direccionales del cristal
            self.sprites['up'] = pygame.transform.scale(
                pygame.image.load('assets/player/CRISTAL_ARRIBA.png').convert_alpha(),
                (PLAYER_SIZE, PLAYER_SIZE)
            )
            self.sprites['down'] = pygame.transform.scale(
                pygame.image.load('assets/player/CRISTAL_ABAJO.png').convert_alpha(),
                (PLAYER_SIZE, PLAYER_SIZE)
            )
            self.sprites['left'] = pygame.transform.scale(
                pygame.image.load('assets/player/CRISTAL_IZQUIERDA.png').convert_alpha(),
                (PLAYER_SIZE, PLAYER_SIZE)
            )
            self.sprites['right'] = pygame.transform.scale(
                pygame.image.load('assets/player/CRISTAL_DERECHA.png').convert_alpha(),
                (PLAYER_SIZE, PLAYER_SIZE)
            )
            # Sprite especial para cuando está feliz/con efectos
            self.sprites['happy'] = pygame.transform.scale(
                pygame.image.load('assets/player/CRYSTAL_FELIZ.png').convert_alpha(),
                (PLAYER_SIZE, PLAYER_SIZE)
            )
            # Sprite base
            self.sprites['default'] = pygame.transform.scale(
                pygame.image.load('assets/player/CRISTAL.png').convert_alpha(),
                (PLAYER_SIZE, PLAYER_SIZE)
            )
            
            # Establecer sprite inicial
            self.current_sprite = self.sprites['down']
            
        except pygame.error as e:
            print(f"Error al cargar sprites del jugador: {e}")
            self.current_sprite = None
    
    def actualizar_sprite(self):
        """Actualiza el sprite actual según el estado del jugador."""
        if not self.sprites:
            return
            
        # Si tiene botas de velocidad, usar sprite feliz
        if self.speed_boots_timer > 0:
            self.current_sprite = self.sprites.get('happy', self.current_sprite)
        else:
            # Usar sprite según dirección
            self.current_sprite = self.sprites.get(self.facing, self.sprites.get('default', self.current_sprite))

    def apply_speed_boots(self, multiplier: float):
        """Aplica el efecto temporal de las botas de velocidad"""
        self.speed_multiplier = multiplier
        self.speed_boots_timer = 10.0  # 10 segundos de duración
        self.speed_boots_glow_timer = 0.0

    def draw(self, surface: pygame.Surface) -> None:
        # Efecto de fuego/rayos detrás del jugador si tiene botas activas
        if self.speed_boots_timer > 0:
            # Determinar dirección opuesta al movimiento
            keys = pygame.key.get_pressed()
            trail_x = self.rect.centerx
            trail_y = self.rect.centery
            
            # Calcular dirección del rastro basado en el movimiento
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                trail_x += 25  # Rastro a la derecha si va izquierda
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                trail_x -= 25  # Rastro a la izquierda si va derecha
            elif keys[pygame.K_UP] or keys[pygame.K_w]:
                trail_y += 25  # Rastro abajo si va arriba
            elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                trail_y -= 25  # Rastro arriba si va abajo
            else:
                # Si no se mueve, rastro detrás según la dirección que mira
                if self.facing == "left":
                    trail_x += 25
                elif self.facing == "right":
                    trail_x -= 25
                elif self.facing == "up":
                    trail_y += 25
                else:  # down
                    trail_y -= 25
            
            # Crear efecto de fuego/rayos detrás
            flame_count = 8
            for i in range(flame_count):
                # Rayos que salen hacia atrás con variación
                angle_base = math.atan2(trail_y - self.rect.centery, trail_x - self.rect.centerx)
                angle_variation = (i - flame_count/2) * 0.3  # Dispersión
                angle = angle_base + angle_variation
                
                # Longitud variable para efecto de llama
                length = 20 + 15 * math.sin(self.speed_boots_glow_timer * 3 + i)
                
                start_x = self.rect.centerx
                start_y = self.rect.centery
                end_x = start_x + math.cos(angle) * length
                end_y = start_y + math.sin(angle) * length
                
                # Colores de fuego (rojo-naranja-amarillo)
                flame_intensity = int(150 + 100 * math.sin(self.speed_boots_glow_timer * 2 + i))
                if i < 3:
                    color = (255, flame_intensity // 2, 0)  # Rojo-naranja
                elif i < 6:
                    color = (255, flame_intensity, 0)       # Naranja
                else:
                    color = (255, 255, flame_intensity // 3)  # Amarillo
                
                if flame_intensity > 50:
                    pygame.draw.line(surface, color, 
                                   (int(start_x), int(start_y)), 
                                   (int(end_x), int(end_y)), 3)
        
        # Dibujar jugador con sprite o fallback
        if self.current_sprite:
            sprite_to_draw = self.current_sprite.copy()
            
            # Aplicar efecto de parpadeo si está en invulnerabilidad
            if self.invuln > 0 and int(self.invuln * 10) % 2 == 0:
                # Crear superficie blanca semi-transparente para efecto de daño
                white_surface = pygame.Surface(sprite_to_draw.get_size())
                white_surface.fill((255, 255, 255))
                white_surface.set_alpha(150)
                sprite_to_draw.blit(white_surface, (0, 0), special_flags=pygame.BLEND_ADD)
            
            surface.blit(sprite_to_draw, self.rect)
        else:
            # Fallback: dibujar rectángulo azul si no hay sprite
            color = BLUE
            if self.invuln > 0 and int(self.invuln * 10) % 2 == 0:
                color = (255, 255, 255)  # Blanco cuando está invulnerable
            pygame.draw.rect(surface, color, self.rect)

    def take_damage(self, amount: int = 1) -> None:
        if self.invuln > 0:
            return
        self.hp = max(0, self.hp - amount)
        self.invuln = PLAYER_INVULN_TIME

    # Ataque melee: activa una pequeña ventana donde existe una hitbox delante del jugador
    def start_melee(self) -> bool:
        if self.melee_cd > 0:
            return False
        self.melee_cd = MELEE_COOLDOWN
        self.melee_active_time = 0.12
        return True

    def melee_hitbox(self) -> pygame.Rect | None:
        if self.melee_active_time <= 0:
            return None
        r = self.rect
        if self.facing == "up":
            return pygame.Rect(r.centerx - 6, r.top - MELEE_RANGE, 12, MELEE_RANGE)
        if self.facing == "down":
            return pygame.Rect(r.centerx - 6, r.bottom, 12, MELEE_RANGE)
        if self.facing == "left":
            return pygame.Rect(r.left - MELEE_RANGE, r.centery - 6, MELEE_RANGE, 12)
        if self.facing == "right":
            return pygame.Rect(r.right, r.centery - 6, MELEE_RANGE, 12)
        return None

    def revert_position(self) -> None:
        self.rect.center = self._prev_center
