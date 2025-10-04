import pygame

from isac.core.scene import Scene
from isac.settings import WIDTH, HEIGHT, WHITE, RED, BLUE


class GameOverScene(Scene):
    def __init__(self, game: "Game") -> None:
        super().__init__(game)
        self.title_font = pygame.font.SysFont(None, 72)
        self.small_font = pygame.font.SysFont(None, 28)
        self.blink_time = 0.0

        # Fade state
        self._fade_alpha: float = 0.0
        self._fade_dir: int = 0
        self._fade_speed: float = 0.0
        self._fade_callback = None
        # Start with fade-in
        self._start_fade(out=False, duration=0.25)

    def update(self, dt: float) -> None:
        self.blink_time += dt
        # Update fade
        if self._fade_dir != 0:
            step = self._fade_speed * dt * (1 if self._fade_dir > 0 else -1)
            self._fade_alpha = max(0.0, min(255.0, self._fade_alpha + step))
            if self._fade_dir < 0 and self._fade_alpha <= 0:
                self._fade_dir = 0
                cb = self._fade_callback
                self._fade_callback = None
                if cb:
                    cb()
                self._start_fade(out=False, duration=0.2)
            elif self._fade_dir > 0 and self._fade_alpha >= 255:
                self._fade_dir = 0
                self._fade_alpha = 0.0

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                from .menu import MenuScene
                if self._fade_dir == 0:
                    self._start_fade(out=True, duration=0.2, on_complete=lambda: self.game.change_scene(MenuScene))
            elif event.key == pygame.K_r:
                from .play import PlayScene
                if self._fade_dir == 0:
                    self._start_fade(out=True, duration=0.2, on_complete=lambda: self.game.change_scene(PlayScene))
            elif event.key == pygame.K_ESCAPE:
                # Fade-out antes de salir
                if self._fade_dir == 0:
                    self._start_fade(out=True, duration=0.2, on_complete=self._quit)

    def _quit(self) -> None:
        self.game.running = False

    def draw(self, surface: pygame.Surface) -> None:
        title = self.title_font.render("GAME OVER", True, RED)
        surface.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 80))

        # Mensajes
        hint1 = self.small_font.render("Enter/Espacio: Menú", True, WHITE)
        hint2 = self.small_font.render("R: Reiniciar  |  Esc: Salir", True, BLUE)
        surface.blit(hint1, (WIDTH // 2 - hint1.get_width() // 2, HEIGHT // 2))
        # Parpadeo suave del segundo hint
        if int(self.blink_time * 2) % 2 == 0:
            surface.blit(hint2, (WIDTH // 2 - hint2.get_width() // 2, HEIGHT // 2 + 36))

        # Fade overlay
        if self._fade_dir != 0 or self._fade_alpha > 0:
            alpha = int(self._fade_alpha)
            if alpha > 0:
                overlay = pygame.Surface((WIDTH, HEIGHT))
                overlay.set_alpha(alpha)
                overlay.fill((0, 0, 0))
                surface.blit(overlay, (0, 0))

    def _start_fade(self, out: bool, duration: float, on_complete=None) -> None:
        self._fade_dir = -1 if out else 1
        self._fade_speed = 255.0 / max(0.01, duration)
        if not out:
            self._fade_alpha = 255.0
        else:
            self._fade_alpha = 0.0
        self._fade_callback = on_complete
