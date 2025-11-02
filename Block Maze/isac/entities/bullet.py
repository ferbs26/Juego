import pygame
from isac.settings import WHITE


class Bullet:
    def __init__(self, x: int, y: int, dir_x: int, dir_y: int, speed: int = 480, radius: int = 6, ttl: float = 1.2):
        # Dirección normalizada en entero (-1, 0, 1)
        self.dir_x = dir_x
        self.dir_y = dir_y
        self.speed = speed
        self.radius = radius
        self.pos = pygame.Vector2(x, y)
        self.ttl = ttl  # time to live en segundos
        self.alive = True

    def update(self, dt: float):
        if not self.alive:
            return
        self.pos.x += self.dir_x * self.speed * dt
        self.pos.y += self.dir_y * self.speed * dt
        self.ttl -= dt
        if self.ttl <= 0:
            self.alive = False

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.pos.x - self.radius), int(self.pos.y - self.radius), self.radius * 2, self.radius * 2)

    def draw(self, surface: pygame.Surface):
        if self.alive:
            pygame.draw.circle(surface, WHITE, (int(self.pos.x), int(self.pos.y)), self.radius)
