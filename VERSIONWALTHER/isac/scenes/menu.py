import pygame

from isac.core.scene import Scene
from isac.settings import WIDTH, HEIGHT, WHITE, BLUE


class MenuScene(Scene):
    def __init__(self, game: "Game") -> None:
        super().__init__(game)
        self.font = pygame.font.SysFont(None, 48)
        self.small = pygame.font.SysFont(None, 28)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                # Import local para evitar import circular
                from .play import PlayScene
                self.game.change_scene(PlayScene)
            elif event.key == pygame.K_ESCAPE:
                self.game.running = False

    def update(self, dt: float) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        title = self.font.render("Isac", True, WHITE)
        hint = self.small.render("Enter/Espacio: Jugar  |  Esc: Salir", True, BLUE)
        surface.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 60))
        surface.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT // 2 + 10))
