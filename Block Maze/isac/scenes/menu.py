import pygame

from isac.core.scene import Scene
from isac.settings import WIDTH, HEIGHT, WHITE, BLUE


class MenuScene(Scene):
    def __init__(self, game: "Game") -> None:
        super().__init__(game)
        self.font = pygame.font.SysFont(None, 48)
        self.small = pygame.font.SysFont(None, 28)
        self.title_font = pygame.font.SysFont(None, 64)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                # Go to character selection screen
                from .character_select import CharacterSelectScene
                self.game.change_scene(CharacterSelectScene)
            elif event.key == pygame.K_ESCAPE:
                self.game.running = False

    def update(self, dt: float) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        title = self.title_font.render("Block Maze", True, WHITE)
        hint = self.small.render("Enter/Espacio: Jugar  |  Esc: Salir", True, BLUE)
        subtitle = self.small.render("Un juego de aventuras y mazmorras", True, BLUE)
        
        surface.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 3))
        surface.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, HEIGHT // 2 - 30))
        surface.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT * 2 // 3))
