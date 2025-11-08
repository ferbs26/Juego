import pygame
import math
from isac.settings import (
    BLUE,
    PLAYER_SIZE,
    PLAYER_MAX_HP,
    PLAYER_SPEED,
    MAGIC_MAX,
    PLAYER_INVULN_TIME,
    MAGIC_REGEN,
    MELEE_COOLDOWN,
    MELEE_RANGE,
)
from isac.characters import get_character, load_character_sprites


class Player:
    def __init__(self, x: int, y: int, speed: int = PLAYER_SPEED, character_type: str = "crystal") -> None:
        self.rect = pygame.Rect(0, 0, PLAYER_SIZE, PLAYER_SIZE)
        self.rect.center = (x, y)
        self.speed = speed
        
        # Cargar datos del personaje
        self.character_data = get_character(character_type)
        self.max_hp = self.character_data.max_hp
        self.hp = self.max_hp
        self.speed_multiplier = self.character_data.speed_multiplier
        self.damage_multiplier = getattr(self.character_data, 'damage_multiplier', 1.0)
        self.character_type = character_type  # Almacenar el tipo de personaje
        
        # Efectos visuales temporales
        self.speed_boots_timer = 0.0
        self.speed_boots_glow_timer = 0.0
        self.big_shot_timer = 0.0
        self.big_shot_active = False
        self.invuln = 0.0  # tiempo restante de invulnerabilidad
        
        # Estado del jugador
        self.facing = "down"  # 'up','down','left','right'
        self.magic = float(MAGIC_MAX)
        self.melee_cd = 0.0
        self.melee_active_time = 0.0  # duración breve del golpe visible
        self.shield = False
        self._prev_center = self.rect.center
        
        # Inicializar sistema de sprites
        self.sprites = load_character_sprites(self.character_data, (PLAYER_SIZE, PLAYER_SIZE))
        self.current_sprite = self.sprites.get('down', [None])[0] if self.sprites.get('down') else None
        
        # Disparo infinito (desactivado por defecto)
        self.infinite_shots = False
        
        # Control de velocidad de disparo
        self.shoot_cooldown = 0
        self.shoot_delay = 0.2  # segundos entre disparos (valor base)
        self.last_shot_time = 0
        
        # Control de disparo continuo
        self.wants_to_shoot = False
        
        # Aplicar efectos visuales específicos del personaje
        if character_type == 'glass':
            self._apply_glass_effects()
    
    def set_shooting(self, shooting: bool) -> None:
        """Establece si el jugador quiere disparar.
        
        Args:
            shooting: True si el jugador quiere disparar, False en caso contrario
        """
        self.wants_to_shoot = shooting
        
    def _apply_glass_effects(self):
        """Aplica efectos visuales específicos para el personaje Glass."""
        # Hacer a Glass semi-transparente
        for direction in self.sprites:
            if direction in ['up', 'down', 'left', 'right']:
                for i in range(len(self.sprites[direction])):
                    if isinstance(self.sprites[direction][i], pygame.Surface):
                        self.sprites[direction][i] = self.sprites[direction][i].copy()
                        self.sprites[direction][i].set_alpha(180)  # Semi-transparente
            elif self.sprites[direction] is not None:
                self.sprites[direction] = self.sprites[direction].copy()
                self.sprites[direction].set_alpha(180)

    def update(self, dt: float, walls: list, obstacles: list) -> None:
        # Reducir cooldowns
        if self.melee_cd > 0:
            self.melee_cd -= dt
        if self.melee_active_time > 0:
            self.melee_active_time -= dt
        if self.invuln > 0:
            self.invuln -= dt
            
        # Actualizar temporizador de BIG SHOT
        if self.big_shot_timer > 0:
            self.big_shot_timer -= dt
            if self.big_shot_timer <= 0:
                self.big_shot_active = False
                self.SHOOT_COOLDOWN_TIME = 0.3  # Restaurar cooldown normal
                print("¡El efecto BIG SHOT ha terminado!")
            
        # Reducir cooldown de disparo
        if self.shoot_cooldown > 0:
            cooldown_multiplier = 3.0 if self.big_shot_active else 1.0
            self.shoot_cooldown = max(0, self.shoot_cooldown - (dt * cooldown_multiplier))
            
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
        """Carga los sprites del personaje actual."""
        # Los sprites ya se cargaron en el __init__
        pass
    
    def actualizar_sprite(self):
        """Actualiza el sprite actual según el estado del jugador."""
        if not self.sprites:
            return
            
        # Obtener el sprite apropiado según el estado
        sprite = None
        
        # 1. Verificar si debe mostrarse el sprite 'happy' (efecto de botas)
        if self.speed_boots_timer > 0 and 'happy' in self.sprites and self.sprites['happy'] is not None:
            sprite = self.sprites['happy']
        
        # 2. Si no hay sprite 'happy' o no está activo, usar el de la dirección actual
        if not sprite:
            # Para el personaje Crystal, que usa sprites de dirección
            if self.facing in self.sprites and self.sprites[self.facing]:
                sprite = self.sprites[self.facing][0]  # Tomar el primer frame de la animación
            
            # Si no hay sprite para la dirección actual, usar el default
            if not sprite and 'default' in self.sprites and self.sprites['default'] is not None:
                sprite = self.sprites['default']
        
        # 3. Si aún no hay sprite, intentar con cualquier sprite disponible
        if not sprite:
            for key in ['down', 'right', 'left', 'up']:  # Orden de preferencia
                if key in self.sprites and self.sprites[key] and isinstance(self.sprites[key], list) and self.sprites[key]:
                    sprite = self.sprites[key][0]
                    break
        
        # 4. Si todo falla, crear un sprite de emergencia rojo
        if not sprite:
            print("Advertencia: No se pudo cargar ningún sprite, usando sprite de emergencia")
            surf = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE), pygame.SRCALPHA)
            surf.fill((255, 0, 0, 128))  # Rojo semitransparente
            sprite = surf
        
        # Actualizar el sprite actual
        self.current_sprite = sprite

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
            pygame.draw.rect(surface, BLUE, self.rect)

    def activate_big_shot(self, duration: float = 7.0) -> None:
        """Activa el efecto BIG SHOT por la duración especificada (7 segundos por defecto)"""
        print(f"[DEBUG] Activando BIG SHOT por {duration} segundos")
        self.big_shot_active = True
        self.big_shot_timer = max(self.big_shot_timer, duration)  # Extender si ya está activo
        print(f"¡BIG SHOT activado por {duration} segundos!")
        # Hacer que el cooldown de disparo sea 3 veces más lento (aumentar el tiempo entre disparos)
        self.SHOOT_COOLDOWN_TIME = 0.9  # 3 veces más lento que el normal (0.3 * 3 = 0.9)
        print(f"[DEBUG] big_shot_active = {self.big_shot_active}, big_shot_timer = {self.big_shot_timer}")
        print(f"[DEBUG] Cooldown de disparo ajustado a {self.SHOOT_COOLDOWN_TIME} segundos (3x más lento)")
        
    def take_damage(self, amount: int) -> None:
        if self.invuln <= 0 and not self.shield:
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
        
    def set_infinite_shots(self, enabled: bool) -> None:
        """Activa o desactiva el disparo infinito."""
        self.infinite_shots = enabled
        
    def can_shoot(self) -> bool:
        """Verifica si el jugador puede disparar (si no está en cooldown)."""
        return self.shoot_cooldown <= 0 and self.wants_to_shoot
        
    def start_shoot_cooldown(self) -> None:
        """Inicia el cooldown de disparo."""
        self.shoot_cooldown = self.shoot_delay
        
    def set_shooting(self, shooting: bool) -> None:
        """Establece si el jugador está intentando disparar."""
        self.wants_to_shoot = shooting
